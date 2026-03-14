import pathlib

f = pathlib.Path(r'H:\Code\Ankama Dev\wakfu-optimizer\scripts\dev_server.py')
c = f.read_text('utf-8')

old = '''    log("SESSION", f"SESSION_HANDOFF.md ({len(handoff)} lignes)")'''

new = '''    log("SESSION", f"SESSION_HANDOFF.md ({len(handoff)} lignes)")
    # Consolider la memoire
    if HAS_MEMORY:
        try:
            mm = get_memory()
            mm.end_session()
            log("SESSION", "Memoire consolidee (episodique + procedurale + briefing)")
        except Exception as e:
            log("SESSION", "Erreur consolidation memoire: " + str(e))'''

if old in c:
    c = c.replace(old, new)
    print('Memory consolidation ajoutee dans session-end')
else:
    print('Pattern non trouve')

f.write_text(c, 'utf-8')
print(f'dev_server.py - {f.stat().st_size} octets')
