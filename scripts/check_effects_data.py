"""
Verifier le contenu des fichiers effects/states deja extraits.
Determiner s'ils sont exploitables ou s'il faut les re-parser.
"""
import json, os

DATA = r"H:\Code\Ankama Dev\wakfu-optimizer\data\extracted"
RAW = r"H:\Code\Ankama Dev\wakfu-optimizer\data\raw"
PARSED = r"H:\Code\Ankama Dev\wakfu-optimizer\data\parsed"

# 1. all_states.json (5984 entries)
print("=" * 60)
print("1. STATES (all_states.json)")
print("=" * 60)
fpath = os.path.join(DATA, "all_states.json")
with open(fpath, 'r', encoding='utf-8') as f:
    states = json.load(f)
print(f"  Count: {len(states)}")
if states:
    print(f"  Keys: {list(states[0].keys())}")
    # Chercher des states connus: Hemorrhagie, Invisible, Isole
    for s in states:
        sid = s.get('m_id', 0)
        if sid in [132, 133, 26, 702, 584, 585]:  # IDs communs
            print(f"  State {sid}: {s}")

# 2. actions.json (du CDN)
print(f"\n{'='*60}")
print("2. ACTIONS (data/raw/actions.json)")
print("=" * 60)
fpath = os.path.join(RAW, "actions.json")
if os.path.exists(fpath):
    with open(fpath, 'r', encoding='utf-8') as f:
        actions = json.load(f)
    if isinstance(actions, list):
        print(f"  Count: {len(actions)}")
        if actions:
            print(f"  Keys: {list(actions[0].keys())[:10]}")
            for a in actions[:3]:
                print(f"  Example: {json.dumps(a, ensure_ascii=False)[:200]}")
    elif isinstance(actions, dict):
        print(f"  Keys: {len(actions)}")
        for k in list(actions.keys())[:5]:
            v = actions[k]
            print(f"  [{k}]: {json.dumps(v, ensure_ascii=False)[:200]}")

# 3. action_map.json (parsed)
print(f"\n{'='*60}")
print("3. ACTION MAP (data/parsed/action_map.json)")
print("=" * 60)
fpath = os.path.join(PARSED, "action_map.json")
if os.path.exists(fpath):
    with open(fpath, 'r', encoding='utf-8') as f:
        amap = json.load(f)
    print(f"  Entries: {len(amap)}")
    for k in list(amap.keys())[:10]:
        print(f"  [{k}]: {json.dumps(amap[k], ensure_ascii=False)[:150]}")

# 4. state_map.json (parsed)
print(f"\n{'='*60}")
print("4. STATE MAP (data/parsed/state_map.json)")
print("=" * 60)
fpath = os.path.join(PARSED, "state_map.json")
if os.path.exists(fpath):
    with open(fpath, 'r', encoding='utf-8') as f:
        smap = json.load(f)
    print(f"  Entries: {len(smap)}")
    for k in list(smap.keys())[:10]:
        print(f"  [{k}]: {json.dumps(smap[k], ensure_ascii=False)[:150]}")

# 5. all_effect_groups.json - trop gros, juste les premiers bytes
print(f"\n{'='*60}")
print("5. EFFECT GROUPS (all_effect_groups.json - 1.1 GB)")
print("=" * 60)
fpath = os.path.join(DATA, "all_effect_groups.json")
if os.path.exists(fpath):
    sz = os.path.getsize(fpath)
    print(f"  Size: {sz:,} bytes ({sz/1024/1024:.0f} MB)")
    # Lire juste le debut
    with open(fpath, 'r', encoding='utf-8') as f:
        chunk = f.read(5000)
    print(f"  First 2000 chars:")
    print(f"  {chunk[:2000]}")

# 6. all_static_effects.json
print(f"\n{'='*60}")
print("6. STATIC EFFECTS (all_static_effects.json - 261 MB)")
print("=" * 60)
fpath = os.path.join(DATA, "all_static_effects.json")
if os.path.exists(fpath):
    sz = os.path.getsize(fpath)
    print(f"  Size: {sz:,} bytes ({sz/1024/1024:.0f} MB)")
    with open(fpath, 'r', encoding='utf-8') as f:
        chunk = f.read(5000)
    print(f"  First 2000 chars:")
    print(f"  {chunk[:2000]}")

# 7. Spells - verifier les effectIds pour les sorts Sram connus
print(f"\n{'='*60}")
print("7. SPELLS SRAM (breedId=1 dans les spells)")
print("=" * 60)
fpath = os.path.join(DATA, "all_spells.json")
with open(fpath, 'r', encoding='utf-8') as f:
    spells = json.load(f)
# On sait que breedId dans les spells n est pas le meme que breed.id
# Cherchons les spells avec breed=1 (142 spells)
breed1 = [s for s in spells if s.get('breedId') == 1]
print(f"  breedId=1: {len(breed1)} spells")
for s in breed1[:10]:
    print(f"    Spell {s['id']}: PA={s.get('PA_base',0)} effects={s.get('effectIds',[])} cast={s.get('castCriterion','')}")

# Aussi regarder les spells avec des stringCasts mentionnant SRAM
sram_mentions = [s for s in spells if 'SRAM' in str(s.get('stringCasts', {}))]
print(f"\n  Spells mentionnant SRAM dans stringCasts: {len(sram_mentions)}")
for s in sram_mentions[:5]:
    keys = list(s.get('stringCasts', {}).keys())
    print(f"    Spell {s['id']}: breed={s['breedId']} PA={s.get('PA_base',0)} stringCasts={keys}")
