import pathlib, json

print('=== ETAT MEMOIRE COMPLET ===')
print()

ep = pathlib.Path(r'H:\Code\Ankama Dev\wakfu-optimizer\memory\episodes.jsonl')
if ep.exists() and ep.stat().st_size > 0:
    episodes = [json.loads(l) for l in ep.read_text('utf-8').strip().split('\n') if l.strip()]
    print('EPISODES:', len(episodes))
    for e in episodes:
        status = 'OK' if e['success'] else 'FAIL'
        ts = e['timestamp'][11:19]
        ctx = e['context'][:60]
        tags = e.get('tags', [])
        print('  [' + status + '] ' + ts + ' ' + ctx)
        print('    Tags: ' + str(tags))
else:
    print('EPISODES: 0')

print()

proc = pathlib.Path(r'H:\Code\Ankama Dev\wakfu-optimizer\memory\procedures.json')
if proc.exists():
    procs = json.loads(proc.read_text('utf-8'))
    print('PROCEDURES:', len(procs))
    for name, p in procs.items():
        print('  ' + name + ' (x' + str(p['use_count']) + ')')
else:
    print('PROCEDURES: 0')

print()

sl = pathlib.Path(r'H:\Code\Ankama Dev\wakfu-optimizer\memory\current_session.jsonl')
if sl.exists() and sl.stat().st_size > 0:
    events = [json.loads(l) for l in sl.read_text('utf-8').strip().split('\n') if l.strip()]
    print('SESSION EVENTS:', len(events))
    for ev in events[-5:]:
        t = ev['type']
        ts = ev['time'][11:19]
        msg = ev.get('command', ev.get('message', ''))[:60]
        print('  [' + t + '] ' + ts + ' ' + msg)
else:
    print('SESSION EVENTS: 0')

print()

ml = pathlib.Path(r'H:\Code\Ankama Dev\wakfu-optimizer\logs\memory_manager.log')
if ml.exists():
    lines = ml.read_text('utf-8').strip().split('\n')
    print('MEMORY LOG:', len(lines), 'lignes')
    for l in lines[-8:]:
        print('  ' + l)
else:
    print('MEMORY LOG: absent')
