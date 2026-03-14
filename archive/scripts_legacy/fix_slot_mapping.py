"""
=============================================================
  FIX SLOT MAPPING — Identify correct typeId -> slot assignments
  Problem: Items are equipped in wrong slots (epaulettes in boots, etc.)
  Solution: Cross-reference typeId with item names to build correct map
  Date: 2026-03-14
=============================================================
"""
import os, json, logging
from collections import Counter, defaultdict

PROJECT  = r"H:\Code\Ankama Dev\wakfu-optimizer"
DATA_DIR = os.path.join(PROJECT, "data", "extracted")
LOG_DIR  = os.path.join(PROJECT, "logs")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, "fix_slots.log"), encoding="utf-8"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger("FixSlots")

# Load items
with open(os.path.join(DATA_DIR, "all_items.json"), "r", encoding="utf-8") as f:
    all_items = json.load(f)
log.info(f"Loaded {len(all_items)} items")

# ── PHASE 1: For each typeId, show sample item names ───────
log.info("\n" + "=" * 60)
log.info("PHASE 1: ITEM TYPE IDENTIFICATION")
log.info("=" * 60)

by_type = defaultdict(list)
for item in all_items:
    by_type[item["itemTypeId"]].append(item)

for tid in sorted(by_type.keys()):
    items = by_type[tid]
    # Get 5 sample names at different levels
    items_sorted = sorted(items, key=lambda x: x["level"])
    samples = []
    step = max(1, len(items_sorted) // 5)
    for i in range(0, len(items_sorted), step):
        samples.append(items_sorted[i])
        if len(samples) >= 5:
            break
    
    # Check common name patterns
    names_fr = [i["name_fr"] for i in items[:50]]
    
    # Detect slot by common French keywords in names
    keywords = {
        "Casque": 0, "Coiffe": 0, "Chapeau": 0, "Heaume": 0, "Diadème": 0,
        "Cape": 0, "Manteau": 0, "Cloak": 0,
        "Amulette": 0, "Collier": 0, "Pendentif": 0,
        "Epaulettes": 0, "Epaulière": 0,
        "Plastron": 0, "Armure": 0, "Cuirasse": 0, "Tunique": 0,
        "Ceinture": 0, "Ceinturon": 0,
        "Anneau": 0, "Bague": 0, "Alliance": 0,
        "Bottes": 0, "Chaussure": 0, "Sandales": 0,
        "Epée": 0, "Dague": 0, "Bâton": 0, "Arc": 0, "Hache": 0,
        "Pelle": 0, "Marteau": 0, "Baguette": 0,
        "Bouclier": 0, "Targe": 0,
        "Emblème": 0,
        "Familier": 0, "Mulot": 0, "Chacha": 0,
        "Monture": 0, "Dragoune": 0,
    }
    for name in names_fr:
        for kw in keywords:
            if kw.lower() in name.lower():
                keywords[kw] += 1
    
    top_kw = [(k, v) for k, v in keywords.items() if v > 0]
    top_kw.sort(key=lambda x: -x[1])
    kw_str = ", ".join(f"{k}:{v}" for k, v in top_kw[:5]) if top_kw else "no keyword match"
    
    # Check what stats are most common
    stat_counts = Counter()
    for item in items:
        for eff in item.get("equipEffects", []):
            stat_counts[eff.get("stat", "?")] += 1
    
    has_use = sum(1 for i in items if i.get("useEffects"))
    
    log.info(f"\n  TypeId {tid:>5} — {len(items)} items, levels {items_sorted[0]['level']}-{items_sorted[-1]['level']}")
    log.info(f"    Keywords: {kw_str}")
    log.info(f"    Has useEffects: {has_use}/{len(items)}")
    log.info(f"    Sample names:")
    for s in samples:
        log.info(f"      [{s['rarity_name']:>9}] Lvl {s['level']:>3}: {s['name_fr']}")

# ── PHASE 2: Build the CORRECT slot map ───────────────────
log.info("\n" + "=" * 60)
log.info("PHASE 2: CORRECT SLOT MAPPING")
log.info("=" * 60)

# Based on Wakfu wiki + names analysis, here's the definitive mapping
# We need to verify this against the data
CORRECT_SLOT_MAP = {
    # Armor
    108: "helmet",
    110: "cloak",
    101: "amulet",
    134: "amulet",     # "new" amulets
    114: "epaulettes",
    113: "breastplate",
    120: "breastplate", # "old" breastplate
    115: "belt",
    119: "belt",        # "old" belt
    103: "ring",
    136: "ring",        # "new" ring
    112: "boots",
    138: "boots",       # "new" boots
    # Weapons 1H
    223: "weapon_1h",   # Sword 1H
    133: "weapon_1h",   # Dagger
    480: "weapon_1h",   # Wand
    537: "weapon_1h",   # Pistol
    582: "weapon_1h",   # Cards
    # Weapons 2H
    253: "weapon_2h",   # Greatsword
    254: "weapon_2h",   # Staff
    518: "weapon_2h",   # Shovel
    519: "weapon_2h",   # Hammer
    520: "weapon_2h",   # Bow
    521: "weapon_2h",   # Axe
    522: "weapon_2h",   # Staff 2H
    # Other
    111: "second_hand",
    132: "second_hand", # Shield
    189: "emblem",
    611: "torch",
    646: "tool",
    647: "accessory",
    811: "mount",
    812: "pet",
}

# Verify: check that items match their slot assignment by name keywords
slot_keyword_check = {
    "helmet":      ["casque", "coiffe", "chapeau", "heaume", "diadème", "masque", "tiare"],
    "cloak":       ["cape", "manteau", "voile", "aile"],
    "amulet":      ["amulette", "collier", "pendentif", "talisman", "dora"],
    "epaulettes":  ["epaulette", "épaulière", "spalière"],
    "breastplate": ["plastron", "armure", "cuirasse", "tunique", "torse"],
    "belt":        ["ceinture", "ceinturon", "cordon"],
    "ring":        ["anneau", "bague", "alliance", "croc"],
    "boots":       ["botte", "chaussure", "sandale", "brase", "godasse"],
}

for tid, slot in CORRECT_SLOT_MAP.items():
    if slot not in slot_keyword_check:
        continue
    items = by_type.get(tid, [])
    if not items:
        continue
    kws = slot_keyword_check[slot]
    matches = 0
    for item in items[:30]:
        name_low = item["name_fr"].lower()
        if any(kw in name_low for kw in kws):
            matches += 1
    pct = (matches / min(30, len(items))) * 100
    status = "OK" if pct >= 10 else "CHECK"
    log.info(f"  TypeId {tid:>5} -> {slot:>14}: {pct:.0f}% name match ({matches}/{min(30, len(items))}) [{status}]")

# ── PHASE 3: Identify problem typeIds ─────────────────────
log.info("\n" + "=" * 60)
log.info("PHASE 3: PROBLEM DETECTION")
log.info("=" * 60)

# Check which typeIds are in multiple slot categories
problem_types = []
for tid in sorted(by_type.keys()):
    items = by_type[tid]
    slot = CORRECT_SLOT_MAP.get(tid, "UNKNOWN")
    if slot == "UNKNOWN":
        problem_types.append(tid)
        log.info(f"  TypeId {tid} ({len(items)} items) has NO SLOT ASSIGNMENT")
        for i in items[:3]:
            log.info(f"    {i['name_fr']} (Lvl {i['level']})")

# Show final definitive mapping
log.info("\n" + "=" * 60)
log.info("FINAL SLOT MAP (for engine/equipment.py)")
log.info("=" * 60)
for tid in sorted(CORRECT_SLOT_MAP.keys()):
    slot = CORRECT_SLOT_MAP[tid]
    count = len(by_type.get(tid, []))
    log.info(f"  {tid:>5} -> {slot:>14} ({count:>4} items)")

log.info("\nDONE")
