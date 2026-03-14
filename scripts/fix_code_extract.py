import pathlib

f = pathlib.Path(r'H:\Code\Ankama Dev\wakfu-dev-extension\content.js')
c = f.read_text('utf-8')

# Trouver comment le code est extrait dans processBlock
# Le probleme: block.textContent inclut le texte du bouton "Copier"
# Solution: extraire seulement depuis block.querySelector('code')

old = "const code = block.textContent || '';"
new = "const codeEl = block.querySelector('code'); const code = codeEl ? codeEl.textContent || '' : block.textContent || '';"

if old in c:
    c = c.replace(old, new)
    print('Fix extraction code: OK')
else:
    print('Pattern non trouve, recherche alternative...')
    lines = c.split('\n')
    for i, line in enumerate(lines):
        if 'textContent' in line and ('code' in line.lower() or 'block' in line.lower()):
            print('L' + str(i+1) + ': ' + line.strip())

f.write_text(c, 'utf-8')
print('content.js:', f.stat().st_size, 'octets')
