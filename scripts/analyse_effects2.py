import json, os, struct

PROJECT = r'H:\Code\Ankama Dev\wakfu-optimizer'

with open(os.path.join(PROJECT, 'data', 'extracted', 'all_static_effects.json'), 'r', encoding='utf-8') as f:
    effects_list = json.load(f)

with open(os.path.join(PROJECT, 'data', 'extracted', 'all_spells.json'), 'r', encoding='utf-8') as f:
    all_spells = json.load(f)

with open(os.path.join(PROJECT, 'data', 'extracted', 'action_map.json'), 'r', encoding='utf-8') as f:
    action_map = json.load(f)

# Indexer les effets par m_effectId
eff_by_id = {}
for e in effects_list:
    eid = e.get('m_effectId')
    if eid is not None:
        eff_by_id[eid] = e

print(f'Effets indexes: {len(eff_by_id)}')

spell_by_id = {s['id']: s for s in all_spells}

# Sorts Sram du log avec leurs degats reels
SRAM_SPELLS = {
    4586: {'name': 'Mise a mort',      'real_direct': 20325, 'pa': 6, 'elem': 'Feu'},
    4585: {'name': 'Attaque perfide',   'real_direct': 7365,  'pa': 3, 'elem': 'Eau'},
    4595: {'name': 'Fourberie',         'real_direct': 2239,  'pa': 3, 'elem': 'Air'},
    4604: {'name': 'Double',            'real_direct': 0,     'pa': 2, 'elem': 'Support'},
}

# Actions de degats connues dans Wakfu
DMG_ACTIONS = {
    132: 'HP_LOSS',
    133: 'HP_LOSS_FIRE',
    134: 'HP_LOSS_WATER', 
    135: 'HP_LOSS_EARTH',
    136: 'HP_LOSS_AIR',
    137: 'HP_LOSS_STASIS',
    138: 'HP_LOSS_LIGHT',
    139: 'HP_STEAL',
    140: 'HP_STEAL_FIRE',
    141: 'HP_STEAL_WATER',
    142: 'HP_STEAL_EARTH',
    143: 'HP_STEAL_AIR',
}

print()
print('=== ANALYSE DETAILLEE DES EFFETS ===')
print()

# Analyser TOUS les sorts Sram (breedId 245)
sram_spells = [s for s in all_spells if s.get('breedId') == 245]
print(f'Sorts breedId=245: {len(sram_spells)}')

for s in sorted(sram_spells, key=lambda x: x['id']):
    sid = s['id']
    effect_ids = s.get('effectIds', [])
    pa = s.get('PA_base', '?')
    elem = s.get('element', '?')
    info = SRAM_SPELLS.get(sid, {})
    name = info.get('name', f'Spell_{sid}')

    print(f'  SORT {sid} ({name}) | PA={pa} | Elem={elem} | {len(effect_ids)} effets')

    for eid in effect_ids:
        e = eff_by_id.get(eid)
        if not e:
            print(f'    eff {eid}: NON TROUVE')
            continue

        aid = e.get('m_actionId', '?')
        params = e.get('m_params')
        parent = e.get('m_parentId', '?')
        area = e.get('m_areaShape', '?')
        duration = e.get('m_durationBase', '?')
        conditions = e.get('m_conditionsCriterion', '')

        # Nom de l'action
        action_name = DMG_ACTIONS.get(aid, action_map.get(str(aid), f'action_{aid}'))

        # Decoder les params
        param_str = 'None'
        decoded_values = []
        if params and isinstance(params, list):
            param_str = str(params[:5])
            # Essayer de decoder les floats comme int32 (technique Wakfu)
            for p in params:
                if isinstance(p, (int, float)):
                    try:
                        # Float IEEE 754 -> bytes -> int32
                        raw_bytes = struct.pack('f', float(p))
                        as_int = struct.unpack('i', raw_bytes)[0]
                        decoded_values.append(as_int)
                    except Exception:
                        decoded_values.append(p)

        is_dmg = aid in DMG_ACTIONS
        marker = ' <<< DEGATS' if is_dmg else ''

        print(f'    eff {eid}: actionId={aid} ({action_name}) parent={parent} dur={duration}{marker}')
        if params:
            print(f'      raw_params: {param_str}')
            if decoded_values:
                print(f'      decoded_int: {decoded_values[:5]}')
        if conditions:
            print(f'      conditions: {str(conditions)[:80]}')

    print()

# Stats sur les actionId les plus frequents dans les effets Sram
print()
print('=== ACTIONS FREQUENTES DANS EFFETS SRAM ===')
from collections import Counter
action_counts = Counter()
for s in sram_spells:
    for eid in s.get('effectIds', []):
        e = eff_by_id.get(eid)
        if e:
            action_counts[e.get('m_actionId', '?')] += 1

for aid, count in action_counts.most_common(20):
    name = DMG_ACTIONS.get(aid, action_map.get(str(aid), f'action_{aid}'))
    print(f'  actionId={aid:>5} | {count:3d}x | {name}')
