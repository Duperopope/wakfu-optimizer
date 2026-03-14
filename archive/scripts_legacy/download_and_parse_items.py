"""
=============================================================
  WAKFU ITEMS PARSER — CDN JSON + BDATA CROSS-REFERENCE
  Date: 2026-03-14
  Source: https://wakfu.cdn.ankama.com/gamedata/1.91.1.53/
  Ref: https://dev.to/heymarkkop/decoding-wakfu-s-action-effects-with-javascript-1nm2
  Ref: https://github.com/CharlyRien/wakfu-autobuilder
=============================================================
"""
import os, sys, json, urllib.request, time, logging
from datetime import datetime

# ── Paths ──────────────────────────────────────────────────
PROJECT    = r"H:\Code\Ankama Dev\wakfu-optimizer"
DATA_DIR   = os.path.join(PROJECT, "data", "extracted")
CDN_DIR    = os.path.join(PROJECT, "data", "cdn")
LOG_DIR    = os.path.join(PROJECT, "logs")
BDATA_DIR  = r"H:\Games\Wakfu\contents\bdata"

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(CDN_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

# ── Logging ────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, "items_parser.log"), encoding="utf-8"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger("ItemsParser")

# ── CDN Config ─────────────────────────────────────────────
CDN_BASE = "https://wakfu.cdn.ankama.com/gamedata"
CONFIG_URL = f"{CDN_BASE}/config.json"

def get_version():
    """Fetch the current game data version from Ankama CDN."""
    log.info(f"Fetching version from {CONFIG_URL}")
    req = urllib.request.Request(CONFIG_URL, headers={"User-Agent": "WakfuOptimizer/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    version = data.get("version", "unknown")
    log.info(f"Current game version: {version}")
    return version

def download_json(version, filename):
    """Download a JSON file from the Wakfu CDN and cache it locally."""
    url = f"{CDN_BASE}/{version}/{filename}"
    local_path = os.path.join(CDN_DIR, f"{version}_{filename}")
    
    # Use cache if file exists and is less than 24h old
    if os.path.exists(local_path):
        age_hours = (time.time() - os.path.getmtime(local_path)) / 3600
        if age_hours < 24:
            log.info(f"Using cached {filename} (age: {age_hours:.1f}h)")
            with open(local_path, "r", encoding="utf-8") as f:
                return json.load(f)
        log.info(f"Cache expired for {filename}, re-downloading")
    
    log.info(f"Downloading {url} ...")
    req = urllib.request.Request(url, headers={"User-Agent": "WakfuOptimizer/1.0"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        raw = resp.read()
    
    size_mb = len(raw) / (1024 * 1024)
    log.info(f"Downloaded {filename}: {size_mb:.1f} MB")
    
    # Save cache
    with open(local_path, "wb") as f:
        f.write(raw)
    
    return json.loads(raw.decode("utf-8"))

def build_action_map(actions_data):
    """Build a mapping of actionId -> human-readable stat name."""
    action_map = {}
    for entry in actions_data:
        defn = entry.get("definition", {})
        aid = defn.get("id")
        effect = defn.get("effect", "")
        desc_en = entry.get("description", {}).get("en", "")
        desc_fr = entry.get("description", {}).get("fr", "")
        if aid is not None:
            action_map[aid] = {
                "effect": effect,
                "desc_en": desc_en,
                "desc_fr": desc_fr
            }
    return action_map

def parse_equip_effect(effect_data, action_map, item_level):
    """Parse a single equipment effect into a readable dict."""
    defn = effect_data.get("effect", {}).get("definition", {})
    action_id = defn.get("actionId", 0)
    params = defn.get("params", [])
    
    # Params come in pairs: [base, scaling, base2, scaling2, ...]
    # Value = base + scaling * level
    values = []
    for i in range(0, len(params), 2):
        base = params[i] if i < len(params) else 0
        scaling = params[i + 1] if i + 1 < len(params) else 0
        value = base + scaling * item_level
        values.append(round(value, 1))
    
    action_info = action_map.get(action_id, {"effect": f"UNKNOWN_{action_id}", "desc_en": "", "desc_fr": ""})
    
    return {
        "actionId": action_id,
        "effect": action_info["effect"],
        "desc_fr": action_info["desc_fr"],
        "params_raw": params,
        "values": values,
        "primary_value": values[0] if values else 0
    }

def parse_items(items_data, action_map):
    """Parse all items from CDN JSON into our optimizer format."""
    parsed = []
    
    for entry in items_data:
        defn = entry.get("definition", {})
        item = defn.get("item", {})
        
        item_id = item.get("id", 0)
        level = item.get("level", 0)
        base_params = item.get("baseParameters", {})
        item_type_id = base_params.get("itemTypeId", 0)
        rarity = item.get("rarity", 0)
        
        # Parse equipment effects
        equip_effects = []
        for eff in defn.get("equipEffects", []):
            parsed_eff = parse_equip_effect(eff, action_map, level)
            equip_effects.append(parsed_eff)
        
        # Parse use effects (for weapons)
        use_effects = []
        for eff in defn.get("useEffects", []):
            parsed_eff = parse_equip_effect(eff, action_map, level)
            use_effects.append(parsed_eff)
        
        # Get title/name from the entry
        title = entry.get("title", {})
        name_fr = title.get("fr", f"Item_{item_id}")
        name_en = title.get("en", name_fr)
        
        parsed_item = {
            "id": item_id,
            "name_fr": name_fr,
            "name_en": name_en,
            "level": level,
            "rarity": rarity,
            "itemTypeId": item_type_id,
            "equipEffects": equip_effects,
            "useEffects": use_effects,
            # Stats summary for quick filtering
            "stats_summary": {}
        }
        
        # Build stats summary
        for eff in equip_effects:
            stat_name = eff["effect"]
            val = eff["primary_value"]
            if stat_name and val != 0:
                parsed_item["stats_summary"][stat_name] = val
        
        parsed.append(parsed_item)
    
    return parsed

# ── RARITY NAMES ───────────────────────────────────────────
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

# ── ITEM TYPE NAMES (partial, from wakfu wiki) ─────────────
ITEM_TYPE_MAP = {
    101: "Amulette",
    103: "Anneau", 
    108: "Casque",
    110: "Cape",
    112: "Bottes",
    114: "Épaulettes",
    119: "Ceinture",
    120: "Plastron",
    132: "Bouclier",
    133: "Dague",
    138: "Relique",
    189: "Emblème",
    223: "Épée 1 main",
    253: "Épée 2 mains",
    254: "Bâton",
    223: "Sword 1H",
    480: "Baguette",
    518: "Pelle",
    519: "Marteau",
    520: "Arc",
    521: "Hache",
    522: "Bâton 2M",
    253: "Greatsword",
    254: "Staff",
    480: "Wand",
    518: "Shovel",
    519: "Hammer",
    520: "Bow",
    521: "Axe",
    522: "Staff 2H",
    537: "Pistolet",
    582: "Cartes",
    647: "Accessoire",
    111: "Second main"
}

# ══════════════════════════════════════════════════════════
#                         M A I N
# ══════════════════════════════════════════════════════════
if __name__ == "__main__":
    log.info("=" * 60)
    log.info("WAKFU ITEMS PARSER — CDN + BDATA")
    log.info("=" * 60)
    
    # Step 1: Get current version
    try:
        version = get_version()
    except Exception as e:
        log.error(f"Failed to get version: {e}")
        log.info("Using fallback version 1.91.1.53")
        version = "1.91.1.53"
    
    # Step 2: Download actions.json (stat definitions)
    log.info("\n--- STEP 2: ACTIONS (stat definitions) ---")
    try:
        actions_raw = download_json(version, "actions.json")
        action_map = build_action_map(actions_raw)
        log.info(f"Loaded {len(action_map)} action definitions")
        
        # Show key equipment actions
        equip_actions = [20, 31, 41, 80, 120, 122, 123, 124, 125, 149, 150, 
                        160, 162, 166, 171, 173, 175, 177, 180, 191, 875,
                        988, 1052, 1053, 1055, 1068, 1069]
        log.info("\nKey equipment stat actions:")
        for aid in equip_actions:
            info = action_map.get(aid, {})
            log.info(f"  {aid:>5}: {info.get('effect', '?')}")
    except Exception as e:
        log.error(f"Failed to download actions: {e}")
        sys.exit(1)
    
    # Step 3: Download items.json
    log.info("\n--- STEP 3: ITEMS ---")
    try:
        items_raw = download_json(version, "items.json")
        log.info(f"Raw items count: {len(items_raw)}")
    except Exception as e:
        log.error(f"Failed to download items: {e}")
        sys.exit(1)
    
    # Step 4: Parse items
    log.info("\n--- STEP 4: PARSING ---")
    all_items = parse_items(items_raw, action_map)
    log.info(f"Parsed {len(all_items)} items")
    
    # Step 5: Statistics
    log.info("\n--- STEP 5: STATISTICS ---")
    
    # By rarity
    rarity_counts = {}
    for item in all_items:
        r = item["rarity"]
        rarity_counts[r] = rarity_counts.get(r, 0) + 1
    log.info("Items by rarity:")
    for r in sorted(rarity_counts.keys()):
        name = RARITY_MAP.get(r, f"Unknown({r})")
        log.info(f"  {name:>12}: {rarity_counts[r]:>5}")
    
    # By level range
    level_ranges = [(1, 50), (51, 100), (101, 150), (151, 200), (201, 245), (246, 300)]
    log.info("\nItems by level range:")
    for lo, hi in level_ranges:
        count = sum(1 for i in all_items if lo <= i["level"] <= hi)
        log.info(f"  Lvl {lo:>3}-{hi:>3}: {count:>5}")
    
    # Items with equipment effects
    with_effects = sum(1 for i in all_items if i["equipEffects"])
    with_use = sum(1 for i in all_items if i["useEffects"])
    log.info(f"\nWith equipEffects: {with_effects}")
    log.info(f"With useEffects:   {with_use}")
    
    # Step 6: Show sample high-level items
    log.info("\n--- STEP 6: SAMPLE ITEMS (Lvl 170-180, Legendary+) ---")
    samples = [i for i in all_items if 170 <= i["level"] <= 180 and i["rarity"] >= 4]
    samples.sort(key=lambda x: (-x["rarity"], -x["level"]))
    for item in samples[:10]:
        rname = RARITY_MAP.get(item["rarity"], "?")
        tname = ITEM_TYPE_MAP.get(item["itemTypeId"], f"Type{item['itemTypeId']}")
        log.info(f"\n  [{rname}] {item['name_fr']} (ID:{item['id']}, Lvl:{item['level']}, {tname})")
        for eff in item["equipEffects"][:8]:
            log.info(f"    {eff['effect']}: {eff['primary_value']}")
    
    # Step 7: Save parsed items
    log.info("\n--- STEP 7: SAVING ---")
    output_path = os.path.join(DATA_DIR, "all_items.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_items, f, ensure_ascii=False, indent=None)
    size_mb = os.path.getsize(output_path) / (1024 * 1024)
    log.info(f"Saved {len(all_items)} items to {output_path} ({size_mb:.1f} MB)")
    
    # Save action map too
    action_path = os.path.join(DATA_DIR, "action_map.json")
    with open(action_path, "w", encoding="utf-8") as f:
        json.dump(action_map, f, ensure_ascii=False, indent=2)
    log.info(f"Saved {len(action_map)} actions to {action_path}")
    
    # Step 8: Cross-reference with BData file 42
    log.info("\n--- STEP 8: BDATA CROSS-REFERENCE ---")
    bdata_42 = os.path.join(BDATA_DIR, "42.jar")
    if os.path.exists(bdata_42):
        size = os.path.getsize(bdata_42)
        log.info(f"BData file 42 exists: {size:,} bytes")
        log.info(f"CDN items: {len(all_items)} vs BData rows: 2842")
        log.info(f"Difference: {len(all_items) - 2842} items (CDN includes consumables, resources, etc.)")
    else:
        log.info(f"BData file 42 not found at {bdata_42}")
    
    # Step 9: Summary
    log.info("\n" + "=" * 60)
    log.info("SUMMARY")
    log.info("=" * 60)
    log.info(f"Game version:      {version}")
    log.info(f"Total items:       {len(all_items)}")
    log.info(f"Action definitions: {len(action_map)}")
    log.info(f"With equip stats:  {with_effects}")
    log.info(f"With use effects:  {with_use}")
    log.info(f"Output files:")
    log.info(f"  {output_path}")
    log.info(f"  {action_path}")
    log.info(f"\nDONE")
