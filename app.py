"""
Wakfu Optimizer - Builder
Version: 2.0
Stack: NiceGUI 3.8+ / Python 3.10
Data: API Wakfuli + Frontend Wakfuli
"""
import json
from pathlib import Path
from nicegui import ui, app

# =============================================================
# CONFIGURATION
# =============================================================
PROJECT = Path(r"H:\Code\Ankama Dev\wakfu-optimizer")
DATA = PROJECT / "data" / "wakfuli"

SLOT_ORDER = [
    "HEAD", "NECK", "CHEST", "BACK", "SHOULDERS", "BELT",
    "LEFT_HAND", "RIGHT_HAND", "LEGS",
    "FIRST_WEAPON", "SECOND_WEAPON", "ACCESSORY",
]

SLOT_LABELS = {
    "HEAD": "Casque", "NECK": "Amulette", "CHEST": "Plastron",
    "BACK": "Cape", "SHOULDERS": "Epaulettes", "BELT": "Ceinture",
    "LEFT_HAND": "Anneau G", "RIGHT_HAND": "Anneau D", "LEGS": "Bottes",
    "FIRST_WEAPON": "Arme 1", "SECOND_WEAPON": "Arme 2", "ACCESSORY": "Embleme",
}

RARITY_COLORS = {
    "COMMON": "#CCCCCC", "RARE": "#33CC33", "EPIC": "#FF9900",
    "LEGENDARY": "#FFCC00", "MYTHICAL": "#FF3366", "RELIC": "#CC33FF",
    "MEMORY": "#33CCFF", "OLD": "#999999",
}

RARITY_ORDER = ["MYTHICAL", "RELIC", "LEGENDARY", "EPIC", "RARE", "COMMON", "MEMORY", "OLD"]

ELEMENT_COLORS = {
    "FIRE": "#FF4444", "WATER": "#4488FF", "AIR": "#44DD44", "EARTH": "#CC8833",
}

CLASSES = [
    "cra", "ecaflip", "eliotrope", "eniripsa", "enutrof", "feca",
    "huppermage", "iop", "osamodas", "ouginak", "pandawa", "roublard",
    "sacrieur", "sadida", "sram", "steamer", "xelor", "zobal",
]

# =============================================================
# CHARGEMENT DES DONNEES
# =============================================================
def load_json(filename):
    path = DATA / filename
    if path.exists():
        return json.loads(path.read_text("utf-8"))
    return []

print("Chargement des donnees...")
ALL_ITEMS = load_json("all_items.json")
ALL_SPELLS = load_json("all_spells.json")
ALL_ACTIONS = load_json("all_actions.json")

# Index items par position
ITEMS_BY_SLOT = {}
for item in ALL_ITEMS:
    for pos in item.get("equipment_position", []):
        if pos not in ITEMS_BY_SLOT:
            ITEMS_BY_SLOT[pos] = []
        ITEMS_BY_SLOT[pos].append(item)

# Trier chaque slot par level desc puis rarity
def rarity_sort_key(item):
    r = item.get("rarity", "COMMON")
    try:
        return RARITY_ORDER.index(r)
    except ValueError:
        return 99

for slot in ITEMS_BY_SLOT:
    ITEMS_BY_SLOT[slot].sort(key=lambda x: (-x.get("level", 0), rarity_sort_key(x)))

# Version
VERSION_DATA = load_json("version.json")
GAME_VERSION = VERSION_DATA.get("version", "inconnue") if isinstance(VERSION_DATA, dict) else "inconnue"

print(f"  Items: {len(ALL_ITEMS)}")
print(f"  Spells: {sum(len(v.get('elementary', [])) + len(v.get('active', [])) + len(v.get('passive', [])) for v in ALL_SPELLS.values()) if isinstance(ALL_SPELLS, dict) else 0}")
print(f"  Actions: {len(ALL_ACTIONS)}")
print(f"  Version: {GAME_VERSION}")
print("Pret.")


# =============================================================
# ETAT DU BUILDER
# =============================================================
class BuildState:
    def __init__(self):
        self.character_class = "cra"
        self.level = 200
        self.equipment = {}
        self.active_spells = []
        self.passive_spells = []

    def get_items_for_slot(self, slot, search="", rarity_filter=None, level_max=None):
        items = ITEMS_BY_SLOT.get(slot, [])
        if level_max is None:
            level_max = self.level
        filtered = []
        for it in items:
            if it.get("level", 0) > level_max:
                continue
            if rarity_filter and it.get("rarity") != rarity_filter:
                continue
            if search:
                name = it.get("name", "").lower()
                if search.lower() not in name:
                    continue
            filtered.append(it)
        return filtered[:50]

    def equip_item(self, slot, item):
        self.equipment[slot] = item

    def unequip_slot(self, slot):
        if slot in self.equipment:
            del self.equipment[slot]

    def get_total_stats(self):
        stats = {
            "HP": 0, "AP": 0, "MP": 0, "WP": 0, "RANGE": 0,
            "MASTERY": 0, "RESISTANCE": 0,
            "CRITICAL_HIT": 0, "CRITICAL_MASTERY": 0,
            "BLOCK": 0, "DODGE": 0, "LOCK": 0, "INITIATIVE": 0,
            "HEAL_MASTERY": 0, "BACK_MASTERY": 0, "BERSERK_MASTERY": 0,
            "DISTANCE_MASTERY": 0, "MELEE_MASTERY": 0,
            "FIRE_RES": 0, "WATER_RES": 0, "AIR_RES": 0, "EARTH_RES": 0,
        }
        type_map = {
            "HP": "HP", "AP": "AP", "MP": "MP", "WP": "WP", "RANGE": "RANGE",
            "DMG_IN_PERCENT": "MASTERY", "RES_IN_PERCENT": "RESISTANCE",
            "CRITICAL_HIT": "CRITICAL_HIT", "CRITICAL_MASTERY": "CRITICAL_MASTERY",
            "BLOCK": "BLOCK", "DODGE": "DODGE", "LOCK": "LOCK", "INIT": "INITIATIVE",
            "HEAL_IN_PERCENT": "HEAL_MASTERY", "REAR_MASTERY": "BACK_MASTERY",
            "BERSERK_MASTERY": "BERSERK_MASTERY",
            "DISTANCE_MASTERY": "DISTANCE_MASTERY", "MELEE_MASTERY": "MELEE_MASTERY",
            "FIRE_RES": "FIRE_RES", "WATER_RES": "WATER_RES",
            "AIR_RES": "AIR_RES", "EARTH_RES": "EARTH_RES",
        }
        for slot, item in self.equipment.items():
            for eff in item.get("effects", []):
                etype = eff.get("type")
                val = eff.get("value", 0)
                if etype and etype in type_map:
                    stats[type_map[etype]] += val
        return stats

    def get_class_spells(self):
        if not isinstance(ALL_SPELLS, dict):
            return {"elementary": [], "active": [], "passive": []}
        class_data = ALL_SPELLS.get(self.character_class, {})
        return {
            "elementary": class_data.get("elementary", []),
            "active": class_data.get("active", []),
            "passive": class_data.get("passive", []),
        }
