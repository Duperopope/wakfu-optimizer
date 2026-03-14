"""
Analyse rapide des 4079 spells extraits.
"""
import json, os
from collections import Counter

DATA = r"H:\Code\Ankama Dev\wakfu-optimizer\data\extracted\all_spells.json"

with open(DATA, 'r', encoding='utf-8') as f:
    spells = json.load(f)

print(f"Total spells: {len(spells)}")

# Distribution par breedId
breeds = Counter(s['breedId'] for s in spells)
print(f"\nBreeds ({len(breeds)} uniques):")
for bid, count in sorted(breeds.items()):
    print(f"  breedId={bid:4d}: {count:4d} spells")

# Spells avec effectIds non vides
with_effects = [s for s in spells if s.get('effectIds')]
print(f"\nSpells avec effectIds: {len(with_effects)} / {len(spells)}")

# Distribution par spellType
types = Counter(s['spellType'] for s in spells)
print(f"\nSpell types:")
for t, c in sorted(types.items()):
    print(f"  type={t}: {c} spells")

# Spells avec stringCasts non vides
with_sc = [s for s in spells if s.get('stringCasts')]
print(f"\nSpells avec stringCasts: {len(with_sc)}")

# Spells avec altCastParams
with_alt = [s for s in spells if s.get('altCastParams')]
print(f"Spells avec altCastParams: {len(with_alt)}")

# Spells avec baseCastParams
with_base = [s for s in spells if s.get('baseCastParams')]
print(f"Spells avec baseCastParams: {len(with_base)}")

# Exemple d'un spell PA > 0 par breed
print(f"\nExemple par breed (PA > 0):")
seen = set()
for s in spells:
    bid = s['breedId']
    if bid not in seen and s.get('PA_base', 0) > 0:
        seen.add(bid)
        sc_keys = list(s.get('stringCasts', {}).keys())
        print(f"  breed={bid}: spell {s['id']} PA={s['PA_base']} effects={s['effectIds'][:3]} stringCasts={sc_keys}")
