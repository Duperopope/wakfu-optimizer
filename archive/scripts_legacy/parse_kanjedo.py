import re, json, os, sys
from collections import defaultdict

LOG_PATH = r'C:\Users\Smedj\AppData\Roaming\zaap\gamesLogs\wakfu\logs\wakfu_chat.log'
PLAYER = "L'Immortel"

with open(LOG_PATH, 'r', encoding='utf-8', errors='replace') as f:
    lines = f.readlines()

print(f'Total lignes: {len(lines)}')

# Trouver la DERNIERE session de combat (la plus recente = le mannequin)
sessions = []
current = None
for i, line in enumerate(lines):
    if ' lance le sort ' in line and current is None:
        ts = line[:12]
        current = {'start': i, 'ts': ts, 'lines': []}
    if current is not None:
        current['lines'].append(line)
    if 'Combat termin' in line and current is not None:
        current['end'] = i
        sessions.append(current)
        current = None

print(f'Sessions trouvees: {len(sessions)}')
if not sessions:
    print('Aucune session trouvee !')
    sys.exit(1)

last = sessions[-1]
print(f'Derniere session: lignes {last["start"]}-{last["end"]}, {len(last["lines"])} lignes')
print(f'Heure debut: {last["ts"]}')
print()

# Parser la session
cast_re = re.compile(r"" + re.escape(PLAYER) + r" lance le sort (.+?)(?:\s*\(Critiques?\))?\s*$")
dmg_re = re.compile(r"(.+?): -([\d ]+) PV\s+\(([^)]+)\)")
armor_re = re.compile(r"(.+?): (\d+) Armure")
buff_re = re.compile(r"" + re.escape(PLAYER) + r": (\d+) % (.+?) \((.+?)\)")

current_spell = None
current_crit = False
spell_data = defaultdict(lambda: {
    'casts': 0, 'crits': 0,
    'direct': [], 'dot': [], 'armor': [],
    'elements': set()
})

for line in last['lines']:
    cm = cast_re.search(line)
    if cm:
        current_spell = cm.group(1).strip()
        current_crit = '(Critiques)' in line or '(Critique)' in line
        spell_data[current_spell]['casts'] += 1
        if current_crit:
            spell_data[current_spell]['crits'] += 1
        continue

    if current_spell:
        dm = dmg_re.search(line)
        if dm:
            target = dm.group(1).strip()
            if PLAYER in target:
                continue
            val = int(dm.group(2).replace(' ', ''))
            elem = dm.group(3)
            is_dot = 'morragie' in line or 'Rupture' in line or 'Conducteur' in line
            is_parade = 'Parade' in line
            spell_data[current_spell]['elements'].add(elem)
            if is_dot:
                spell_data[current_spell]['dot'].append(val)
            else:
                spell_data[current_spell]['direct'].append({
                    'dmg': val, 'elem': elem,
                    'parade': is_parade, 'crit': current_crit
                })
            continue

        am = armor_re.search(line)
        if am:
            target = am.group(1).strip()
            if PLAYER not in target:
                spell_data[current_spell]['armor'].append(int(am.group(2)))

# Afficher le rapport
print('=' * 80)
print('  RAPPORT DE DEGATS REELS - SESSION MANNEQUIN KANJEDO')
print('=' * 80)
print()

# Trier par nombre de casts
for spell, data in sorted(spell_data.items(), key=lambda x: -x[1]['casts']):
    d = data['direct']
    crit_pct = f"{data['crits']}/{data['casts']}" if data['casts'] > 0 else '0/0'
    elems = ', '.join(data['elements']) if data['elements'] else '?'

    print(f'  {spell}')
    print(f'    Casts: {data["casts"]}  |  Crits: {crit_pct}  |  Elements: {elems}')

    if d:
        vals = [h['dmg'] for h in d]
        # Separer crits et non-crits
        crit_vals = [h['dmg'] for h in d if h['crit']]
        norm_vals = [h['dmg'] for h in d if not h['crit']]
        parades = sum(1 for h in d if h['parade'])

        print(f'    Direct: {len(d)} coups | moy={sum(vals)/len(vals):.0f} min={min(vals)} max={max(vals)} | parades={parades}')
        if crit_vals:
            print(f'      Crits:  {len(crit_vals)} coups | moy={sum(crit_vals)/len(crit_vals):.0f} min={min(crit_vals)} max={max(crit_vals)}')
        if norm_vals:
            print(f'      Normal: {len(norm_vals)} coups | moy={sum(norm_vals)/len(norm_vals):.0f} min={min(norm_vals)} max={max(norm_vals)}')

    if data['dot']:
        avg_dot = sum(data['dot']) / len(data['dot'])
        print(f'    DOT: {len(data["dot"])} ticks | moy={avg_dot:.0f} min={min(data["dot"])} max={max(data["dot"])}')

    if data['armor']:
        avg_a = sum(data['armor']) / len(data['armor'])
        print(f'    Armure: {len(data["armor"])} | moy={avg_a:.0f}')

    print()

# Lister aussi les 10 premieres lignes brutes pour debug
print('=== 10 PREMIERES LIGNES DE LA SESSION ===')
for line in last['lines'][:10]:
    print(f'  {line.rstrip()[:130]}')

print()
print('=== 10 DERNIERES LIGNES DE LA SESSION ===')
for line in last['lines'][-10:]:
    print(f'  {line.rstrip()[:130]}')
