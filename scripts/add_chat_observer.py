import pathlib

f = pathlib.Path(r'H:\Code\Ankama Dev\wakfu-dev-extension\content.js')
c = f.read_text('utf-8')

# Ajouter un observateur de messages du chat
chat_observer = """
// === CHAT MEMORY OBSERVER ===
let lastMessageCount = 0;

function captureNewMessages() {
  const msgs = document.querySelectorAll('[class*="message"], [class*="Message"]');
  if (msgs.length > lastMessageCount) {
    const newMsgs = Array.from(msgs).slice(lastMessageCount);
    newMsgs.forEach(m => {
      const text = (m.textContent || '').trim().substring(0, 500);
      if (text.length > 10) {
        const isUser = m.className.includes('user') || m.closest('[class*="user"]');
        fetch(SERVER + '/ext-log', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({
            message: (isUser ? '[USER] ' : '[ASSISTANT] ') + text,
            type: 'chat'
          })
        }).catch(() => {});
      }
    });
    lastMessageCount = msgs.length;
  }
}

setInterval(captureNewMessages, 5000);
"""

# Ajouter avant le dernier })(); ou a la fin du fichier
if '// === CHAT MEMORY OBSERVER ===' not in c:
    c = c + '\n' + chat_observer
    f.write_text(c, 'utf-8')
    print('Chat observer ajoute - content.js:', f.stat().st_size, 'octets')
else:
    print('Chat observer deja present')
