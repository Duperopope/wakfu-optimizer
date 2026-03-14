import pathlib

f = pathlib.Path(r'H:\Code\Ankama Dev\wakfu-optimizer\scripts\dev_server.py')
c = f.read_text('utf-8')

# Remplacer le bloc casse par la version correcte
old = """try:
    from memory_manager import get_manager as get_memory
    HAS_MEMORY = True
try:
    from conductor import ask_conductor, format_message
    HAS_CONDUCTOR = True
except Exception as e:
    print('Conductor non disponible:', e)
    HAS_CONDUCTOR = False
except Exception as e:
    print(f"Memory Manager non disponible: {e}")
    HAS_MEMORY = False"""

new = """try:
    from memory_manager import get_manager as get_memory
    HAS_MEMORY = True
except Exception as e:
    print(f"Memory Manager non disponible: {e}")
    HAS_MEMORY = False

try:
    from conductor import ask_conductor, format_message
    HAS_CONDUCTOR = True
except Exception as e:
    print('Conductor non disponible:', e)
    HAS_CONDUCTOR = False"""

c = c.replace(old, new)
f.write_text(c, 'utf-8')
print('Fix imports - dev_server.py:', f.stat().st_size, 'octets')
