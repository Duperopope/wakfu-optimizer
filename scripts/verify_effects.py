"""
Verification rapide des static_effects.json et croisement avec les spells
"""
import json
import os
from collections import Counter

DATA = r"H:\Code\Ankama Dev\wakfu-optimizer\data\extracted"

# 1. Load effects
print("Loading static_effects.json...")
epath = os.path.join(DATA, "static_effects.json")
fsize = os.path.getsize(epath)
print(f"  File size: {fsize / 1048576:.1f} MB")

with open(epath, 'r', encoding='utf-8') as f:
    effects = json.load(f)
print(f"  Effects loaded: {len(effects):,}")

# Index by id
eff_by_id = {e['id']: e for e in effects}
print(f"  Unique IDs: {len(eff_by_id):,}")

# 2. Action distribution (top 20)
actions = Counter(e['actionId'] for e in effects)
print(f"\n=== Top 20 actionIds ===")
for aid, cnt in actions.most_common(20):
    print(f"  actionId={aid:>6d}: {cnt:>6d} effects")

# 3. Target effects for Sram spells
target_ids = [174266, 174268, 174270, 178427, 178430, 182653]
print(f"\n=== Sram spell effects ===")
for tid in target_ids:
    e = eff_by_id.get(tid)
    if e:
        print(f"\n  Effect {tid}:")
        print(f"    actionId   = {e['actionId']}")
        print(f"    params     = {e['params']}")
        print(f"    areaShape  = {e['areaShape']}")
        print(f"    areaSize   = {e['areaSize']}")
        print(f"    element    = {e['effectElement']}")
        print(f"    stateId    = {e['stateId']}")
        print(f"    duration   = {e['durationBase']}")
        print(f"    condition  = '{e['condition']}'")
        print(f"    targets    = {e['targets']}")
        print(f"    floatParam = {e['floatParams']}")
        print(f"    critBonus  = {e['critBonus']}")
    else:
        print(f"\n  Effect {tid}: NOT FOUND!")

# 4. Load spells and cross-reference
print(f"\n=== Cross-reference with spells ===")
spath = os.path.join(DATA, "all_spells.json")
with open(spath, 'r', encoding='utf-8') as f:
    spells = json.load(f)
print(f"  Spells loaded: {len(spells):,}")

# Find Sram spells (breedId=4 from breeds.json)
sram_spells = [s for s in spells if s.get('breedId') == 4]
print(f"  Sram spells (breedId=4): {len(sram_spells)}")

# If none, check which breedIds exist and find Sram via spell IDs
if not sram_spells:
    breeds = Counter(s.get('breedId') for s in spells)
    print(f"  BreedId distribution: {dict(breeds.most_common(20))}")
    
    # Load breeds to find Sram breed id mapping
    bpath = os.path.join(DATA, "breeds.json")
    with open(bpath, 'r', encoding='utf-8') as f:
        breed_data = json.load(f)
    
    # Find SRAM entry
    sram_breed = None
    for b in breed_data:
        if b.get('name') == 'SRAM':
            sram_breed = b
            break
    
    if sram_breed:
        print(f"  SRAM breed entry: id={sram_breed['id']}")
        # Get spell IDs from breed
        spell_ids = sram_breed.get('spellIds', sram_breed.get('ehx', []))
        print(f"  SRAM spell IDs from breed: {len(spell_ids)} spells")
        if spell_ids:
            print(f"  First 10: {spell_ids[:10]}")
            
            # Find these spells
            spell_by_id = {s['id']: s for s in spells}
            found = 0
            for sid in spell_ids[:5]:
                sp = spell_by_id.get(sid)
                if sp:
                    found += 1
                    eids = sp.get('effectIds', [])
                    print(f"\n  Spell {sid}: PA={sp.get('PA_base',0)}, effectIds={eids}")
                    for eid in eids[:3]:
                        ef = eff_by_id.get(eid)
                        if ef:
                            print(f"    -> Effect {eid}: action={ef['actionId']}, params={ef['params']}, element={ef['effectElement']}")
            print(f"\n  Found {found}/{min(5, len(spell_ids))} spells in all_spells.json")

# 5. Effect groups cross-reference
print(f"\n=== Effect groups ===")
gpath = os.path.join(DATA, "effect_groups.json")
if os.path.exists(gpath):
    with open(gpath, 'r', encoding='utf-8') as f:
        groups = json.load(f)
    print(f"  Groups loaded: {len(groups):,}")
    
    # Check if spell effectIds are group IDs or direct effect IDs
    sample_spell = spells[1]  # spell 5624 (breed=1, known to work)
    sample_eids = sample_spell.get('effectIds', [])
    print(f"\n  Sample spell {sample_spell['id']}: effectIds={sample_eids}")
    
    grp_by_id = {g['id']: g for g in groups}
    for eid in sample_eids[:3]:
        if eid in grp_by_id:
            grp = grp_by_id[eid]
            print(f"    effectId {eid} -> GROUP with effects: {grp['effects']}")
            for sub_eid in grp['effects']:
                ef = eff_by_id.get(sub_eid)
                if ef:
                    print(f"      -> Effect {sub_eid}: action={ef['actionId']}, params={ef['params']}, element={ef['effectElement']}")
        elif eid in eff_by_id:
            ef = eff_by_id[eid]
            print(f"    effectId {eid} -> DIRECT effect: action={ef['actionId']}, params={ef['params']}")
        else:
            print(f"    effectId {eid} -> NOT FOUND in groups or effects!")

print(f"\nDONE")
