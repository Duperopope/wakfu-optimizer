import pathlib

f = pathlib.Path(r'H:\Code\Ankama Dev\wakfu-optimizer\scripts\dev_server.py')
c = f.read_text('utf-8')

# Supprimer les routes mal inseres
old_block = '''                self._json({"success": False, "error": str(e)})
                elif path == "/ext-log":
            message = body.get("message", "")
            if HAS_MEMORY:
                try:
                    mm = get_memory()
                    mm.on_ext_log(message)
                except: pass
            self._json({"success": True})
                elif path == "/memory-status":
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
        elif path == "/ollama":'''

new_block = '''                self._json({"success": False, "error": str(e)})
        elif path == "/ext-log":
            message = body.get("message", "")
            if HAS_MEMORY:
                try:
                    mm = get_memory()
                    mm.on_ext_log(message)
                except: pass
            self._json({"success": True})
        elif path == "/memory-status":
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
        elif path == "/ollama":'''

if old_block in c:
    c = c.replace(old_block, new_block)
    print('Routes ext-log et memory-status corrigees')
else:
    print('Pattern non trouve')

f.write_text(c, 'utf-8')
print(f'dev_server.py - {f.stat().st_size} octets')
