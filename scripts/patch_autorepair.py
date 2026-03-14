import pathlib

f = pathlib.Path(r'H:\Code\Ankama Dev\wakfu-dev-extension\content.js')
c = f.read_text('utf-8')

# Remplacer autoInjectResult par une version avec boucle auto-repair
old_func_start = "async function autoInjectResult(text) {"
old_func_end = "  }, 600);\n}"

# Trouver et remplacer toute la fonction
start_idx = c.index(old_func_start)
# Chercher la fin de la fonction (le dernier } avant la prochaine function)
end_search = c[start_idx:]
brace_count = 0
end_idx = start_idx
for i, ch in enumerate(end_search):
    if ch == '{':
        brace_count += 1
    elif ch == '}':
        brace_count -= 1
        if brace_count == 0:
            end_idx = start_idx + i + 1
            break

old_func = c[start_idx:end_idx]

new_func = """async function autoInjectResult(text) {
  var ta = getTextarea();
  if (!ta) { logExt('Textarea introuvable'); return; }
  var output = text.output || '';
  var duration = text.duration || '?';
  var command = text.command || '';
  var returncode = text.success ? 0 : 1;
  var maxRetries = 3;
  var attempt = 0;
  var finalMsg = '';

  while (attempt < maxRetries) {
    attempt++;
    try {
      logExt('CONDUCTOR: analyse du resultat (tentative ' + attempt + ')...');
      var decision = await serverFetch('/conductor', {
        method: 'POST',
        body: JSON.stringify({ command: command, output: output, returncode: returncode, task_context: '' })
      });

      if (!decision || !decision.action) {
        finalMsg = 'Resultat de l\\'execution (' + duration + '):\\n```\\n' + output.slice(0, 3000) + '\\n```\\nContinue avec la prochaine etape.';
        break;
      }

      logExt('CONDUCTOR: ' + decision.action + ' - ' + (decision.analysis || '').substring(0, 60));

      if (decision.action === 'done' || decision.action === 'continue') {
        finalMsg = 'Resultat de l\\'execution (' + duration + '):\\n```\\n' + output.slice(0, 3000) + '\\n```\\n' + (decision.formatted_message || 'Continue.');
        break;
      }

      if (decision.action === 'escalate') {
        finalMsg = 'Resultat de l\\'execution (' + duration + '):\\n```\\n' + output.slice(0, 3000) + '\\n```\\n[ESCALADE] ' + (decision.formatted_message || 'Probleme critique.');
        break;
      }

      if (decision.action === 'fix' && decision.fix_command) {
        logExt('AUTO-REPAIR tentative ' + attempt + ': ' + decision.fix_command.substring(0, 60));
        var fixRes = await serverFetch('/execute', {
          method: 'POST',
          body: JSON.stringify({ command: decision.fix_command, timeout: 30 })
        });
        if (fixRes && fixRes.success) {
          logExt('AUTO-REPAIR OK');
          output = fixRes.stdout || fixRes.output || 'Fix OK';
          returncode = 0;
          command = decision.fix_command;
          duration = (fixRes.duration || '?') + 's';
          continue;
        } else {
          logExt('AUTO-REPAIR ECHEC');
          output = 'Erreur fix: ' + (fixRes ? fixRes.stderr || fixRes.error || '' : 'no response');
          returncode = 1;
          continue;
        }
      }

      if (decision.action === 'fix') {
        finalMsg = 'Resultat de l\\'execution (' + duration + '):\\n```\\n' + output.slice(0, 3000) + '\\n```\\n' + (decision.formatted_message || 'Erreur a corriger.');
        break;
      }

      finalMsg = 'Resultat de l\\'execution (' + duration + '):\\n```\\n' + output.slice(0, 3000) + '\\n```\\nContinue.';
      break;

    } catch(e) {
      logExt('CONDUCTOR err: ' + e.message);
      finalMsg = 'Resultat de l\\'execution (' + duration + '):\\n```\\n' + output.slice(0, 3000) + '\\n```\\nContinue avec la prochaine etape.';
      break;
    }
  }

  var nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set;
  nativeSetter.call(ta, finalMsg);
  ta.dispatchEvent(new Event('input', { bubbles: true }));
  setTimeout(function() {
    if (clickSendButton()) {
      state.exchanges++;
      updatePanel();
      logExt('Auto-send OK (echange #' + state.exchanges + ')');
    } else {
      logExt('Auto-send ECHEC: bouton send introuvable');
    }
  }, 600);
}"""

c = c[:start_idx] + new_func + c[end_idx:]
f.write_text(c, 'utf-8')
print('Auto-repair pipeline - content.js:', f.stat().st_size, 'octets')
