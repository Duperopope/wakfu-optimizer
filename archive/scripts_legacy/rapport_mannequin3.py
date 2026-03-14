import re
from collections import OrderedDict

LOG_PATH = r'C:\Users\Smedj\AppData\Roaming\zaap\gamesLogs\wakfu\logs\wakfu_chat.log'
PLAYER = "L'Immortel"

with open(LOG_PATH, 'r', encoding='utf-8', errors='replace') as f:
    raw_lines = f.readlines()

# Normaliser TOUS les espaces Unicode en espaces normaux
def normalize(text):
    # Remplacer narrow no-break space, no-break space, thin space, etc.
    for ch in ['\u202f', '\u00a0', '\u2009', '\u2007', '\u2008']:
        text = text.replace(ch, ' ')
    return text

mannequin = [normalize(line) for line in raw_lines[8447:8531]]

print(f'Lignes: {len(mannequin)}')

# Verifier que la normalisation fonctionne
for line in mannequin[:8]:
    if 'PV' in line and 'combat' in line:
        print(f'  NORM: {repr(line.rstrip()[:100])}')
print()

cast_re = re.compile(
    r"\[Information \(combat\)\] " + re.escape(PLAYER) + r" lance le sort (.+?)(\s*\(Critiques?\))?\s*$"
)
dmg_re = re.compile(
    r"\[Information \(combat\)\] ([^:]+): -([\d ]+) PV\s+\(([^)]+)\)"
)
armor_re = re.compile(
    r"\[Information \(combat\)\] ([^:]+): ([\d ]+) Armure"
)
heal_re = re.compile(
    r"\[Information \(combat\)\] " + re.escape(PLAYER) + r": \+([\d ]+) PV"
)

current_spell = None
current_crit = False
cast_order = []
spell_data = OrderedDict()

def get_data(spell):
    if spell not in spell_data:
        spell_data[spell] = {
            'casts': 0, 'crits': 0,
            'direct': [], 'dot': [], 'armor': [], 'heal': [],
            'elements': set()
        }
    return spell_data[spell]

for line in mannequin:
    cm = cast_re.search(line)
    if cm:
        current_spell = cm.group(1).strip()
        current_crit = bool(cm.group(2))
        d = get_data(current_spell)
        d['casts'] += 1
        if current_crit:
            d['crits'] += 1
        if current_spell not in cast_order:
            cast_order.append(current_spell)
        continue

    if not current_spell:
        continue

    dm = dmg_re.search(line)
    if dm:
        target = dm.group(1).strip()
        if PLAYER in target:
            continue
        val = int(dm.group(2).replace(' ', ''))
        elem = dm.group(3).strip()
        is_dot = 'morragie' in line or 'Rupture violente' in line
        d = get_data(current_spell)
        d['elements'].add(elem)
        if is_dot:
            d['dot'].append({'dmg': val, 'elem': elem})
        else:
            d['direct'].append({'dmg': val, 'elem': elem, 'crit': current_crit})
        continue

    am = armor_re.search(line)
    if am:
        target = am.group(1).strip()
        if PLAYER not in target:
            get_data(current_spell)['armor'].append(int(am.group(2).replace(' ', '')))
        continue

    hm = heal_re.search(line)
    if hm:
        get_data(current_spell)['heal'].append(int(hm.group(1).replace(' ', '')))

# ============================================================
# RAPPORT
# ============================================================
print('=' * 90)
print('  RAPPORT MANNEQUIN KANJEDO - SAC A PATATES (0 resistance)')
print('  Personnage: L\'Immortel (Sram 179)')
print('=' * 90)
print()

grand_direct = 0
grand_dot = 0

for spell in cast_order:
    data = spell_data[spell]
    d = data['direct']
    crit_mark = 'CRIT' if data['crits'] > 0 else 'NORM'
    elems = '/'.join(sorted(data['elements'])) if data['elements'] else '-'

    direct_sum = sum(h['dmg'] for h in d)
    dot_sum = sum(h['dmg'] for h in data['dot'])
    armor_sum = sum(data['armor'])
    heal_sum = sum(data['heal'])
    total_spell = direct_sum + dot_sum

    grand_direct += direct_sum
    grand_dot += dot_sum

    print(f'  [{crit_mark}] {spell}  |  Elem: {elems}  |  Total: {total_spell:,} PV')

    if d:
        for i, h in enumerate(d):
            print(f'      direct {i+1}: -{h["dmg"]:>7,} PV  ({h["elem"]})')

    if data['dot']:
        for i, h in enumerate(data['dot']):
            print(f'      dot    {i+1}: -{h["dmg"]:>7,} PV  ({h["elem"]})')

    if data['armor']:
        print(f'      armure:    {armor_sum:>7,}')

    if data['heal']:
        print(f'      heal:     +{heal_sum:>7,} PV')

    print()

print('=' * 90)
print(f'  TOTAUX:  Direct={grand_direct:,}  DOT={grand_dot:,}  TOTAL={grand_direct+grand_dot:,} PV')
print('=' * 90)
print()

print('  TABLEAU RECAPITULATIF:')
print(f'  {"Sort":30s} | {"Cr":2s} | {"Direct":>8s} | {"DOT":>8s} | {"Total":>8s} | {"Armure":>7s} | {"Elem"}')
print('  ' + '-' * 80)
for spell in cast_order:
    data = spell_data[spell]
    ds = sum(h['dmg'] for h in data['direct'])
    dots = sum(h['dmg'] for h in data['dot'])
    arm = sum(data['armor'])
    elems = '/'.join(sorted(data['elements'])) if data['elements'] else '-'
    cm = 'C' if data['crits'] > 0 else ' '
    print(f'  {spell:30s} | {cm:2s} | {ds:>8,} | {dots:>8,} | {ds+dots:>8,} | {arm:>7,} | {elems}')
print('  ' + '-' * 80)
print(f'  {"TOTAL":30s} |    | {grand_direct:>8,} | {grand_dot:>8,} | {grand_direct+grand_dot:>8,} |')
