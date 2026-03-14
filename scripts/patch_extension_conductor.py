import pathlib

f = pathlib.Path(r'H:\Code\Ankama Dev\wakfu-dev-extension\content.js')
c = f.read_text('utf-8')

# Remplacer autoInjectResult pour passer par le Conductor
old = """function autoInjectResult(text) {
  var ta = getTextarea();
  if (!ta) { logExt('Textarea introuvable'); return; }
  var output = text.output || '';
  var duration = text.duration || '?';
  // Construire le message
  var msg = 'Resultat de l\\'execution (' + duration + '):\\n```\\n' + output.slice(0, 3000) + '\\n```\\nContinue avec la prochaine etape.';"""

new = """async function autoInjectResult(text) {
  var ta = getTextarea();
  if (!ta) { logExt('Textarea introuvable'); return; }
  var output = text.output || '';
  var duration = text.duration || '?';
  var command = text.command || '';
  var returncode = text.success ? 0 : 1;
  // Demander au Conductor d analyser le resultat
  var msg = '';
  try {
    logExt('CONDUCTOR: analyse du resultat...');
    var decision = await serverFetch('/conductor', {
      method: 'POST',
      body: JSON.stringify({ command: command, output: output, returncode: returncode, task_context: '' })
    });
    if (decision && decision.formatted_message) {
      logExt('CONDUCTOR: ' + (decision.action || '?') + ' - ' + (decision.analysis || '').substring(0, 60));
      msg = 'Resultat de l\\'execution (' + duration + '):\\n```\\n' + output.slice(0, 3000) + '\\n```\\n' + decision.formatted_message;
    } else {
      msg = 'Resultat de l\\'execution (' + duration + '):\\n```\\n' + output.slice(0, 3000) + '\\n```\\nContinue avec la prochaine etape.';
    }
  } catch(e) {
    logExt('CONDUCTOR err: ' + e.message);
    msg = 'Resultat de l\\'execution (' + duration + '):\\n```\\n' + output.slice(0, 3000) + '\\n```\\nContinue avec la prochaine etape.';
  }"""

c = c.replace(old, new)

# Aussi passer la commande et le success dans les appels a autoInjectResult
c = c.replace(
    "autoInjectResult({\n            output: res.stdout || res.output || 'OK',\n            duration: (res.duration || '?') + 's'\n          });",
    "autoInjectResult({\n            output: res.stdout || res.output || 'OK',\n            duration: (res.duration || '?') + 's',\n            command: cmd,\n            success: true\n          });"
)

c = c.replace(
    "autoInjectResult({\n            output: 'Erreur: ' + (res ? (res.error || res.stderr || JSON.stringify(res)) : 'No response'),\n            duration: (res ? res.duration || '0' : '0') + 's'\n          });",
    "autoInjectResult({\n            output: 'Erreur: ' + (res ? (res.error || res.stderr || JSON.stringify(res)) : 'No response'),\n            duration: (res ? res.duration || '0' : '0') + 's',\n            command: cmd,\n            success: false\n          });"
)

f.write_text(c, 'utf-8')
print('Conductor branche dans content.js:', f.stat().st_size, 'octets')
