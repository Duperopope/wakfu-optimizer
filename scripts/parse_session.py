import re, json
from collections import defaultdict

path = r'C:\Users\Smedj\AppData\Roaming\zaap\gamesLogs\wakfu\logs\wakfu_chat.log'
with open(path, 'r', encoding='utf-8', errors='replace') as f:
    lines = f.readlines()

print(f'Total lignes: {len(lines)}')

# ============================================================
# 1) Trouver les sessions de combat (debut/fin)
# ============================================================
sessions = []
current_session = None
for i, line in enumerate(lines):
    if ' lance le sort ' in line and current_session is None:
        # Debut approximatif d'un combat
        ts_match = re.match(r'(\d{2}:\d{2}:\d{2}),(\d+)', line)
        ts = ts_match.group(0) if ts_match else '?'
        current_session = {'start': i, 'start_ts': ts, 'lines': []}
    if current_session is not None:
        current_session['lines'].append(line)
    if 'Combat termin' in line and current_session is not None:
        current_session['end'] = i
        ts_match = re.match(r'(\d{2}:\d{2}:\d{2}),(\d+)', line)
        current_session['end_ts'] = ts_match.group(0) if ts_match else '?'
        sessions.append(current_session)
        current_session = None

print(f'Sessions de combat trouvees: {len(sessions)}')
print()

# ============================================================
# 2) Analyser la derniere session en detail
# ============================================================
if sessions:
    last = sessions[-1]
    print(f'=== DERNIERE SESSION ===')
    print(f'Lignes {last["start"]} -> {last["end"]}')
    print(f'Heure: {last["start_ts"]} -> {last["end_ts"]}')
    print(f'Nombre de lignes: {len(last["lines"])}')
    print()

    # Extraire les buffs de L'Immortel
    print('=== BUFFS / ETATS ACTIFS ===')
    buff_re = re.compile(r"L'Immortel: (.+?) \(\+?(\d+) Niv\.\)")
    pct_re = re.compile(r"L'Immortel: (\d+) % (.+?) \((.+?)\)")
    buffs = {}
    pcts = {}
    for line in last['lines']:
        bm = buff_re.search(line)
        if bm:
            buffs[bm.group(1)] = int(bm.group(2))
        pm = pct_re.search(line)
        if pm:
            pcts[pm.group(2)] = {'val': int(pm.group(1)), 'source': pm.group(3)}

    for name, lvl in sorted(buffs.items()):
        print(f'  {name}: Niv. {lvl}')
    for name, info in sorted(pcts.items()):
        print(f'  {name}: {info["val"]}% (source: {info["source"]})')

    # Sorts lances dans cette session
    print()
    print('=== SORTS LANCES (cette session) ===')
    cast_re = re.compile(r"L'Immortel lance le sort (.+?)(?:\s*\(Critiques?\))?\s*$")
    casts = defaultdict(lambda: {'total': 0, 'crit': 0})
    for line in last['lines']:
        cm = cast_re.search(line)
        if cm:
            spell = cm.group(1).strip()
            casts[spell]['total'] += 1
            if '(Critiques)' in line or '(Critique)' in line:
                casts[spell]['crit'] += 1

    for spell, data in sorted(casts.items(), key=lambda x: -x[1]['total']):
        crit_pct = (data['crit'] / data['total'] * 100) if data['total'] > 0 else 0
        print(f'  {spell:35s} | {data["total"]:3d}x | crit: {data["crit"]}/{data["total"]} ({crit_pct:.0f}%)')

    # Degats dans cette session
    print()
    print('=== DEGATS PAR SORT (cette session) ===')
    current_spell = None
    session_dmg = defaultdict(lambda: {'direct': [], 'dot': [], 'armor': []})
    for line in last['lines']:
        cm = cast_re.search(line)
        if cm:
            current_spell = cm.group(1).strip()
        elif current_spell:
            # Degats
            dm = re.search(r": -([\d ]+) PV\s+\(([^)]+)\)", line)
            if dm and "L'Immortel" not in line:
                val = int(dm.group(1).replace(' ', ''))
                elem = dm.group(2)
                is_dot = 'morragie' in line or 'Rupture' in line
                is_parade = 'Parade' in line
                if is_dot:
                    session_dmg[current_spell]['dot'].append(val)
                else:
                    session_dmg[current_spell]['direct'].append({'dmg': val, 'elem': elem, 'parade': is_parade})
            # Armure
            am = re.search(r": (\d+) Armure", line)
            if am and "L'Immortel" not in line:
                session_dmg[current_spell]['armor'].append(int(am.group(1)))

    for spell, data in sorted(session_dmg.items(), key=lambda x: -(sum(h['dmg'] for h in x[1]['direct']) + sum(x[1]['dot']))):
        d = data['direct']
        if d:
            vals = [h['dmg'] for h in d]
            parades = sum(1 for h in d if h['parade'])
            elem = d[0]['elem']
            print(f'  {spell:30s} | Direct: {len(d):3d} coups | moy={sum(vals)/len(vals):.0f} min={min(vals)} max={max(vals)} | {elem} | parades={parades}')
        if data['dot']:
            avg_dot = sum(data['dot']) / len(data['dot'])
            print(f'  {"":30s} | DOT:    {len(data["dot"]):3d} coups | moy={avg_dot:.0f}')
        if data['armor']:
            avg_a = sum(data['armor']) / len(data['armor'])
            print(f'  {"":30s} | Armure: {len(data["armor"]):3d} coups | moy={avg_a:.0f}')

    # XP de fin
    print()
    print('=== XP ===')
    for line in last['lines']:
        if 'points d' in line and 'XP' in line:
            print(f'  {line.strip()[:120]}')
