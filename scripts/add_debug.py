import pathlib

f = pathlib.Path(r'H:\Code\Ankama Dev\wakfu-dev-extension\content.js')
c = f.read_text('utf-8')

# Ajouter un log avant l'envoi au serveur dans la fonction exec
old = "var res = await serverFetch('/execute', {"
new = "logExt('DEBUG CMD: ' + cmd.substring(0, 80));\n        var res = await serverFetch('/execute', {"

c = c.replace(old, new)
f.write_text(c, 'utf-8')
print('Debug log ajoute - content.js:', f.stat().st_size, 'octets')
