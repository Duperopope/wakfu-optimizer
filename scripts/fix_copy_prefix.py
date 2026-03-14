import pathlib

f = pathlib.Path(r'H:\Code\Ankama Dev\wakfu-dev-extension\content.js')
c = f.read_text('utf-8')

# Ajouter un guard dans processBlock pour ignorer les textes commencant par "Copy"
old = "function processBlock(block) {"
new = """function processBlock(block) {
  const raw = block.textContent || '';
  if (raw.startsWith('Copy')) {
    const cleaned = raw.replace(/^Copy/, '').trim();
    if (block.querySelector('code')) {
      block.querySelector('code').textContent = cleaned;
    }
  }"""

c = c.replace(old, new)
f.write_text(c, 'utf-8')
print('Fix Copy prefix - content.js:', f.stat().st_size, 'octets')
