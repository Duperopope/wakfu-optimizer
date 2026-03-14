import re

path = r'C:\Users\Smedj\AppData\Roaming\zaap\gamesLogs\wakfu\logs\wakfu_chat.log'
with open(path, 'r', encoding='utf-8', errors='replace') as f:
    lines = f.readlines()

# Extraire tous les sorts lances par L'Immortel
spell_pattern = re.compile(r" lance le sort (.+?)(?:\s*\(Critiques?\))?\s*$")
player_spells = {}
for line in lines:
    if " lance le sort" in line and ("L'Immortel" in line or "Immortel" in line):
        m = spell_pattern.search(line)
        if m:
            name = m.group(1).strip()
            player_spells[name] = player_spells.get(name, 0) + 1

print('=== SORTS DE L IMMORTEL ===')
for name, count in sorted(player_spells.items(), key=lambda x: -x[1]):
    print(f'  {count:4d}x  {name}')

print(f'\nTotal sorts distincts: {len(player_spells)}')

# Extraire les degats par sort
print('\n=== DEGATS PAR SORT ===')
cast_pattern = re.compile(r"L'Immortel lance le sort (.+?)(?:\s*\(Critiques?\))?\s*$")
dmg_re = re.compile(r": -([\d ]+) PV\s+\(([^)]+)\)")

current_spell = None
spell_damages = {}
for line in lines:
    cm = cast_pattern.search(line)
    if cm:
        current_spell = cm.group(1).strip()
        if current_spell not in spell_damages:
            spell_damages[current_spell] = []
    elif current_spell and 'PV' in line and ': -' in line:
        dm = dmg_re.search(line)
        if dm:
            val = int(dm.group(1).replace(' ', ''))
            elem = dm.group(2)
            is_dot = 'morragie' in line or 'Rupture' in line or 'Conducteur' in line
            spell_damages[current_spell].append({'dmg': val, 'elem': elem, 'dot': is_dot})

for spell, hits in sorted(spell_damages.items(), key=lambda x: -len(x[1])):
    direct = [h for h in hits if not h['dot']]
    dots = [h for h in hits if h['dot']]
    if direct:
        avg_d = sum(h['dmg'] for h in direct) / len(direct)
        min_d = min(h['dmg'] for h in direct)
        max_d = max(h['dmg'] for h in direct)
        elem = direct[0]['elem']
        print(f'  {spell:30s} | {len(direct):3d} coups | moy={avg_d:.0f} min={min_d} max={max_d} | {elem}')
    if dots:
        avg_dot = sum(h['dmg'] for h in dots) / len(dots)
        print(f'  {"":30s} | {len(dots):3d} DOTs  | moy={avg_dot:.0f}')
