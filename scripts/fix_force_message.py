import pathlib

f = pathlib.Path(r'H:\Code\Ankama Dev\wakfu-dev-extension\content.js')
c = f.read_text('utf-8')

# Le probleme: quand action=fix sans fix_command, le code tombe dans le dernier else
# et envoie juste "Continue." au lieu du vrai message du Conductor
# Aussi apres 3 tentatives le while sort et finalMsg peut etre vide

# Verifier que le fallback apres la boucle while envoie toujours un message
old_after_while = """  var nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set;
  nativeSetter.call(ta, finalMsg);"""

new_after_while = """  // Si finalMsg est vide apres les tentatives, forcer un message
  if (!finalMsg || finalMsg.length < 10) {
    finalMsg = 'Resultat de l\\'execution (' + duration + '):\\n```\\n' + output.slice(0, 3000) + '\\n```\\nLe Conductor n\\'a pas pu corriger automatiquement. Analyse l\\'erreur et propose une solution.';
  }
  logExt('MESSAGE FINAL: ' + finalMsg.substring(0, 80));
  var nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set;
  nativeSetter.call(ta, finalMsg);"""

c = c.replace(old_after_while, new_after_while)

f.write_text(c, 'utf-8')
print('Fix message obligatoire - content.js:', f.stat().st_size, 'octets')
