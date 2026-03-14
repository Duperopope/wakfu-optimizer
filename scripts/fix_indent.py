import pathlib

f = pathlib.Path(r'H:\Code\Ankama Dev\wakfu-optimizer\scripts\dev_server.py')
c = f.read_text('utf-8')

old = '''        duration = round(time.time() - start, 2)
        # Memory hook
            if HAS_MEMORY:
                try:
                    mm = get_memory()
                    mm.on_command_executed(cmd[:300], stdout[:500], returncode == 0, duration)
                except: pass
            log("RESULT",'''

new = '''        duration = round(time.time() - start, 2)
        # Memory hook
        if HAS_MEMORY:
            try:
                mm = get_memory()
                mm.on_command_executed(cmd[:300], result.stdout[:500], result.returncode == 0, duration)
            except: pass
        log("RESULT",'''

if old in c:
    c = c.replace(old, new)
    print('Indentation corrigee')
else:
    print('Pattern non trouve')

f.write_text(c, 'utf-8')
print(f'dev_server.py - {f.stat().st_size} octets')
