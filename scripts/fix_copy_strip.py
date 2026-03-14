import pathlib

f = pathlib.Path(r'H:\Code\Ankama Dev\wakfu-dev-extension\content.js')
c = f.read_text('utf-8')

# Remplacer l'extraction de code par une version qui nettoie le prefix Copy
old = "var code = codeEl2.textContent || '';"
new = """var rawCode = codeEl2.textContent || '';
    var code = rawCode.replace(/^Copy/, '').trimStart();"""

c = c.replace(old, new)

# Aussi dans la fonction exec, nettoyer le cmd
old2 = "var cmd = code;"
new2 = "var cmd = code.replace(/^Copy/, '').trimStart();"

c = c.replace(old2, new2)

f.write_text(c, 'utf-8')
print('Fix Copy strip - content.js:', f.stat().st_size, 'octets')
