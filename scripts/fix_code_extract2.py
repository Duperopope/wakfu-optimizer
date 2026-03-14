import pathlib

f = pathlib.Path(r'H:\Code\Ankama Dev\wakfu-dev-extension\content.js')
c = f.read_text('utf-8')

# Remplacer l'extraction de code pour utiliser le <code> directement
old = "    const code = el.textContent || '';"
new = "    const codeEl2 = el.tagName === 'CODE' ? el : (el.querySelector('code') || el);\n    const code = codeEl2.textContent || '';"

c = c.replace(old, new)

f.write_text(c, 'utf-8')
print('Fix code extraction - content.js:', f.stat().st_size, 'octets')

# Verifier
lines = f.read_text('utf-8').split('\n')
for i in range(125, 142):
    print('L' + str(i+1) + ': ' + lines[i])
