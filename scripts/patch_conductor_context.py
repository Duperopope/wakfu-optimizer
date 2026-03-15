import pathlib

cond = pathlib.Path(r'H:\Code\Ankama Dev\wakfu-optimizer\scripts\conductor.py')
cc = cond.read_text('utf-8')

old = "def format_message(decision):"
new = """def format_message(decision):
    # Mini-contexte anti context-rot
    try:
        project = Path(__file__).resolve().parent.parent
        todo_file = project / 'PROJECT_MEMORY.md'
        if todo_file.exists():
            tc = todo_file.read_text('utf-8', errors='replace')
            idx = tc.find('- [ ]')
            if idx > 0:
                end = tc.find('\\n', idx)
                current_task = tc[idx:end].strip() if end > 0 else tc[idx:idx+100].strip()
                decision['current_task'] = current_task
    except: pass"""

if old in cc:
    cc = cc.replace(old, new)
    cond.write_text(cc, 'utf-8')
    print('OK conductor.py:', cond.stat().st_size, 'octets')
else:
    print('ERREUR: pattern format_message non trouve')
    # Chercher ce qui existe
    for i, line in enumerate(cc.split('\n')):
        if 'format_message' in line:
            print(f'  L{i+1}: {line.strip()}')
