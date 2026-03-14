import pathlib

f = pathlib.Path(r'H:\Code\Ankama Dev\wakfu-optimizer\scripts\dev_server.py')
c = f.read_text('utf-8')

# 1. Ajouter import memory_manager apres les imports existants
if 'memory_manager' not in c:
    c = c.replace(
        'from pathlib import Path',
        'from pathlib import Path\ntry:\n    from memory_manager import get_manager as get_memory\n    HAS_MEMORY = True\nexcept Exception as e:\n    print(f"Memory Manager non disponible: {e}")\n    HAS_MEMORY = False'
    )
    print('Import memory_manager ajoute')

# 2. Ajouter hook apres execution de commande
# Trouver la ligne qui log le resultat d execution
old_result_log = 'log("RESULT",'
if old_result_log in c and 'HAS_MEMORY' not in c.split(old_result_log)[1][:200]:
    c = c.replace(
        old_result_log,
        '# Memory hook\n            if HAS_MEMORY:\n                try:\n                    mm = get_memory()\n                    mm.on_command_executed(cmd[:300], stdout[:500], returncode == 0, duration)\n                except: pass\n            ' + old_result_log
    )
    print('Hook memory sur /execute ajoute')

# 3. Ajouter route /ext-log avant /ollama
ollama_line = 'elif path == "/ollama":'
if '/ext-log' not in c and ollama_line in c:
    ext_log_route = '''        elif path == "/ext-log":
            message = body.get("message", "")
            if HAS_MEMORY:
                try:
                    mm = get_memory()
                    mm.on_ext_log(message)
                except: pass
            self._json({"success": True})
'''
    c = c.replace(ollama_line, ext_log_route + '        ' + ollama_line)
    print('Route /ext-log ajoutee')

# 4. Ajouter route /memory-status avant /ollama
if '/memory-status' not in c:
    memory_route = '''        elif path == "/memory-status":
            if HAS_MEMORY:
                mm = get_memory()
                self._json({
                    "success": True,
                    "episodes": len(mm.episodic.episodes),
                    "procedures": len(mm.procedural.procedures),
                    "session": mm.session.get_summary(),
                    "working": mm.working.summarize()
                })
            else:
                self._json({"success": False, "error": "Memory Manager non disponible"})
'''
    c = c.replace(ollama_line, memory_route + '        ' + ollama_line)
    print('Route /memory-status ajoutee')

f.write_text(c, 'utf-8')
print(f'dev_server.py mis a jour - {f.stat().st_size} octets')
