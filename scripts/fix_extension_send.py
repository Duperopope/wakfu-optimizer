import pathlib

f = pathlib.Path(r'H:\Code\Ankama Dev\wakfu-dev-extension\content.js')
c = f.read_text('utf-8')

# FIX 1: Remplacer clickSendButton par detection exacte du SVG Genspark
old_click = """function clickSendButton() {
  const btns = document.querySelectorAll('button');
  for (const b of btns) {
    const svg = b.querySelector('svg');
    if (svg && b.offsetParent !== null && !b.disabled) {
      const r = b.getBoundingClientRect();
      if (r.width > 20 && r.width < 60) { b.click(); return true; }
    }
  }
  return false;
}"""

new_click = """function clickSendButton() {
  // Chercher le bouton d'envoi Genspark via son SVG clip-path exact
  const clips = document.querySelectorAll('clipPath');
  for (const clip of clips) {
    if (clip.id && clip.id.includes('clip0_739_13340')) {
      const svg = clip.closest('svg');
      if (svg) {
        const btn = svg.closest('button');
        if (btn && !btn.disabled) { btn.click(); return true; }
      }
    }
  }
  // Fallback: chercher bouton avec SVG 24x24 pres du textarea
  const ta = getTextarea();
  if (ta) {
    const parent = ta.closest('form') || ta.parentElement;
    if (parent) {
      const btns = parent.querySelectorAll('button');
      for (const b of btns) {
        if (b.querySelector('svg') && !b.disabled) { b.click(); return true; }
      }
    }
  }
  return false;
}"""

if old_click in c:
    c = c.replace(old_click, new_click)
    print('Fix clickSendButton: OK')
else:
    print('clickSendButton non trouve')

# FIX 2: autoInjectResult - utiliser value + input event au lieu de clipboard
old_inject = """function autoInjectResult(text) {
  const ta = getTextarea();
  if (!ta) { logExt('Textarea introuvable'); return; }"""

new_inject = """function autoInjectResult(text) {
  const ta = getTextarea();
  if (!ta) { logExt('Textarea introuvable'); return; }
  // Nettoyer le prefixe Copy si present
  ta.value = '';
  ta.dispatchEvent(new Event('input', { bubbles: true }));"""

if old_inject in c:
    c = c.replace(old_inject, new_inject)
    print('Fix autoInjectResult: OK')
else:
    print('autoInjectResult non trouve')

f.write_text(c, 'utf-8')
print(f'content.js - {f.stat().st_size} octets')
