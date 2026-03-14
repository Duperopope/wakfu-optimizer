"""
End-to-end test: L'Immortel (Sram) with full State resolution.
"""
import sys
import os
import json

sys.path.insert(0, r"H:\Code\Ankama Dev\wakfu-optimizer")

from engine.fighter import Fighter, StateManager
from engine.damage import calculate_damage
from engine.effect_bridge import (
    SpellExecutor, get_states_index, get_state, get_effects_index,
    ACTION_HANDLERS, get_breeds
)

# ================================================================
# SETUP
# ================================================================
print("=" * 70)
print("END-TO-END TEST: L'Immortel (Sram) + States")
print("=" * 70)

sys.path.insert(0, r"H:\Code\Ankama Dev\wakfu-optimizer\data\profiles")
from limmortel import PROFILE as LIMMORTEL

executor = SpellExecutor()
states_idx = get_states_index()
effects_idx = get_effects_index()
breeds = get_breeds()

# Find Sram breed
sram_breed = None
for b in breeds:
    bid = b.get('breedId', b.get('id', -1))
    if bid in [4, 11]:
        sram_breed = b
        break

# Create fighters
caster = Fighter("L'Immortel", "Team_Sram", profile=LIMMORTEL)

# Dummy profile matching Fighter.__init__ expected format
DUMMY_PROFILE = {
    'name': 'Dummy',
    'class': 'monster',
    'level': 200,
    'hp': 10000,
    'ap': 6,
    'mp': 3,
    'wp': 6,
    'masteries': {},
    'resistances': {
        'fire': 40, 'water': 40, 'earth': 40, 'air': 40,
        'critical': 0, 'rear': 0
    },
    'damage_inflicted': 0,
    'healing_mastery': 0,
    'critical_hit': 0,
    'block': 0,
}
dummy = Fighter("Dummy", "Team_Monsters", profile=DUMMY_PROFILE)

print(f"\n  Caster: {caster.name}")
print(f"    HP={caster.stats.get('hp', '?')}, PA={caster.stats.get('ap', '?')}, "
      f"PM={caster.stats.get('mp', '?')}")
print(f"\n  Target: {dummy.name}")
print(f"    HP={dummy.stats.get('hp', '?')}, Res fire={dummy.stats.get('resistances', {}).get('fire', '?')}%")

# ================================================================
# FIND ALL SRAM SPELLS
# ================================================================
print("\n" + "=" * 70)
print("SRAM SPELLS ANALYSIS")
print("=" * 70)

sram_spell_ids = []
if sram_breed:
    sram_spell_ids = sram_breed.get('spellIds', [])
    print(f"  Breed spells: {sram_spell_ids}")

spells_path = os.path.join(r"H:\Code\Ankama Dev\wakfu-optimizer\data\extracted", "all_spells.json")
with open(spells_path, 'r', encoding='utf-8') as f:
    spells_data = json.load(f)

# Find active Sram spells (apply known Sram states or are breed spells)
sram_known_states = {3114, 3129, 3136, 2956, 1579}
active_sram = []
seen_ids = set()

# From breed
for sid in sram_spell_ids:
    sp = executor.get_spell(sid)
    if sp and sp.get('PA_base', 0) > 0 and sid not in seen_ids:
        active_sram.append(sp)
        seen_ids.add(sid)

# From state references
for sp in spells_data:
    pa = sp.get('PA_base', 0)
    if pa <= 0 or sp['id'] in seen_ids:
        continue
    for eid in sp.get('effectIds', []):
        eff = effects_idx.get(eid)
        if eff and eff.get('actionId') in [304, 20, 306]:
            fp0 = eff.get('floatParams', [])
            if fp0 and int(fp0[0]) in sram_known_states:
                active_sram.append(sp)
                seen_ids.add(sp['id'])
                break

active_sram.sort(key=lambda s: s.get('PA_base', 0))
print(f"\n  Active Sram spells: {len(active_sram)}")

for sp in active_sram:
    pa = sp.get('PA_base', 0)
    eff_names = []
    for eid in sp.get('effectIds', []):
        eff = effects_idx.get(eid)
        if eff:
            aid = eff.get('actionId', -1)
            h = ACTION_HANDLERS.get(aid)
            name = h['name'] if h else f'UNK_{aid}'
            eff_names.append(name)
    print(f"    Spell {sp['id']} (PA={pa}): {', '.join(eff_names)}")

# ================================================================
# CAST SEQUENCE WITH STATE RESOLUTION
# ================================================================
print("\n" + "=" * 70)
print("CAST SEQUENCE (full state chain)")
print("=" * 70)

test_spells = [sp['id'] for sp in active_sram[:8]]
print(f"\n  Casting {len(test_spells)} spells:")

missing_actions = {}
total_damage = 0

for spell_id in test_spells:
    sp = executor.get_spell(spell_id)
    if not sp:
        continue

    pa = sp.get('PA_base', 0)
    print(f"\n  {'='*50}")
    print(f"  Spell {spell_id} (PA={pa})")
    print(f"  {'='*50}")

    contexts = [
        {'is_melee': True, 'is_rear': False, 'is_critical': False, 'resolve_state_effects': True},
        {'is_melee': True, 'is_rear': True, 'is_critical': True, 'resolve_state_effects': True},
    ]
    labels = ['Front/Normal', 'Rear/Crit']

    for ctx, label in zip(contexts, labels):
        results = executor.cast(caster, spell_id, target=dummy, context=dict(ctx))
        spell_dmg = 0

        print(f"\n    [{label}]:")
        for r in results:
            action = r.get('action_name', r.get('action', '?'))

            if 'damage' in r or 'actual_damage' in r:
                dmg = r.get('actual_damage', r.get('damage', 0))
                if isinstance(dmg, (int, float)):
                    spell_dmg += dmg
                print(f"      {action}: {dmg} dmg (id={r.get('effect_id')})")

            elif r.get('action') == 'APPLY_STATE':
                sid = r.get('state_id')
                slvl = r.get('level', 1)
                sdur = r.get('duration', '?')
                sdesc = r.get('state_desc', '')
                scount = r.get('state_effect_count', 0)
                print(f"      APPLY_STATE: state_{sid} (desc='{sdesc}') lvl={slvl} dur={sdur} "
                      f"[{scount} sub-effects]")

                for se in r.get('state_effects', []):
                    se_name = se.get('action_name', se.get('action', '?'))
                    se_dmg = se.get('actual_damage', se.get('damage', ''))
                    se_fp = se.get('fp', [])
                    if isinstance(se_dmg, (int, float)) and se_dmg > 0:
                        print(f"        -> {se_name}: {se_dmg:.1f} dmg (state {sid}, eff {se.get('effect_id')})")
                        spell_dmg += se_dmg
                    elif se_fp:
                        print(f"        -> {se_name}: fp={se_fp[:5]} (state {sid})")
                    else:
                        detail = ''
                        for k in ['mastery', 'amount', 'value', 'hp']:
                            if k in se:
                                detail += f" {k}={se[k]}"
                        print(f"        -> {se_name}{detail} (state {sid}, eff {se.get('effect_id')})")

            elif r.get('action') == 'UNHANDLED':
                aid = r.get('action_id', '?')
                fp = r.get('fp', [])
                missing_actions[aid] = missing_actions.get(aid, 0) + 1
                print(f"      UNHANDLED action {aid}: fp={fp[:5]} (id={r.get('effect_id')})")

            elif r.get('action') == 'ERROR':
                print(f"      ERROR: {r.get('error')} (id={r.get('effect_id')})")

            else:
                detail = ''
                for k in ['mastery', 'amount', 'value', 'state_id', 'hp']:
                    if k in r:
                        detail += f" {k}={r[k]}"
                print(f"      {action}{detail} (id={r.get('effect_id')})")

        total_damage += spell_dmg
        if spell_dmg > 0:
            eff_str = f" ({spell_dmg/pa:.0f}/PA)" if pa > 0 else ""
            print(f"    => Total damage [{label}]: {spell_dmg:.1f}{eff_str}")

# ================================================================
# TARGET STATE SUMMARY
# ================================================================
print("\n" + "=" * 70)
print("TARGET STATES AFTER ALL CASTS")
print("=" * 70)

active = dummy.states.list_states()
if active:
    for name, info in sorted(active.items()):
        sid_str = name.replace('state_', '')
        state_data = states_idx.get(int(sid_str)) if sid_str.isdigit() else None
        desc = state_data.get('description', '') if state_data else ''
        eff_count = len(state_data.get('effectIds', [])) if state_data else 0
        print(f"  {name}: lvl={info['level']}, dur={info['duration']}, "
              f"desc='{desc}', sub_effects={eff_count}")
else:
    print("  No active states")

# ================================================================
# MISSING HANDLERS
# ================================================================
print("\n" + "=" * 70)
print("MISSING HANDLERS (from Sram casts)")
print("=" * 70)

if missing_actions:
    for aid, count in sorted(missing_actions.items(), key=lambda x: -x[1]):
        example_fp = []
        for eid, eff in effects_idx.items():
            if eff.get('actionId') == aid:
                example_fp = eff.get('floatParams', [])[:6]
                break
        print(f"  Action {aid}: {count}x, example fp={example_fp}")
else:
    print("  All actions handled!")

# ================================================================
# SRAM STATE TREE
# ================================================================
print("\n" + "=" * 70)
print("SRAM STATE TREE")
print("=" * 70)

sram_state_ids = set()
for sp in active_sram:
    for eid in sp.get('effectIds', []):
        eff = effects_idx.get(eid)
        if eff and eff.get('actionId') in [304, 20, 306]:
            fp0 = eff.get('floatParams', [])
            if fp0:
                sram_state_ids.add(int(fp0[0]))

for sid in sram_spell_ids:
    sp = executor.get_spell(sid)
    if sp:
        for eid in sp.get('effectIds', []):
            eff = effects_idx.get(eid)
            if eff and eff.get('actionId') in [304, 20, 306]:
                fp0 = eff.get('floatParams', [])
                if fp0:
                    sram_state_ids.add(int(fp0[0]))

print(f"\n  Sram-related states: {len(sram_state_ids)}")
for sid in sorted(sram_state_ids):
    state = states_idx.get(sid)
    if not state:
        print(f"\n  State {sid}: NOT FOUND")
        continue

    desc = state.get('description', str(sid))
    dur = state.get('durationParams', [])
    stype = state.get('stateType', '?')
    eff_ids = state.get('effectIds', [])

    print(f"\n  State {sid} (type={stype}, desc='{desc}', dur={dur}):")
    for eid in eff_ids:
        eff = effects_idx.get(eid)
        if eff:
            aid = eff.get('actionId', -1)
            h = ACTION_HANDLERS.get(aid)
            name = h['name'] if h else f'UNK_{aid}'
            fp = eff.get('floatParams', [])[:5]
            print(f"    [{eid}] {name} fp={fp}")
        else:
            print(f"    [{eid}] MISSING")

# ================================================================
# DAMAGE TABLE
# ================================================================
print("\n" + "=" * 70)
print("DAMAGE TABLE (L'Immortel vs 40% res)")
print("=" * 70)

stats = LIMMORTEL
scenarios = [
    ('Fire Melee Front',     'fire',  True, False, False),
    ('Fire Melee Crit',      'fire',  True, False, True),
    ('Fire Melee Rear',      'fire',  True, True,  False),
    ('Fire Melee Rear+Crit', 'fire',  True, True,  True),
    ('Water Melee Front',    'water', True, False, False),
    ('Air Melee Front',      'air',   True, False, False),
]

print(f"\n  {'Scenario':<25s} {'Base 20':>10s} {'Base 50':>10s} {'Base 100':>10s}")
print(f"  {'-'*25} {'-'*10} {'-'*10} {'-'*10}")

for label, element, melee, rear, crit in scenarios:
    row = []
    for base in [20, 50, 100]:
        try:
            dmg = calculate_damage(
                base_damage=base, stats=stats, element=element,
                target_elemental_res=40, is_melee=melee,
                is_rear=rear, is_critical=crit,
            )
            final = dmg if isinstance(dmg, (int, float)) else dmg.get('final_damage', dmg.get('damage', 0))
            row.append(final)
        except Exception as e:
            row.append(f"ERR")
    print(f"  {label:<25s} {str(row[0]):>10s} {str(row[1]):>10s} {str(row[2]):>10s}")

print("\n" + "=" * 70)
print("END-TO-END TEST COMPLETE")
print("=" * 70)
