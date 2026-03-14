"""
=============================================================
  WAKFU ITEMS PARSER v2 — FIXED RARITY + NAMES
  Source: https://wakfu.cdn.ankama.com/gamedata/
  Ref: https://dev.to/heymarkkop/decoding-wakfu-s-action-effects-with-javascript-1nm2
  Fix: rarity from definition.item.baseParameters.rarity
  Fix: names from title.fr / title.en
  Date: 2026-03-14
=============================================================
"""
import os, json, logging
from collections import Counter

PROJECT  = r"H:\Code\Ankama Dev\wakfu-optimizer"
CDN_DIR  = os.path.join(PROJECT, "data", "cdn")
DATA_DIR = os.path.join(PROJECT, "data", "extracted")
LOG_DIR  = os.path.join(PROJECT, "logs")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, "rebuild_items.log"), encoding="utf-8"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger("RebuildItems")

# ── Constants ──────────────────────────────────────────────
RARITY_MAP = {
    0: "Common",
    1: "Unusual",
    2: "Rare",
    3: "Mythical",
    4: "Legendary",
    5: "Relic",
    6: "Souvenir",
    7: "Epic"
}

ITEM_TYPE_MAP = {
    101: "Amulette",
    103: "Anneau",
    108: "Casque",
    110: "Cape",
    111: "Seconde Main",
    112: "Bottes",
    113: "Plastron",
    114: "Epaulettes",
    115: "Ceinture",
    117: "Brassards",
    119: "Ceinture (old)",
    120: "Plastron (old)",
    132: "Bouclier",
    133: "Dague",
    134: "Amulette (new)",
    136: "Anneau (new)",
    138: "Bottes (new)",
    189: "Embleme",
    223: "Epee 1M",
    253: "Epee 2M",
    254: "Baton",
    480: "Baguette",
    537: "Pistolet",
    582: "Cartes",
    611: "Torches",
    646: "Outils",
    647: "Accessoire",
    811: "Monture",
    812: "Familier"
}

# ── Load action map ────────────────────────────────────────
action_path = os.path.join(DATA_DIR, "action_map.json")
with open(action_path, "r", encoding="utf-8") as f:
    action_map = json.load(f)
log.info(f"Loaded {len(action_map)} actions")

# ── Stat name simplifier ──────────────────────────────────
STAT_NAMES = {
    20: "HP", 21: "-HP",
    31: "AP", 41: "MP", 56: "-AP", 57: "-MP",
    71: "Rear Resistance", 80: "Elemental Resistance",
    82: "Fire Resistance", 83: "Water Resistance",
    84: "Earth Resistance", 85: "Air Resistance",
    90: "-Elemental Resistance",
    96: "-Earth Resistance", 97: "-Fire Resistance",
    98: "-Water Resistance", 100: "-Elemental Resistance",
    120: "Elemental Mastery",
    122: "Fire Mastery", 123: "Earth Mastery",
    124: "Water Mastery", 125: "Air Mastery",
    130: "-Elemental Mastery",
    149: "Critical Mastery", 150: "Critical Hit",
    160: "Range", 161: "-Range",
    162: "Prospecting", 166: "Wisdom",
    168: "-Critical Hit",
    171: "Initiative", 172: "-Initiative",
    173: "Lock", 174: "-Lock",
    175: "Dodge", 176: "-Dodge",
    177: "Force of Will",
    180: "Rear Mastery", 181: "-Rear Mastery",
    191: "WP", 192: "-WP", 193: "WP",
    875: "Block", 876: "-Block",
    988: "Critical Resistance",
    1052: "Melee Mastery", 1053: "Distance Mastery",
    1055: "Berserk Mastery",
    1056: "-Critical Mastery",
    1059: "-Melee Mastery", 1060: "-Distance Mastery",
    1061: "-Berserk Mastery",
    1062: "-Critical Resistance", 1063: "-Rear Resistance",
    1068: "Random Elemental Mastery",
    1069: "Random Elemental Resistance"
}

def parse_effect(eff_data, item_level):
    """Parse one equipment effect entry."""
    defn = eff_data.get("effect", {}).get("definition", {})
    action_id = defn.get("actionId", 0)
    params = defn.get("params", [])

    values = []
    for i in range(0, len(params), 2):
        base = params[i] if i < len(params) else 0
        scaling = params[i + 1] if i + 1 < len(params) else 0
        values.append(round(base + scaling * item_level, 1))

    stat_name = STAT_NAMES.get(action_id, "")
    if not stat_name:
        info = action_map.get(str(action_id), {})
        stat_name = info.get("effect", f"action_{action_id}")

    # For random mastery/res (1068/1069), second value = nb elements
    nb_elements = None
    if action_id in (1068, 1069) and len(values) >= 2:
        nb_elements = int(values[1])

    return {
        "actionId": action_id,
        "stat": stat_name,
        "value": values[0] if values else 0,
        "nb_elements": nb_elements,
        "params_raw": params
    }

# ── Load raw CDN items ─────────────────────────────────────
cdn_files = sorted(
    [f for f in os.listdir(CDN_DIR) if f.endswith("_items.json")],
    key=lambda x: os.path.getmtime(os.path.join(CDN_DIR, x)),
    reverse=True
)
items_path = os.path.join(CDN_DIR, cdn_files[0])
log.info(f"Loading {items_path}")
with open(items_path, "r", encoding="utf-8") as f:
    raw_items = json.load(f)
log.info(f"Raw items: {len(raw_items)}")

# ── Parse all items ────────────────────────────────────────
all_items = []
for entry in raw_items:
    defn = entry.get("definition", {})
    item = defn.get("item", {})
    bp = item.get("baseParameters", {})
    title = entry.get("title", {})

    item_id = item.get("id", 0)
    level = item.get("level", 0)
    rarity = bp.get("rarity", 0)
    item_type_id = bp.get("itemTypeId", 0)
    item_set_id = bp.get("itemSetId", 0)

    equip_effects = [parse_effect(e, level) for e in defn.get("equipEffects", [])]
    use_effects = [parse_effect(e, level) for e in defn.get("useEffects", [])]

    # Build compact stats dict
    stats = {}
    for eff in equip_effects:
        key = eff["stat"]
        if eff["nb_elements"] is not None:
            key = f"{key} ({eff['nb_elements']}elem)"
        if key and eff["value"] != 0:
            stats[key] = eff["value"]

    parsed = {
        "id": item_id,
        "name_fr": title.get("fr", f"Item_{item_id}"),
        "name_en": title.get("en", title.get("fr", f"Item_{item_id}")),
        "level": level,
        "rarity": rarity,
        "rarity_name": RARITY_MAP.get(rarity, f"Unknown({rarity})"),
        "itemTypeId": item_type_id,
        "item_type": ITEM_TYPE_MAP.get(item_type_id, f"Type_{item_type_id}"),
        "itemSetId": item_set_id,
        "equipEffects": equip_effects,
        "useEffects": use_effects,
        "stats": stats
    }
    all_items.append(parsed)

log.info(f"Parsed {len(all_items)} items")

# ── Statistics ─────────────────────────────────────────────
log.info("\n--- BY RARITY ---")
rarity_counter = Counter(i["rarity"] for i in all_items)
for r in sorted(rarity_counter.keys()):
    log.info(f"  {RARITY_MAP.get(r, '?'):>12} (r={r}): {rarity_counter[r]:>5}")

log.info("\n--- BY ITEM TYPE (top 20) ---")
type_counter = Counter(i["item_type"] for i in all_items)
for typ, cnt in type_counter.most_common(20):
    log.info(f"  {typ:>25}: {cnt:>5}")

log.info("\n--- BY LEVEL RANGE ---")
ranges = [(1,50),(51,100),(101,150),(151,200),(201,245)]
for lo, hi in ranges:
    cnt = sum(1 for i in all_items if lo <= i["level"] <= hi)
    log.info(f"  Lvl {lo:>3}-{hi:>3}: {cnt:>5}")

# ── Sample: Sram-relevant high-level items ─────────────────
log.info("\n--- SAMPLE: Level 170-185 items, Rarity >= 4 (Legendary+) ---")
sram_range = [i for i in all_items if 170 <= i["level"] <= 185 and i["rarity"] >= 4]
sram_range.sort(key=lambda x: (-x["rarity"], -x["level"]))
for item in sram_range[:15]:
    log.info(f"\n  [{item['rarity_name']}] {item['name_fr']} (ID:{item['id']}, Lvl:{item['level']}, {item['item_type']})")
    for stat, val in item["stats"].items():
        log.info(f"    {stat}: {val}")

# ── Sample: Daggers for Sram ───────────────────────────────
log.info("\n--- DAGGERS (Sram weapons) Level 150+ ---")
daggers = [i for i in all_items if i["itemTypeId"] == 133 and i["level"] >= 150]
daggers.sort(key=lambda x: (-x["rarity"], -x["level"]))
for item in daggers[:10]:
    log.info(f"\n  [{item['rarity_name']}] {item['name_fr']} (ID:{item['id']}, Lvl:{item['level']})")
    for stat, val in item["stats"].items():
        log.info(f"    {stat}: {val}")

# ── Save ───────────────────────────────────────────────────
output_path = os.path.join(DATA_DIR, "all_items.json")
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(all_items, f, ensure_ascii=False)
size_mb = os.path.getsize(output_path) / (1024*1024)
log.info(f"\nSaved {len(all_items)} items to {output_path} ({size_mb:.1f} MB)")

# Also save a lightweight index for fast lookups
index = {}
for item in all_items:
    index[item["id"]] = {
        "name_fr": item["name_fr"],
        "level": item["level"],
        "rarity": item["rarity"],
        "type": item["item_type"],
        "stats": item["stats"]
    }
index_path = os.path.join(DATA_DIR, "items_index.json")
with open(index_path, "w", encoding="utf-8") as f:
    json.dump(index, f, ensure_ascii=False)
size_kb = os.path.getsize(index_path) / 1024
log.info(f"Saved items index to {index_path} ({size_kb:.0f} KB)")

log.info("\n" + "=" * 60)
log.info("SUMMARY")
log.info("=" * 60)
log.info(f"Total items:    {len(all_items)}")
log.info(f"With stats:     {sum(1 for i in all_items if i['stats'])}")
log.info(f"Unique types:   {len(type_counter)}")
log.info(f"Rarity range:   {min(rarity_counter.keys())} - {max(rarity_counter.keys())}")
log.info(f"Level range:    {min(i['level'] for i in all_items)} - {max(i['level'] for i in all_items)}")
log.info(f"\nFiles:")
log.info(f"  {output_path} ({size_mb:.1f} MB)")
log.info(f"  {index_path} ({size_kb:.0f} KB)")
log.info("DONE")
