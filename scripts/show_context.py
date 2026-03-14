import pathlib

f = pathlib.Path(r'H:\Code\Ankama Dev\wakfu-dev-extension\content.js')
c = f.read_text('utf-8')

# Voir le contexte autour de la ligne 127
lines = c.split('\n')
print('=== Contexte L120-140 ===')
for i in range(119, min(140, len(lines))):
    print('L' + str(i+1) + ': ' + lines[i])
