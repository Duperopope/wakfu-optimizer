import pathlib

f = pathlib.Path(r'H:\Code\Ankama Dev\wakfu-optimizer\scripts\dev_server.py')
c = f.read_text('utf-8')

old = '''def write_file(rel_path, content):
    full = PROJECT / rel_path.replace("/", os.sep)
    if not str(full.resolve()).startswith(str(PROJECT.resolve())): return {"success": False, "error": "Hors projet"}
    try:
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_text(content, "utf-8")
        log("WRITE", f"{rel_path} ({len(content)} chars)")
        return {"success": True, "path": rel_path, "size": len(content)}
    except Exception as e: return {"success": False, "error": str(e)}'''

new = '''def write_file(rel_path, content):
    full = PROJECT / rel_path.replace("/", os.sep)
    if not str(full.resolve()).startswith(str(PROJECT.resolve())): return {"success": False, "error": "Hors projet"}
    try:
        # Lire ancien contenu pour review de regression
        old_content = None
        if full.exists():
            try: old_content = full.read_text("utf-8")
            except: pass
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_text(content, "utf-8")
        log("WRITE", f"{rel_path} ({len(content)} chars)")
        # Memory + Reviewer hook (background)
        if HAS_MEMORY:
            try:
                from threading import Thread
                mm = get_memory()
                mm.on_file_modified(rel_path, old_content, content)
                mm.episodic.record(
                    "Ecriture fichier: " + rel_path,
                    "write_file " + rel_path,
                    str(len(content)) + " chars ecrit",
                    True,
                    ["write", rel_path.split("/")[-1]]
                )
            except: pass
        return {"success": True, "path": rel_path, "size": len(content)}
    except Exception as e: return {"success": False, "error": str(e)}'''

if old in c:
    c = c.replace(old, new)
    print('Reviewer hook ajoute sur write_file')
else:
    print('Pattern non trouve')

f.write_text(c, 'utf-8')
print(f'dev_server.py - {f.stat().st_size} octets')
