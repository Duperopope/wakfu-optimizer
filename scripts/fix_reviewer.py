import pathlib, json

f = pathlib.Path(r'H:\Code\Ankama Dev\wakfu-optimizer\scripts\memory_manager.py')
c = f.read_text('utf-8')

# Remplacer deepseek-coder-v2 par qwen2.5-coder:7b pour le Reviewer
# (meme modele que SENTINEL mais prompt different - plus rapide, pas de timeout)
c = c.replace('deepseek-coder-v2:latest', 'qwen2.5-coder:7b')

# Reduire le timeout Ollama de 60s a 20s
c = c.replace('timeout=60', 'timeout=20')
c = c.replace('timeout = 60', 'timeout = 20')

# Ajouter un timeout sur les requetes Ollama si absent
if 'timeout=20' not in c and 'timeout=30' in c:
    c = c.replace('timeout=30', 'timeout=20')

f.write_text(c, 'utf-8')
print('Reviewer: qwen2.5-coder:7b (rapide)')
print('Timeout: 20s')
print('Taille:', f.stat().st_size, 'octets')
