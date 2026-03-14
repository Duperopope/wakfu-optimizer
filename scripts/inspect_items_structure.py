"""
=============================================================
  INSPECT CDN ITEMS.JSON STRUCTURE
  Find: rarity field path, name/title field path, item types
  Date: 2026-03-14
=============================================================
"""
import os, json, logging

PROJECT  = r"H:\Code\Ankama Dev\wakfu-optimizer"
CDN_DIR  = os.path.join(PROJECT, "data", "cdn")
DATA_DIR = os.path.join(PROJECT, "data", "extracted")
LOG_DIR  = os.path.join(PROJECT, "logs")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, "inspect_items.log"), encoding="utf-8"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger("InspectItems")

# ── Load cached items.json ─────────────────────────────────
cdn_files = [f for f in os.listdir(CDN_DIR) if f.endswith("_items.json")]
cdn_files.sort(key=lambda x: os.path.getmtime(os.path.join(CDN_DIR, x)), reverse=True)

if not cdn_files:
    log.error("No cached items.json found in CDN dir")
    exit(1)

items_path = os.path.join(CDN_DIR, cdn_files[0])
log.info(f"Loading {items_path}")

with open(items_path, "r", encoding="utf-8") as f:
    raw_items = json.load(f)

log.info(f"Total raw items: {len(raw_items)}")

# ══════════════════════════════════════════════════════════
# PHASE 1: Dump the FULL structure of 3 items (low, mid, high level)
# ══════════════════════════════════════════════════════════
log.info("\n" + "=" * 60)
log.info("PHASE 1: RAW STRUCTURE OF SAMPLE ITEMS")
log.info("=" * 60)

def find_item_by_approx_level(items, target_level):
    """Find an item close to target level that has equipEffects."""
    best = None
    best_diff = 999
    for it in items:
        defn = it.get("definition", {})
        item = defn.get("item", {})
        level = item.get("level", 0)
        effects = defn.get("equipEffects", [])
        if effects and abs(level - target_level) < best_diff:
            best = it
            best_diff = abs(level - target_level)
    return best

# Find items at different levels
for target in [15, 109, 179]:
    item = find_item_by_approx_level(raw_items, target)
    if item:
        defn = item.get("definition", {})
        item_data = defn.get("item", {})
        log.info(f"\n--- Item near level {target} (actual: {item_data.get('level')}) ---")
        log.info(f"TOP-LEVEL KEYS: {list(item.keys())}")
        log.info(f"  definition KEYS: {list(defn.keys())}")
        log.info(f"  definition.item KEYS: {list(item_data.keys())}")
        
        bp = item_data.get("baseParameters", {})
        log.info(f"  definition.item.baseParameters KEYS: {list(bp.keys())}")
        
        # Dump full JSON of this item (truncated for readability)
        full_json = json.dumps(item, ensure_ascii=False, indent=2)
        # Limit to 3000 chars
        if len(full_json) > 3000:
            log.info(f"  FULL JSON (first 3000 chars):\n{full_json[:3000]}\n  ... (truncated)")
        else:
            log.info(f"  FULL JSON:\n{full_json}")

# ══════════════════════════════════════════════════════════
# PHASE 2: Find where rarity lives
# ══════════════════════════════════════════════════════════
log.info("\n" + "=" * 60)
log.info("PHASE 2: RARITY DETECTION")
log.info("=" * 60)

def deep_search(obj, target_key, path=""):
    """Recursively search for a key in nested dicts/lists."""
    results = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            current = f"{path}.{k}" if path else k
            if k.lower() == target_key.lower():
                results.append((current, v))
            results.extend(deep_search(v, target_key, current))
    elif isinstance(obj, list):
        for i, v in enumerate(obj[:3]):  # only first 3 elements
            current = f"{path}[{i}]"
            results.extend(deep_search(v, target_key, current))
    return results

# Search for "rarity" in first 20 items
rarity_paths = set()
for it in raw_items[:20]:
    found = deep_search(it, "rarity")
    for path, val in found:
        rarity_paths.add((path, val))

if rarity_paths:
    log.info("Found 'rarity' at these paths:")
    for path, val in sorted(rarity_paths):
        log.info(f"  {path} = {val}")
else:
    log.info("'rarity' NOT found anywhere! Searching for similar keys...")
    # Search for any key containing 'rar' or 'quality' or 'grade'
    for search_term in ["rar", "quality", "grade", "tier", "colour", "color"]:
        for it in raw_items[:5]:
            for path, val in deep_search(it, search_term):
                log.info(f"  Found '{search_term}': {path} = {val}")

# ══════════════════════════════════════════════════════════
# PHASE 3: Find where title/name lives
# ══════════════════════════════════════════════════════════
log.info("\n" + "=" * 60)
log.info("PHASE 3: TITLE / NAME DETECTION")
log.info("=" * 60)

name_paths = set()
for search_term in ["title", "name", "label"]:
    for it in raw_items[:10]:
        found = deep_search(it, search_term)
        for path, val in found:
            preview = str(val)[:80] if val else "None"
            name_paths.add((search_term, path, preview))

if name_paths:
    log.info("Found name-related fields:")
    for term, path, val in sorted(name_paths):
        log.info(f"  [{term}] {path} = {val}")
else:
    log.info("No title/name found in item structure")

# ══════════════════════════════════════════════════════════
# PHASE 4: Unique itemTypeIds and their frequency
# ══════════════════════════════════════════════════════════
log.info("\n" + "=" * 60)
log.info("PHASE 4: ITEM TYPES")
log.info("=" * 60)

type_counts = {}
for it in raw_items:
    defn = it.get("definition", {})
    item = defn.get("item", {})
    bp = item.get("baseParameters", {})
    tid = bp.get("itemTypeId", -1)
    type_counts[tid] = type_counts.get(tid, 0) + 1

log.info(f"Unique itemTypeIds: {len(type_counts)}")
for tid, count in sorted(type_counts.items(), key=lambda x: -x[1])[:30]:
    log.info(f"  TypeId {tid:>5}: {count:>5} items")

# ══════════════════════════════════════════════════════════
# PHASE 5: Check distribution of a few int fields for rarity clues
# ══════════════════════════════════════════════════════════
log.info("\n" + "=" * 60)
log.info("PHASE 5: INT FIELD DISTRIBUTIONS (rarity clue)")
log.info("=" * 60)

# Check all int-valued fields in item.baseParameters and item itself
sample_item = raw_items[0].get("definition", {}).get("item", {})
for field_name, field_val in sample_item.items():
    if isinstance(field_val, int) and field_name not in ("id", "level"):
        dist = {}
        for it in raw_items:
            v = it.get("definition", {}).get("item", {}).get(field_name, None)
            if v is not None:
                dist[v] = dist.get(v, 0) + 1
        if 2 <= len(dist) <= 15:  # Likely an enum-like field
            log.info(f"\n  Field '{field_name}' distribution ({len(dist)} values):")
            for v, c in sorted(dist.items(), key=lambda x: -x[1]):
                log.info(f"    {v}: {c}")

log.info("\nDONE")
