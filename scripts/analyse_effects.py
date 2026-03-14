import json, os, sys
sys.path.insert(0, r'H:\Code\Ankama Dev\wakfu-optimizer')

PROJECT = r'H:\Code\Ankama Dev\wakfu-optimizer'

def load_json(name):
    p = os.path.join(PROJECT, 'data', 'extracted', name)
    with open(p, 'r', encoding='utf-8') as f:
        return json.load(f)

all_spells = load_json('all_spells.json')
static_effects = load_json('all_static_effects.json')
action_map = load_json('action_map.json')
breeds = load_json('breeds.json')

spell_by_id = {s['id']: s for s in all_spells}
effect_by_id = {e['id']: e for e in static_effects} if isinstance(static_effects, list) else {}

# Si c'est un dict
if isinstance(static_effects, dict):
    for k, v in static_effects.items():
        if isinstance(v, dict):
            v['id'] = int(k)
            effect_by_id[int(k)] = v
        elif isinstance(v, list):
            for e in v:
                if isinstance(e, dict) and 'id' in e:
                    effect_by_id[e['id']] = e

# Sorts Sram
sram = None
for b in breeds:
    if isinstance(b, dict) and b.get('id') == 4:
        sram = b
        break

sram_ids = sram.get('ehx', []) if sram else []

# Aussi chercher d'autres sorts par breedId
sram_extended = [s for s in all_spells if s.get('breedId') == 245]

# Tous les sorts utilises dans le log
LOG_SPELLS = {
    'Mise a mort': 4586,
    'Attaque perfide': 4585,
    'Fourberie': 4595,
    'Double': 4604,
}

print('=' * 90)
print('  ANALYSE DES EFFETS DE SORTS SRAM')
print('=' * 90)
print()

# Analyser les sorts du log
all_sram_spell_ids = set(sram_ids)
for s in sram_extended:
    all_sram_spell_ids.add(s['id'])

print(f'Sorts Sram trouves: {len(all_sram_spell_ids)}')
print(f'  ehx: {sram_ids}')
print(f'  breedId=245: {[s["id"] for s in sram_extended[:10]]}')
print()

# Pour chaque sort Sram, analyser les effets
print(f'{"ID":>6s} | {"breedId":>7s} | {"PA":>4s} | {"Elem":>4s} | {"Effects":>3s} | Details')
print('-' * 90)

for spell_id in sorted(all_sram_spell_ids):
    s = spell_by_id.get(spell_id)
    if not s:
        continue
    effect_ids = s.get('effectIds', [])
    pa = s.get('PA_base', s.get('pa', '?'))
    elem = s.get('element', '?')
    bid = s.get('breedId', '?')

    print(f'{spell_id:>6d} | {bid:>7s} | {str(pa):>4s} | {elem:>4s} | {len(effect_ids):>3d} |')

    # Analyser chaque effet
    for eid in effect_ids[:8]:
        eff = effect_by_id.get(eid)
        if eff:
            aid = eff.get('actionId', eff.get('action_id', '?'))
            params = eff.get('params', eff.get('fp', []))
            area = eff.get('areaId', '?')
            desc = action_map.get(str(aid), action_map.get(aid, '?'))

            # Chercher les valeurs de degats dans les params
            if isinstance(params, list) and len(params) >= 1:
                param_str = ', '.join(f'{p:.1f}' if isinstance(p, float) else str(p) for p in params[:5])
            elif isinstance(params, dict):
                param_str = str(params)[:60]
            else:
                param_str = str(params)[:60]

            print(f'       eff {eid}: actionId={aid} params=[{param_str}] desc={desc}')
        else:
            print(f'       eff {eid}: NOT FOUND in static_effects')

    print()

# Action map - quelles actions sont liees aux degats?
print()
print('=== ACTION MAP (actions de degats) ===')
dmg_actions = {}
for k, v in action_map.items():
    vl = str(v).lower() if v else ''
    if any(word in vl for word in ['damage', 'degat', 'steal', 'vol', 'hp', 'pv']):
        dmg_actions[k] = v
        print(f'  {k}: {v}')

print(f'\nActions de degats trouvees: {len(dmg_actions)}')
