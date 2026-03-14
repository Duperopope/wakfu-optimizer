import pathlib

content = r"""// === WAKFU DEV ASSISTANT v5.0 - CLEAN REBUILD ===
// 2026-03-15 | Selecteurs Genspark verifies | Pipeline LLM complet
// Conteneur: .conversation-content
// Messages: .conversation-statement.assistant / .user
// Send: .enter-icon | Textarea: textarea[name="query"]

const SERVER = 'http://127.0.0.1:8091';
const VERSION = '5.0';

let initialScanDone = false;
let scanTimer = null;
let lastProcessedAssistantIndex = -1;
let state = { connected: false, autoMode: false, exchanges: 0 };

// === LOGGING ===
function logExt(msg) {
  console.log('[WAKFU] ' + msg);
  try {
    fetch(SERVER + '/ext-log', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: msg, type: 'ext' })
    }).catch(function(){});
  } catch(e) {}
  var d = document.getElementById('wakfu-logs');
  if (d) {
    var e = document.createElement('div');
    e.style.cssText = 'font-size:11px;border-bottom:1px solid #333;padding:2px 0';
    e.textContent = new Date().toLocaleTimeString() + ' - ' + msg;
    d.insertBefore(e, d.firstChild);
    if (d.children.length > 50) d.removeChild(d.lastChild);
  }
}

// === SERVER COMMUNICATION ===
async function serverFetch(path, opts) {
  try {
    var options = Object.assign({ method: 'GET', headers: { 'Content-Type': 'application/json' } }, opts || {});
    var r = await fetch(SERVER + path, options);
    return await r.json();
  } catch (e) {
    logExt('Fetch err: ' + path + ' ' + e.message);
    return null;
  }
}

async function checkHealth() {
  var r = await serverFetch('/health');
  state.connected = !!(r && r.status === 'ok');
  updatePanel();
}

// === GENSPARK DOM HELPERS ===
function getTextarea() {
  return document.querySelector('textarea[name="query"]') || document.querySelector('textarea');
}

function clickSendButton() {
  var btn = document.querySelector('.enter-icon');
  if (btn) { btn.click(); return true; }
  return false;
}

function isGenerating() {
  // Genspark montre un stop-icon pendant la generation
  var stop = document.querySelector('.stop-icon, .loading-icon');
  if (stop) return true;
  var ta = getTextarea();
  if (ta && ta.disabled) return true;
  return false;
}

// === DERNIER MESSAGE ASSISTANT SEULEMENT ===
function getLastAssistantMessage() {
  var msgs = document.querySelectorAll('.conversation-statement.assistant');
  if (msgs.length === 0) return null;
  return msgs[msgs.length - 1];
}

function getNewCodeBlocksFromLastAssistant() {
  var lastMsg = getLastAssistantMessage();
  if (!lastMsg) return [];
  var blocks = lastMsg.querySelectorAll('pre code');
  var results = [];
  for (var i = 0; i < blocks.length; i++) {
    var el = blocks[i];
    if (el.dataset.wakfuProcessed === 'true') continue;
    var code = el.textContent || '';
    if (code.trim().length < 5) continue;
    var type = detectType(el, code);
    results.push({ element: el, code: code, type: type, index: i });
  }
  return results;
}

function detectType(el, code) {
  var cl = ((el.className || '') + ' ' + ((el.parentElement && el.parentElement.className) || '')).toLowerCase();
  if (cl.includes('powershell') || cl.includes('ps1')) return 'powershell';
  if (cl.includes('python') || cl.includes('py')) return 'python';
  if (cl.includes('javascript') || cl.includes('js')) return 'javascript';
  if (cl.includes('typescript') || cl.includes('tsx') || cl.includes('ts')) return 'typescript';
  if (cl.includes('html')) return 'html';
  if (cl.includes('css')) return 'css';
  if (cl.includes('json')) return 'json';
  if (cl.includes('bash') || cl.includes('shell')) return 'powershell';
  // Detection par contenu
  if (code.trimStart().startsWith('$') || code.includes('Write-Host') || code.includes('Invoke-') || code.includes('Get-Content') || code.includes('Set-Content') || code.includes('| ConvertTo-Json')) return 'powershell';
  if (code.trimStart().startsWith('import pathlib') || code.trimStart().startsWith('import ') || code.includes('def ') || code.includes('print(')) return 'python';
  return 'unknown';
}

// === SENTINEL CLASSIFICATION ===
async function classifyCode(code) {
  try {
    var r = await serverFetch('/classify', { method: 'POST', body: JSON.stringify({ code: code }) });
    if (r && r.classification) return r.classification;
    return { verdict: 'UNKNOWN', reason: 'no response' };
  } catch (e) {
    return { verdict: 'UNKNOWN', reason: e.message };
  }
}

// === AUTO INJECT RESULT ===
function autoInjectResult(text) {
  var ta = getTextarea();
  if (!ta) { logExt('Textarea introuvable'); return; }
  var output = text.output || '';
  var duration = text.duration || '?';
  // Construire le message
  var msg = 'Resultat de l\'execution (' + duration + '):\n```\n' + output.slice(0, 3000) + '\n```\nContinue avec la prochaine etape.';
  // Injecter dans le textarea
  var nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set;
  nativeSetter.call(ta, msg);
  ta.dispatchEvent(new Event('input', { bubbles: true }));
  // Cliquer send apres un court delai
  setTimeout(function() {
    if (clickSendButton()) {
      state.exchanges++;
      updatePanel();
      logExt('Auto-send OK (echange #' + state.exchanges + ')');
    } else {
      logExt('Auto-send ECHEC: bouton send introuvable');
    }
  }, 600);
}

// === EXEC BUTTON ===
function addExecButtons(block) {
  var element = block.element;
  var code = block.code;
  var type = block.type;
  var index = block.index;

  if (element.dataset.wakfuProcessed === 'true') return;
  element.dataset.wakfuProcessed = 'true';

  var wrapper = document.createElement('div');
  wrapper.className = 'wakfu-btn-wrapper';

  var execBtn = null;

  if (type === 'powershell' || type === 'python') {
    execBtn = document.createElement('button');
    execBtn.className = 'wakfu-exec-btn';
    execBtn.textContent = '\u25B6 Executer';
    execBtn.onclick = async function() {
      execBtn.textContent = '\u23F3 En cours...';
      execBtn.disabled = true;
      try {
        var cmd = code;
        if (type === 'python' && !code.trimStart().startsWith('python')) {
          // Ecrire dans un fichier temp et executer
          cmd = 'python -c "' + code.replace(/"/g, '\\"').replace(/\n/g, '\\n') + '"';
        }
        var res = await serverFetch('/execute', {
          method: 'POST',
          body: JSON.stringify({ command: cmd, timeout: 120 })
        });
        execBtn.disabled = false;
        if (res && res.success) {
          execBtn.textContent = '\u2705 OK';
          execBtn.style.background = '#16a34a';
          autoInjectResult({
            output: res.stdout || res.output || 'OK',
            duration: (res.duration || '?') + 's'
          });
        } else {
          execBtn.textContent = '\u274C Erreur';
          execBtn.style.background = '#dc2626';
          autoInjectResult({
            output: 'Erreur: ' + (res ? (res.error || res.stderr || JSON.stringify(res)) : 'No response'),
            duration: (res ? res.duration || '0' : '0') + 's'
          });
        }
      } catch (e) {
        execBtn.disabled = false;
        execBtn.textContent = '\u274C Erreur';
        execBtn.style.background = '#dc2626';
      }
      setTimeout(function() {
        if (execBtn) {
          execBtn.textContent = '\u25B6 Executer';
          execBtn.style.background = '';
          execBtn.disabled = false;
        }
      }, 5000);
    };
    wrapper.appendChild(execBtn);

    // SENTINEL classification si scan initial termine
    if (initialScanDone) {
      (function(btn, el, c, w) {
        setTimeout(async function() {
          logExt('SENTINEL: classification bloc #' + index);
          var result = await classifyCode(c);
          logExt('SENTINEL: ' + result.verdict + ' - ' + (result.reason || '').substring(0, 80));
          var lbl = w.querySelector('.wakfu-type-label');
          if (result.verdict === 'EXEC_DANGER') {
            btn.style.background = '#dc3545';
            btn.textContent = '\u26D4 BLOQUE';
            btn.disabled = true;
            if (lbl) { lbl.textContent = 'DANGER'; lbl.style.background = '#dc3545'; lbl.style.color = '#fff'; }
          } else if (result.verdict === 'NO_EXEC') {
            btn.style.background = '#6c757d';
            btn.textContent = 'Exemple';
            btn.disabled = true;
            if (lbl) { lbl.textContent = 'EXEMPLE'; lbl.style.background = '#6c757d'; lbl.style.color = '#fff'; }
          } else if (result.verdict === 'EXEC_SAFE' && state.autoMode) {
            if (lbl) { lbl.textContent = 'AUTO'; lbl.style.background = '#28a745'; lbl.style.color = '#fff'; }
            logExt('AUTO-EXEC: LLM a valide, lancement...');
            setTimeout(function() { if (btn && !btn.disabled) btn.click(); }, 1500);
          } else if (result.verdict === 'EXEC_SAFE') {
            if (lbl) { lbl.textContent = 'SAFE'; lbl.style.background = '#28a745'; lbl.style.color = '#fff'; }
          }
        }, 1500);
      })(execBtn, element, code, wrapper);
    }
  }

  // Bouton copier
  var copyBtn = document.createElement('button');
  copyBtn.className = 'wakfu-copy-btn';
  copyBtn.textContent = '\uD83D\uDCCB Copier';
  copyBtn.onclick = function() {
    navigator.clipboard.writeText(code);
    copyBtn.textContent = '\u2705 Copie!';
    setTimeout(function() { copyBtn.textContent = '\uD83D\uDCCB Copier'; }, 2000);
  };
  wrapper.appendChild(copyBtn);

  // Label type
  var typeLabel = document.createElement('span');
  typeLabel.className = 'wakfu-type-label';
  typeLabel.textContent = type.toUpperCase();
  typeLabel.style.cssText = 'font-size:10px;padding:2px 6px;border-radius:3px;background:#374151;color:#9ca3af;align-self:center';
  wrapper.appendChild(typeLabel);

  // Inserer apres le bloc code
  var pre = element.closest('pre') || element.parentElement;
  if (pre && pre.parentElement) {
    pre.parentElement.insertBefore(wrapper, pre.nextSibling);
  }
}

// === SCAN - SEULEMENT DERNIER MESSAGE ASSISTANT ===
function scanBlocks() {
  var blocks = getNewCodeBlocksFromLastAssistant();
  var n = 0;
  for (var i = 0; i < blocks.length; i++) {
    addExecButtons(blocks[i]);
    n++;
  }
  if (n > 0) logExt('Scan: ' + n + ' nouveaux blocs (dernier assistant)');
}

function debouncedScan() {
  if (isGenerating()) return;
  if (scanTimer) clearTimeout(scanTimer);
  scanTimer = setTimeout(scanBlocks, 2000);
}

// === PANEL UI ===
function updatePanel() {
  var s = document.getElementById('wakfu-status');
  var x = document.getElementById('wakfu-exchanges');
  var a = document.getElementById('wakfu-auto-toggle');
  if (s) {
    s.textContent = state.connected ? 'En ligne' : 'Hors ligne';
    s.style.color = state.connected ? '#4ade80' : '#f87171';
  }
  if (x) x.textContent = 'Echanges: ' + state.exchanges;
  if (a) {
    a.textContent = state.autoMode ? 'AUTO: ON' : 'AUTO: OFF';
    a.style.background = state.autoMode ? '#16a34a' : '#dc2626';
  }
}

function createPanel() {
  if (document.getElementById('wakfu-panel')) return;
  var p = document.createElement('div');
  p.id = 'wakfu-panel';
  p.innerHTML = '<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px">'
    + '<strong style="color:#60a5fa">Wakfu Dev v' + VERSION + '</strong>'
    + '<span id="wakfu-status" style="font-size:11px">...</span></div>'
    + '<div style="display:flex;gap:6px;margin-bottom:6px;flex-wrap:wrap">'
    + '<button id="wakfu-auto-toggle" style="padding:3px 8px;border:none;border-radius:4px;color:#fff;cursor:pointer;font-size:11px;background:#dc2626">AUTO: OFF</button>'
    + '<span id="wakfu-exchanges" style="font-size:11px;color:#9ca3af;align-self:center">Echanges: 0</span></div>'
    + '<div id="wakfu-logs" style="max-height:150px;overflow-y:auto;font-family:monospace;font-size:10px;color:#d1d5db"></div>';
  document.body.appendChild(p);
  document.getElementById('wakfu-auto-toggle').addEventListener('click', function() {
    state.autoMode = !state.autoMode;
    updatePanel();
    logExt('Mode auto: ' + (state.autoMode ? 'ON' : 'OFF'));
  });
}

function addStyles() {
  var s = document.createElement('style');
  s.textContent = '#wakfu-panel{position:fixed;top:10px;right:10px;width:320px;max-height:90vh;overflow-y:auto;background:#1e1e2e;border:1px solid #374151;border-radius:8px;padding:12px;z-index:99999;font-family:system-ui,sans-serif;box-shadow:0 4px 12px rgba(0,0,0,.5);color:#e5e7eb}'
    + '.wakfu-exec-btn{background:#2563eb;color:#fff;border:none;padding:4px 10px;border-radius:4px;cursor:pointer;font-size:12px}'
    + '.wakfu-exec-btn:hover{background:#1d4ed8}'
    + '.wakfu-exec-btn:disabled{opacity:0.6;cursor:not-allowed}'
    + '.wakfu-copy-btn{background:#374151;color:#d1d5db;border:none;padding:4px 10px;border-radius:4px;cursor:pointer;font-size:12px}'
    + '.wakfu-copy-btn:hover{background:#4b5563}'
    + '.wakfu-btn-wrapper{display:flex;gap:6px;margin:6px 0 2px 0;align-items:center}';
  document.head.appendChild(s);
}

// === CHAT MEMORY OBSERVER ===
var lastChatCount = 0;

function captureChat() {
  var msgs = document.querySelectorAll('.conversation-statement');
  if (msgs.length <= lastChatCount) return;
  var newMsgs = Array.prototype.slice.call(msgs, lastChatCount);
  for (var i = 0; i < newMsgs.length; i++) {
    var m = newMsgs[i];
    var text = (m.textContent || '').trim().substring(0, 500);
    if (text.length < 10) continue;
    var isUser = m.classList.contains('user');
    try {
      fetch(SERVER + '/ext-log', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: (isUser ? '[USER] ' : '[ASSISTANT] ') + text,
          type: 'chat'
        })
      }).catch(function(){});
    } catch(e) {}
  }
  lastChatCount = msgs.length;
}

// === INIT ===
var observer = new MutationObserver(function() { debouncedScan(); });

function init() {
  logExt('Wakfu Dev Assistant v' + VERSION + ' initialise');
  addStyles();
  createPanel();
  observer.observe(document.body, { childList: true, subtree: true });
  logExt('Observer DOM actif (debounce 2000ms)');
  checkHealth();
  setInterval(checkHealth, 15000);
  setInterval(captureChat, 5000);
  // Scan initial: marquer tous les blocs existants comme deja traites
  var existingBlocks = document.querySelectorAll('pre code');
  for (var i = 0; i < existingBlocks.length; i++) {
    existingBlocks[i].dataset.wakfuProcessed = 'true';
  }
  logExt('Scan initial: ' + existingBlocks.length + ' blocs existants marques');
  setTimeout(function() {
    initialScanDone = true;
    logExt('SENTINEL actif pour nouveaux blocs');
  }, 4000);
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}
"""

out = pathlib.Path(r'H:\Code\Ankama Dev\wakfu-dev-extension\content.js')
out.write_text(content, 'utf-8')
lines = content.strip().split('\n')
print('content.js v5.0 ecrit')
print('Lignes:', len(lines))
print('Taille:', out.stat().st_size, 'octets')
