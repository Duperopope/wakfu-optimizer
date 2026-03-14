// ============================================================
// content.js v5.0 — Wakfu Dev Assistant
// Phase 1 : DIAGNOSTIC DOM + Architecture modulaire
// Genere le 2026-03-15 par Claude Opus
// ============================================================

(function() {
  "use strict";

  // ── CONFIG ─────────────────────────────────────────────────
  const CONFIG = {
    SERVER_URL: "http://127.0.0.1:8091",
    VERSION: "5.0.0-diag",
    DEBOUNCE_MS: 2000,
    LOG_PREFIX: "[WDA5]",
    RETRY_MAX: 3,
    RETRY_DELAY_MS: 1000
  };

  // ── LOGGER ─────────────────────────────────────────────────
  // Envoie les logs à la console ET au dev_server /ext-log
  const Logger = {
    _queue: [],
    _sending: false,

    _format(level, msg) {
      const ts = new Date().toISOString().substring(11, 19);
      return `${CONFIG.LOG_PREFIX} [${ts}] [${level}] ${msg}`;
    },

    info(msg)  { const m = this._format("INFO", msg);  console.log(m);  this._send(m); },
    warn(msg)  { const m = this._format("WARN", msg);  console.warn(m); this._send(m); },
    error(msg) { const m = this._format("ERROR", msg); console.error(m); this._send(m); },
    debug(msg) { const m = this._format("DEBUG", msg); console.debug(m); this._send(m); },

    async _send(message) {
      this._queue.push(message);
      if (this._sending) return;
      this._sending = true;
      while (this._queue.length > 0) {
        const batch = this._queue.splice(0, 10);
        for (const msg of batch) {
          try {
            await fetch(`${CONFIG.SERVER_URL}/ext-log`, {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ message: msg }),
              signal: AbortSignal.timeout(3000)
            });
          } catch (e) {
            // Silencieux — le serveur n'est peut-etre pas lance
          }
        }
      }
      this._sending = false;
    }
  };

  // ── SERVER BRIDGE ──────────────────────────────────────────
  // Communication avec le dev_server local
  const Server = {
    async ping() {
      try {
        const resp = await fetch(`${CONFIG.SERVER_URL}/health`, {
          signal: AbortSignal.timeout(3000)
        });
        const data = await resp.json();
        return data.status === "ok";
      } catch (e) {
        return false;
      }
    },

    async send(route, payload) {
      for (let attempt = 1; attempt <= CONFIG.RETRY_MAX; attempt++) {
        try {
          const resp = await fetch(`${CONFIG.SERVER_URL}${route}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
            signal: AbortSignal.timeout(10000)
          });
          return await resp.json();
        } catch (e) {
          if (attempt < CONFIG.RETRY_MAX) {
            await new Promise(r => setTimeout(r, CONFIG.RETRY_DELAY_MS * attempt));
          } else {
            Logger.error(`Server.send ${route} echec apres ${CONFIG.RETRY_MAX} tentatives: ${e.message}`);
            return null;
          }
        }
      }
    }
  };

  // ── DOM SCANNER ────────────────────────────────────────────
  // Scanne le DOM Genspark et identifie les éléments clés par heuristiques
  const DOMScanner = {
    results: null,

    scan() {
      Logger.info("Debut scan DOM Genspark...");
      const r = {
        timestamp: new Date().toISOString(),
        url: window.location.href,
        rootApp: this._findRootApp(),
        chatContainers: this._findChatContainers(),
        messageElements: this._findMessages(),
        codeBlocks: this._findCodeBlocks(),
        inputArea: this._findInputArea(),
        sendButton: this._findSendButton(),
        copyButtons: this._findCopyButtons(),
        allRoles: this._findAllRoles(),
        interestingSelectors: this._probeSelectors()
      };
      this.results = r;
      Logger.info(`Scan termine: ${r.chatContainers.length} conteneurs chat, ${r.messageElements.length} messages, ${r.codeBlocks.length} blocs code, input=${!!r.inputArea}, send=${r.sendButton.length} boutons`);
      return r;
    },

    _findRootApp() {
      const candidates = ["#app", "#root", "#__next", "[data-app]", "#main-app", ".app-container", "#__nuxt"];
      for (const sel of candidates) {
        const el = document.querySelector(sel);
        if (el) {
          return {
            selector: sel,
            tag: el.tagName,
            className: (el.className || "").substring(0, 200),
            id: el.id || null,
            childCount: el.children.length
          };
        }
      }
      // Fallback: premier div direct dans body avec beaucoup d'enfants
      const bodyDivs = Array.from(document.body.children).filter(c => c.tagName === "DIV");
      if (bodyDivs.length > 0) {
        const best = bodyDivs.sort((a, b) => b.children.length - a.children.length)[0];
        return {
          selector: `body > div (fallback, ${bodyDivs.length} divs)`,
          tag: best.tagName,
          className: (best.className || "").substring(0, 200),
          id: best.id || null,
          childCount: best.children.length
        };
      }
      return null;
    },

    _findChatContainers() {
      const results = [];
      document.querySelectorAll("div, main, section").forEach(el => {
        const style = window.getComputedStyle(el);
        const hasScroll = style.overflowY === "auto" || style.overflowY === "scroll";
        const isTall = el.offsetHeight > 200;
        const hasChildren = el.children.length > 2;
        const scrollsDown = el.scrollHeight > el.offsetHeight + 50;
        if (hasScroll && isTall && hasChildren && scrollsDown) {
          results.push({
            tag: el.tagName,
            className: (el.className || "").substring(0, 200),
            id: el.id || null,
            childCount: el.children.length,
            scrollHeight: el.scrollHeight,
            offsetHeight: el.offsetHeight,
            role: el.getAttribute("role"),
            firstChildClass: el.firstElementChild ? (el.firstElementChild.className || "").substring(0, 100) : null,
            dataAttrs: Array.from(el.attributes).filter(a => a.name.startsWith("data-")).map(a => `${a.name}=${a.value}`).slice(0, 10),
            childrenPreview: Array.from(el.children).slice(0, 5).map(c => ({
              tag: c.tagName,
              className: (c.className || "").substring(0, 100),
              textLen: (c.textContent || "").length,
              hasCode: c.querySelector("pre, code") !== null
            }))
          });
        }
      });
      return results;
    },

    _findMessages() {
      const results = [];
      // Stratégie 1: chercher par class/role connus
      const selectors = [
        '[class*="message"]', '[class*="chat-message"]', '[class*="msg-"]',
        '[class*="bubble"]', '[class*="turn"]', '[class*="response"]',
        '[class*="answer"]', '[class*="assistant"]', '[class*="user-msg"]',
        '[role="article"]', '[role="log"]', '[role="listitem"]',
        '[data-message-id]', '[data-role]', '[data-type="message"]'
      ];
      const seen = new Set();
      for (const sel of selectors) {
        document.querySelectorAll(sel).forEach(el => {
          const key = el.tagName + el.className + el.textContent.substring(0, 30);
          if (!seen.has(key) && results.length < 30) {
            seen.add(key);
            results.push({
              matchedSelector: sel,
              tag: el.tagName,
              className: (el.className || "").substring(0, 200),
              id: el.id || null,
              role: el.getAttribute("role"),
              textPreview: (el.textContent || "").substring(0, 100).trim(),
              childCount: el.children.length,
              hasCode: el.querySelector("pre, code") !== null,
              dataAttrs: Array.from(el.attributes).filter(a => a.name.startsWith("data-")).map(a => `${a.name}=${a.value}`).slice(0, 10),
              depth: this._getDepth(el)
            });
          }
        });
      }
      return results;
    },

    _findCodeBlocks() {
      const results = [];
      document.querySelectorAll("pre").forEach((el, i) => {
        if (i >= 15) return;
        const codeChild = el.querySelector("code");
        const text = (codeChild || el).textContent || "";
        // Detecter le langage
        const langClass = codeChild ? Array.from(codeChild.classList).find(c => c.startsWith("language-") || c.startsWith("lang-") || c.startsWith("hljs")) : null;
        // Detecter le bouton Copy frère ou parent
        const parent = el.parentElement;
        const copyBtn = parent ? parent.querySelector('button') : null;
        const copyBtnText = copyBtn ? (copyBtn.textContent || "").trim() : null;

        results.push({
          tag: "PRE",
          className: (el.className || "").substring(0, 150),
          hasCodeChild: !!codeChild,
          codeClassName: codeChild ? (codeChild.className || "").substring(0, 150) : null,
          langClass: langClass || null,
          textPreview: text.substring(0, 80).trim(),
          textLength: text.length,
          parentTag: parent ? parent.tagName : null,
          parentClassName: parent ? (parent.className || "").substring(0, 100) : null,
          nearbyButtonText: copyBtnText,
          nearbyButtonClass: copyBtn ? (copyBtn.className || "").substring(0, 100) : null
        });
      });
      return results;
    },

    _findInputArea() {
      // Chercher textarea, contenteditable, ou role=textbox
      const candidates = document.querySelectorAll('textarea, [contenteditable="true"], [role="textbox"], input[type="text"]');
      const results = [];
      candidates.forEach(el => {
        const rect = el.getBoundingClientRect();
        // Ne garder que ceux visibles et en bas de page (typique d'un chat)
        if (rect.height > 0 && rect.bottom > window.innerHeight * 0.5) {
          results.push({
            tag: el.tagName,
            className: (el.className || "").substring(0, 200),
            type: el.type || null,
            placeholder: el.placeholder || el.getAttribute("data-placeholder") || null,
            contentEditable: el.contentEditable,
            role: el.getAttribute("role"),
            rect: { top: Math.round(rect.top), bottom: Math.round(rect.bottom), height: Math.round(rect.height), width: Math.round(rect.width) },
            parentClassName: el.parentElement ? (el.parentElement.className || "").substring(0, 100) : null
          });
        }
      });
      return results.length > 0 ? results : null;
    },

    _findSendButton() {
      const results = [];
      document.querySelectorAll("button").forEach(btn => {
        const text = (btn.textContent || "").trim().toLowerCase();
        const ariaLabel = (btn.getAttribute("aria-label") || "").toLowerCase();
        const rect = btn.getBoundingClientRect();
        // Bouton envoi = en bas de page + petit + contient SVG ou texte "send"
        const isBottom = rect.bottom > window.innerHeight * 0.5;
        const isSmall = rect.width < 200 && rect.height < 100;
        const hasSvg = btn.querySelector("svg") !== null;
        const hasHint = ["send", "submit", "envoyer", "enter"].some(k => text.includes(k) || ariaLabel.includes(k));
        // Aussi verifier s'il est proche d'un textarea
        const nearInput = btn.closest('[class*="input"], [class*="composer"], [class*="chat-input"], [class*="editor"]');

        if ((hasHint || (hasSvg && isBottom && isSmall) || nearInput) && isBottom) {
          results.push({
            tag: "BUTTON",
            className: (btn.className || "").substring(0, 200),
            text: text.substring(0, 50),
            ariaLabel: btn.getAttribute("aria-label"),
            disabled: btn.disabled,
            hasSvg: hasSvg,
            rect: { top: Math.round(rect.top), bottom: Math.round(rect.bottom), width: Math.round(rect.width), height: Math.round(rect.height) },
            nearInput: !!nearInput,
            parentClassName: btn.parentElement ? (btn.parentElement.className || "").substring(0, 100) : null,
            svgPath: hasSvg ? (btn.querySelector("svg path") || {}).getAttribute("d") || "" : null
          });
        }
      });
      return results;
    },

    _findCopyButtons() {
      const results = [];
      document.querySelectorAll("button").forEach(btn => {
        const text = (btn.textContent || "").trim().toLowerCase();
        const ariaLabel = (btn.getAttribute("aria-label") || "").toLowerCase();
        if (text.includes("copy") || text.includes("copier") || ariaLabel.includes("copy")) {
          const pre = btn.closest("div")?.querySelector("pre");
          results.push({
            text: (btn.textContent || "").trim().substring(0, 50),
            className: (btn.className || "").substring(0, 150),
            ariaLabel: btn.getAttribute("aria-label"),
            hasSiblingPre: !!pre,
            parentClassName: btn.parentElement ? (btn.parentElement.className || "").substring(0, 100) : null
          });
        }
      });
      return results;
    },

    _findAllRoles() {
      const roles = new Set();
      document.querySelectorAll("[role]").forEach(el => {
        roles.add(el.getAttribute("role") + " -> " + el.tagName + "." + (el.className || "").substring(0, 60));
      });
      return Array.from(roles).slice(0, 30);
    },

    _probeSelectors() {
      // Tester des selecteurs communs pour frameworks SPA
      const probes = {
        "div[class*='markdown']": document.querySelectorAll("div[class*='markdown']").length,
        "div[class*='prose']": document.querySelectorAll("div[class*='prose']").length,
        "div[class*='content']": document.querySelectorAll("div[class*='content']").length,
        "div[class*='agent']": document.querySelectorAll("div[class*='agent']").length,
        "div[class*='stream']": document.querySelectorAll("div[class*='stream']").length,
        "div[class*='thread']": document.querySelectorAll("div[class*='thread']").length,
        "div[class*='conversation']": document.querySelectorAll("div[class*='conversation']").length,
        "div[class*='chat']": document.querySelectorAll("div[class*='chat']").length,
        "div[class*='output']": document.querySelectorAll("div[class*='output']").length,
        "div[class*='result']": document.querySelectorAll("div[class*='result']").length,
        "[data-testid]": document.querySelectorAll("[data-testid]").length,
        "[data-message]": document.querySelectorAll("[data-message]").length,
        "[data-index]": document.querySelectorAll("[data-index]").length,
        "[data-role]": document.querySelectorAll("[data-role]").length,
        "[data-type]": document.querySelectorAll("[data-type]").length
      };
      // Ne garder que ceux > 0
      const found = {};
      for (const [sel, count] of Object.entries(probes)) {
        if (count > 0) found[sel] = count;
      }
      return found;
    },

    _getDepth(el) {
      let depth = 0;
      let current = el;
      while (current.parentElement) { depth++; current = current.parentElement; }
      return depth;
    }
  };

  // ── PANEL UI ───────────────────────────────────────────────
  // Panneau flottant en bas à droite
  const Panel = {
    el: null,
    contentEl: null,

    create() {
      // Container
      this.el = document.createElement("div");
      this.el.id = "wda5-panel";
      this.el.style.cssText = `
        position: fixed; bottom: 12px; right: 12px; z-index: 999999;
        width: 420px; max-height: 500px; overflow-y: auto;
        background: #1a1a2e; color: #e0e0e0; border: 1px solid #16213e;
        border-radius: 8px; font-family: 'Cascadia Code', 'Fira Code', monospace;
        font-size: 11px; box-shadow: 0 4px 20px rgba(0,0,0,0.5);
      `;

      // Header
      const header = document.createElement("div");
      header.style.cssText = `
        padding: 8px 12px; background: #16213e; border-radius: 8px 8px 0 0;
        display: flex; justify-content: space-between; align-items: center;
        cursor: move; user-select: none;
      `;
      header.innerHTML = '<span style="color:#0f3460;font-weight:bold;">WDA</span><span style="color:#e94560;font-weight:bold;"> v5.0</span><span style="margin-left:8px;color:#888;" id="wda5-status">...</span>';

      // Boutons header
      const btnGroup = document.createElement("div");

      const scanBtn = document.createElement("button");
      scanBtn.textContent = "SCAN DOM";
      scanBtn.style.cssText = "background:#e94560;color:white;border:none;padding:3px 8px;border-radius:4px;cursor:pointer;font-size:10px;margin-right:4px;font-family:inherit;";
      scanBtn.onclick = () => this.runScan();

      const copyBtn = document.createElement("button");
      copyBtn.textContent = "COPIER";
      copyBtn.style.cssText = "background:#0f3460;color:white;border:none;padding:3px 8px;border-radius:4px;cursor:pointer;font-size:10px;margin-right:4px;font-family:inherit;";
      copyBtn.onclick = () => this.copyResults();

      const minBtn = document.createElement("button");
      minBtn.textContent = "—";
      minBtn.style.cssText = "background:none;color:#888;border:none;padding:3px 6px;cursor:pointer;font-size:14px;font-family:inherit;";
      minBtn.onclick = () => {
        const isHidden = this.contentEl.style.display === "none";
        this.contentEl.style.display = isHidden ? "block" : "none";
        minBtn.textContent = isHidden ? "—" : "+";
      };

      btnGroup.appendChild(scanBtn);
      btnGroup.appendChild(copyBtn);
      btnGroup.appendChild(minBtn);
      header.appendChild(btnGroup);

      // Content
      this.contentEl = document.createElement("div");
      this.contentEl.style.cssText = "padding: 10px 12px; max-height: 440px; overflow-y: auto;";
      this.contentEl.innerHTML = '<div style="color:#888;">Clique <span style="color:#e94560;">SCAN DOM</span> pour analyser la page Genspark.</div>';

      this.el.appendChild(header);
      this.el.appendChild(this.contentEl);
      document.body.appendChild(this.el);
      Logger.info("Panel v5.0 injecte dans la page");
    },

    setStatus(text, color) {
      const el = document.getElementById("wda5-status");
      if (el) { el.textContent = text; el.style.color = color || "#888"; }
    },

    async runScan() {
      this.setStatus("Scan...", "#f0c040");
      this.contentEl.innerHTML = '<div style="color:#f0c040;">Scan du DOM en cours...</div>';

      // Petite pause pour laisser le DOM se stabiliser
      await new Promise(r => setTimeout(r, 500));

      const results = DOMScanner.scan();

      // Envoyer au serveur
      const serverResp = await Server.send("/ext-log", {
        message: "DOM_SCAN_RESULT: " + JSON.stringify(results).substring(0, 5000)
      });

      // Afficher les résultats
      this.renderResults(results);

      if (serverResp) {
        this.setStatus("En ligne", "#4ade80");
      } else {
        this.setStatus("Serveur OFF", "#ef4444");
      }
    },

    renderResults(r) {
      const h = (label, count, color) => `<span style="color:${color || '#e0e0e0'}">${label}: <b>${count}</b></span>`;
      let html = '<div style="margin-bottom:8px;padding-bottom:6px;border-bottom:1px solid #333;">';
      html += `<div style="color:#4ade80;font-weight:bold;margin-bottom:4px;">DIAGNOSTIC DOM GENSPARK</div>`;
      html += `<div style="font-size:10px;color:#666;">${r.url}</div>`;
      html += '</div>';

      // Root App
      html += '<div style="margin-bottom:6px;">';
      html += '<div style="color:#e94560;font-weight:bold;">Root App</div>';
      if (r.rootApp) {
        html += `<div style="color:#aaa;font-size:10px;">${r.rootApp.selector} | class="${r.rootApp.className.substring(0, 80)}" | ${r.rootApp.childCount} enfants</div>`;
      } else {
        html += '<div style="color:#ef4444;">Non trouve</div>';
      }
      html += '</div>';

      // Chat containers
      html += '<div style="margin-bottom:6px;">';
      html += `<div style="color:#e94560;font-weight:bold;">Conteneurs Chat (scroll) — ${r.chatContainers.length} trouves</div>`;
      r.chatContainers.forEach((c, i) => {
        html += `<div style="color:#aaa;font-size:10px;margin-left:8px;margin-top:2px;">`;
        html += `[${i}] ${c.tag} .${(c.className || "").substring(0, 60)} | ${c.childCount} enfants | scroll=${c.scrollHeight}/${c.offsetHeight}`;
        if (c.role) html += ` | role="${c.role}"`;
        if (c.dataAttrs.length > 0) html += ` | ${c.dataAttrs.join(", ")}`;
        html += `</div>`;
      });
      html += '</div>';

      // Messages
      html += '<div style="margin-bottom:6px;">';
      html += `<div style="color:#e94560;font-weight:bold;">Messages — ${r.messageElements.length} elements</div>`;
      r.messageElements.slice(0, 10).forEach((m, i) => {
        html += `<div style="color:#aaa;font-size:10px;margin-left:8px;margin-top:2px;">`;
        html += `[${i}] sel="${m.matchedSelector}" | .${(m.className || "").substring(0, 50)} | code=${m.hasCode} | "${m.textPreview.substring(0, 40)}"`;
        if (m.dataAttrs.length > 0) html += ` | ${m.dataAttrs.join(", ")}`;
        html += `</div>`;
      });
      html += '</div>';

      // Code blocks
      html += '<div style="margin-bottom:6px;">';
      html += `<div style="color:#e94560;font-weight:bold;">Blocs Code (PRE) — ${r.codeBlocks.length} trouves</div>`;
      r.codeBlocks.slice(0, 5).forEach((c, i) => {
        html += `<div style="color:#aaa;font-size:10px;margin-left:8px;margin-top:2px;">`;
        html += `[${i}] code_child=${c.hasCodeChild} | lang="${c.langClass || "?"}" | btn="${c.nearbyButtonText || "none"}" | "${c.textPreview.substring(0, 40)}"`;
        html += `</div>`;
      });
      html += '</div>';

      // Input
      html += '<div style="margin-bottom:6px;">';
      html += `<div style="color:#e94560;font-weight:bold;">Zone de saisie</div>`;
      if (r.inputArea) {
        r.inputArea.forEach((inp, i) => {
          html += `<div style="color:#aaa;font-size:10px;margin-left:8px;">[${i}] ${inp.tag} | placeholder="${inp.placeholder || "?"}" | ${inp.rect.width}x${inp.rect.height}px</div>`;
        });
      } else {
        html += '<div style="color:#ef4444;margin-left:8px;">Non trouve</div>';
      }
      html += '</div>';

      // Send buttons
      html += '<div style="margin-bottom:6px;">';
      html += `<div style="color:#e94560;font-weight:bold;">Boutons Envoi — ${r.sendButton.length} candidats</div>`;
      r.sendButton.forEach((b, i) => {
        html += `<div style="color:#aaa;font-size:10px;margin-left:8px;">[${i}] text="${b.text}" | svg=${b.hasSvg} | disabled=${b.disabled} | nearInput=${b.nearInput} | ${b.rect.width}x${b.rect.height}px</div>`;
      });
      html += '</div>';

      // Copy buttons
      html += '<div style="margin-bottom:6px;">';
      html += `<div style="color:#e94560;font-weight:bold;">Boutons Copy — ${r.copyButtons.length}</div>`;
      r.copyButtons.slice(0, 5).forEach((b, i) => {
        html += `<div style="color:#aaa;font-size:10px;margin-left:8px;">[${i}] text="${b.text}" | pre_nearby=${b.hasSiblingPre}</div>`;
      });
      html += '</div>';

      // Probe selectors
      html += '<div style="margin-bottom:6px;">';
      html += `<div style="color:#e94560;font-weight:bold;">Selecteurs detectes</div>`;
      for (const [sel, count] of Object.entries(r.interestingSelectors)) {
        html += `<div style="color:#4ade80;font-size:10px;margin-left:8px;">${sel} → ${count}</div>`;
      }
      if (Object.keys(r.interestingSelectors).length === 0) {
        html += '<div style="color:#ef4444;margin-left:8px;">Aucun selecteur connu detecte</div>';
      }
      html += '</div>';

      // Roles
      html += '<div style="margin-bottom:6px;">';
      html += `<div style="color:#e94560;font-weight:bold;">Roles ARIA — ${r.allRoles.length}</div>`;
      r.allRoles.slice(0, 10).forEach(role => {
        html += `<div style="color:#aaa;font-size:10px;margin-left:8px;">${role}</div>`;
      });
      html += '</div>';

      html += '<div style="color:#666;font-size:9px;margin-top:8px;border-top:1px solid #333;padding-top:6px;">Clique COPIER pour envoyer ce JSON a Claude. Il generera content.js v5.0 avec les bons selecteurs.</div>';

      this.contentEl.innerHTML = html;
    },

    async copyResults() {
      if (!DOMScanner.results) {
        this.contentEl.innerHTML = '<div style="color:#ef4444;">Lance d\'abord un SCAN DOM !</div>';
        return;
      }
      try {
        const json = JSON.stringify(DOMScanner.results, null, 2);
        await navigator.clipboard.writeText(json);
        this.setStatus("JSON copie !", "#4ade80");
        Logger.info("Resultats DOM copies dans le clipboard (" + json.length + " chars)");
        setTimeout(() => this.setStatus("En ligne", "#4ade80"), 2000);
      } catch (e) {
        // Fallback: prompt
        const json = JSON.stringify(DOMScanner.results, null, 2);
        const textarea = document.createElement("textarea");
        textarea.value = json;
        textarea.style.cssText = "position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);z-index:9999999;width:600px;height:400px;font-size:11px;";
        document.body.appendChild(textarea);
        textarea.select();
        Logger.warn("Clipboard non disponible, textarea affichee pour copie manuelle");
      }
    }
  };

  // ── INIT ───────────────────────────────────────────────────
  async function init() {
    Logger.info("Wakfu Dev Assistant v5.0 - Phase DIAGNOSTIC");
    Logger.info("URL: " + window.location.href);

    // Vérifier le serveur
    const serverOk = await Server.ping();
    Logger.info("Dev Server: " + (serverOk ? "EN LIGNE" : "HORS LIGNE"));

    // Créer le panneau
    Panel.create();
    Panel.setStatus(serverOk ? "En ligne" : "Serveur OFF", serverOk ? "#4ade80" : "#ef4444");

    // Si le serveur est en ligne, notifier
    if (serverOk) {
      await Server.send("/ext-log", {
        message: "WDA v5.0 DIAGNOSTIC charge sur " + window.location.href
      });
    }

    Logger.info("Init complete — clique SCAN DOM dans le panneau");
  }

  // Lancer quand le DOM est prêt
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => setTimeout(init, 1500));
  } else {
    setTimeout(init, 1500);
  }

})();
