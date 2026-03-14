"""
=============================================================
  WAKFU EQUIPMENT v2 — CORRECT SLOT MAPPING
  Based on actual item name analysis + useEffects detection
  Sources:
    - https://wakfu.wiki.gg/wiki/Equipment
    - Phase 1 audit of 8324 items by typeId
  Date: 2026-03-14
=============================================================
"""
import os, sys, json, logging, copy
from collections import defaultdict, Counter

PROJECT  = r"H:\Code\Ankama Dev\wakfu-optimizer"
DATA_DIR = os.path.join(PROJECT, "data", "extracted")
ENGINE   = os.path.join(PROJECT, "engine")
LOG_DIR  = os.path.join(PROJECT, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, "equipment_v2.log"), encoding="utf-8"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger("EquipV2")

# ══════════════════════════════════════════════════════════
#  CORRECTED SLOT MAPPING (verified via name audit)
# ══════════════════════════════════════════════════════════

TYPEID_TO_SLOT = {
    # ── Armor (no useEffects) ──────────────────────────────
    134: "helmet",        # Casque, Coiffe, Chapeau (913 items)
    132: "cloak",         # Cape, Manteau (798 items)
    120: "amulet",        # Amulette, Collier (730 items)
    138: "epaulettes",    # Epaulettes (695 items)
    136: "breastplate",   # Plastron, Armure (751 items)
    133: "belt",          # Ceinture, Ceinturon (697 items)
    103: "ring",          # Anneau, Bague (847 items)
    119: "boots",         # Bottes, Chaussures (827 items)

    # ── Weapons 1H (have useEffects) ──────────────────────
    110: "weapon_1h",     # Epée 1H (149 items)
    112: "weapon_1h",     # Dague (131 items)
    108: "weapon_1h",     # Baguette/Wand (90 items)
    101: "weapon_1h",     # Hache 1H (70 items)
    115: "weapon_1h",     # Aiguille (86 items)
    254: "weapon_1h",     # Cartes (68 items)

    # ── Weapons 2H (have useEffects) ──────────────────────
    223: "weapon_2h",     # Grande Epée (101 items)
    253: "weapon_2h",     # Main/Gourdin/Lance (102 items)
    113: "weapon_2h",     # Bâton (90 items)
    114: "weapon_2h",     # Marteau (86 items)
    117: "weapon_2h",     # Arc (67 items)
    111: "weapon_2h",     # Pelle (83 items)

    # ── Other ─────────────────────────────────────────────
    189: "second_hand",   # Bouclier/Shield (161 items)
    646: "emblem",        # Emblème (114 items)
    480: "torch",         # Torche/Lanterne (5 items)
    537: "tool",          # Outils (18 items)
    647: "accessory",     # Costume (7 items)
    611: "mount",         # Monture/Dragoune (37 items)
    582: "pet",           # Familier/Chacha (117 items)
    811: "sublimation",   # Sublimation scrolls (17 items)
    812: "enchantment",   # Enchantements (467 items)
}

# Reverse: slot -> list of typeIds
SLOT_TO_TYPEIDS = defaultdict(list)
for tid, slot in TYPEID_TO_SLOT.items():
    SLOT_TO_TYPEIDS[slot].append(tid)

WEAPON_1H_TYPES = set(SLOT_TO_TYPEIDS["weapon_1h"])
WEAPON_2H_TYPES = set(SLOT_TO_TYPEIDS["weapon_2h"])

RARITY_NAMES = {0:"Common", 1:"Unusual", 2:"Rare", 3:"Mythical",
                4:"Legendary", 5:"Relic", 6:"Souvenir", 7:"Epic"}

SLOT_DISPLAY = {
    "helmet": "Casque", "cloak": "Cape", "amulet": "Amulette",
    "epaulettes": "Epaulettes", "breastplate": "Plastron",
    "belt": "Ceinture", "ring": "Anneau", "boots": "Bottes",
    "weapon_1h": "Arme 1M", "weapon_2h": "Arme 2M",
    "second_hand": "Seconde Main", "emblem": "Emblème",
    "torch": "Torche", "tool": "Outil", "accessory": "Accessoire",
    "mount": "Monture", "pet": "Familier",
    "sublimation": "Sublimation", "enchantment": "Enchantement"
}

# ── Stat mapping ───────────────────────────────────────────
STAT_KEY_MAP = {
    20: "hp", 31: "ap", 41: "mp", 56: "ap", 57: "mp",
    191: "wp", 192: "wp", 193: "wp",
    80: "elemental_resistance",
    82: "fire_resistance", 83: "water_resistance",
    84: "earth_resistance", 85: "air_resistance",
    90: "elemental_resistance", 96: "earth_resistance",
    97: "fire_resistance", 98: "water_resistance",
    100: "elemental_resistance",
    120: "elemental_mastery",
    122: "fire_mastery", 123: "earth_mastery",
    124: "water_mastery", 125: "air_mastery",
    130: "elemental_mastery",
    149: "critical_mastery", 150: "critical_hit",
    160: "range", 161: "range",
    162: "prospecting", 166: "wisdom", 168: "critical_hit",
    171: "initiative", 172: "initiative",
    173: "lock", 174: "lock", 175: "dodge", 176: "dodge",
    177: "force_of_will",
    180: "rear_mastery", 181: "rear_mastery",
    875: "block", 876: "block",
    988: "critical_resistance",
    1052: "melee_mastery", 1053: "distance_mastery",
    1055: "berserk_mastery", 1056: "critical_mastery",
    1059: "melee_mastery", 1060: "distance_mastery",
    1061: "berserk_mastery",
    1062: "critical_resistance", 1063: "rear_resistance",
    1068: "random_elemental_mastery",
    1069: "random_elemental_resistance",
    26: "healing_mastery", 71: "rear_resistance",
}

NEGATIVE_ACTIONS = {21, 56, 57, 90, 96, 97, 98, 100, 130, 161, 168,
                    172, 174, 176, 181, 192, 876, 1056, 1059, 1060,
                    1061, 1062, 1063}

# ══════════════════════════════════════════════════════════
#  EQUIPMENT MANAGER v2
# ══════════════════════════════════════════════════════════

class EquipmentManager:
    EQUIP_SLOTS = [
        "helmet", "cloak", "amulet", "epaulettes", "breastplate",
        "belt", "ring1", "ring2", "boots", "weapon", "second_hand",
        "emblem", "pet", "mount"
    ]

    def __init__(self, character_level, items_db=None):
        self.character_level = character_level
        self.items_db = items_db or {}
        self.equipped = {slot: None for slot in self.EQUIP_SLOTS}
        self._stats_cache = None

    def get_slot_for_item(self, item):
        tid = item["itemTypeId"]
        base_slot = TYPEID_TO_SLOT.get(tid)
        if base_slot is None:
            return []
        if base_slot == "ring":
            return ["ring1", "ring2"]
        if base_slot in ("weapon_1h", "weapon_2h"):
            return ["weapon"]
        if base_slot in ("sublimation", "enchantment"):
            return []
        return [base_slot]

    def can_equip(self, item, target_slot=None):
        if item["level"] > self.character_level:
            return False, f"Level {item['level']} > {self.character_level}"
        rarity = item["rarity"]
        if rarity == 5:
            for slot, eq in self.equipped.items():
                if eq and eq["id"] != item["id"] and eq["rarity"] == 5:
                    if target_slot and slot == target_slot:
                        continue
                    return False, f"Relic already in {slot}"
        if rarity == 7:
            for slot, eq in self.equipped.items():
                if eq and eq["id"] != item["id"] and eq["rarity"] == 7:
                    if target_slot and slot == target_slot:
                        continue
                    return False, f"Epic already in {slot}"
        if target_slot in ("ring1", "ring2"):
            other = "ring2" if target_slot == "ring1" else "ring1"
            oeq = self.equipped.get(other)
            if oeq and oeq["id"] == item["id"]:
                return False, "Duplicate ring"
        return True, "OK"

    def equip(self, item, target_slot=None):
        self._stats_cache = None
        if target_slot is None:
            possible = self.get_slot_for_item(item)
            if not possible:
                return False, f"No slot for typeId {item['itemTypeId']}"
            target_slot = possible[0]
            for s in possible:
                if self.equipped.get(s) is None:
                    target_slot = s
                    break

        tid = item["itemTypeId"]
        if tid in WEAPON_2H_TYPES:
            target_slot = "weapon"
            if self.equipped.get("second_hand"):
                self.equipped["second_hand"] = None
        elif tid in WEAPON_1H_TYPES:
            target_slot = "weapon"

        ok, reason = self.can_equip(item, target_slot)
        if not ok:
            return False, reason

        old = self.equipped.get(target_slot)
        self.equipped[target_slot] = item
        return True, f"OK: {item['name_fr']} -> {target_slot}"

    def calculate_stats(self):
        if self._stats_cache is not None:
            return self._stats_cache
        stats = defaultdict(float)
        for slot, item in self.equipped.items():
            if item is None:
                continue
            for eff in item.get("equipEffects", []):
                aid = eff.get("actionId", 0)
                val = eff.get("value", 0)
                key = STAT_KEY_MAP.get(aid)
                if key is None:
                    continue
                if aid in NEGATIVE_ACTIONS and val > 0:
                    val = -val
                if aid in (1068, 1069):
                    nb = eff.get("nb_elements", 1)
                    stats[key] += val
                    stats[f"{key}_nb_elements"] = max(stats.get(f"{key}_nb_elements", 0), nb)
                else:
                    stats[key] += val
        self._stats_cache = {k: round(v, 1) for k, v in stats.items()}
        return self._stats_cache

    def get_fighter_profile(self, base_profile):
        es = self.calculate_stats()
        p = copy.deepcopy(base_profile)
        p["hp"] = p.get("hp", 0) + es.get("hp", 0)
        p["ap"] = p.get("ap", 0) + es.get("ap", 0)
        p["mp"] = p.get("mp", 0) + es.get("mp", 0)
        p["wp"] = p.get("wp", 0) + es.get("wp", 0)
        m = p.get("masteries", {})
        for k in ["elemental_mastery","fire_mastery","water_mastery",
                   "earth_mastery","air_mastery","melee_mastery",
                   "distance_mastery","critical_mastery","rear_mastery",
                   "berserk_mastery","healing_mastery"]:
            m[k] = m.get(k, 0) + es.get(k, 0)
        rem = es.get("random_elemental_mastery", 0)
        if rem > 0:
            for k in ["fire_mastery","water_mastery","earth_mastery","air_mastery"]:
                m[k] = m.get(k, 0) + rem
        p["masteries"] = m
        r = p.get("resistances", {})
        for k in ["fire","water","earth","air"]:
            r[k] = r.get(k, 0) + es.get(f"{k}_resistance", 0)
        er = es.get("elemental_resistance", 0)
        rer = es.get("random_elemental_resistance", 0)
        for k in ["fire","water","earth","air"]:
            r[k] = r.get(k, 0) + er + rer
        r["critical"] = r.get("critical", 0) + es.get("critical_resistance", 0)
        r["rear"] = r.get("rear", 0) + es.get("rear_resistance", 0)
        p["resistances"] = r
        p["critical_hit"] = p.get("critical_hit", 0) + es.get("critical_hit", 0)
        p["block"] = p.get("block", 0) + es.get("block", 0)
        p["range"] = p.get("range", 0) + es.get("range", 0)
        p["dodge"] = p.get("dodge", 0) + es.get("dodge", 0)
        p["lock"] = p.get("lock", 0) + es.get("lock", 0)
        return p

    def summary(self):
        lines = [f"\n{'='*60}", f"  BUILD (Level {self.character_level})", f"{'='*60}"]
        count = 0
        for slot in self.EQUIP_SLOTS:
            item = self.equipped.get(slot)
            if item:
                rn = RARITY_NAMES.get(item["rarity"], "?")
                sn = SLOT_DISPLAY.get(slot, slot)
                lines.append(f"  {sn:>14}: [{rn}] {item['name_fr']} (Lvl {item['level']})")
                count += 1
            else:
                sn = SLOT_DISPLAY.get(slot, slot)
                lines.append(f"  {sn:>14}: ---")
        stats = self.calculate_stats()
        lines.append(f"\n  --- TOTAL STATS ({count} items) ---")
        for k in sorted(stats.keys()):
            if stats[k] != 0 and not k.endswith("_nb_elements"):
                lines.append(f"  {k:>30}: {stats[k]:>+.0f}")
        return "\n".join(lines)


# ══════════════════════════════════════════════════════════
#  ITEM RECOMMENDER v2
# ══════════════════════════════════════════════════════════

class ItemRecommender:
    SRAM_MELEE_WEIGHTS = {
        "melee_mastery": 1.0, "elemental_mastery": 1.0,
        "fire_mastery": 0.8, "water_mastery": 0.8,
        "air_mastery": 0.8, "earth_mastery": 0.5,
        "critical_mastery": 0.7, "rear_mastery": 0.9,
        "berserk_mastery": 0.6,
        "critical_hit": 10.0, "hp": 0.1,
        "ap": 200.0, "mp": 100.0, "wp": 50.0, "range": 15.0,
        "dodge": 0.3, "lock": 0.3, "block": 5.0,
        "random_elemental_mastery": 0.9,
        "distance_mastery": 0.0,
        "healing_mastery": 0.0,
    }

    def __init__(self, all_items, character_level):
        self.all_items = all_items
        self.character_level = character_level
        self.by_slot = defaultdict(list)
        for item in all_items:
            if item["level"] > character_level:
                continue
            tid = item["itemTypeId"]
            base_slot = TYPEID_TO_SLOT.get(tid)
            if base_slot:
                self.by_slot[base_slot].append(item)
        log.info(f"Recommender: {len(all_items)} total, eligible per slot:")
        for slot in sorted(self.by_slot.keys()):
            log.info(f"  {slot:>16}: {len(self.by_slot[slot])}")

    def score_item(self, item, weights):
        score = 0.0
        for eff in item.get("equipEffects", []):
            aid = eff.get("actionId", 0)
            val = eff.get("value", 0)
            key = STAT_KEY_MAP.get(aid)
            if key is None:
                continue
            if aid in NEGATIVE_ACTIONS and val > 0:
                val = -val
            w = weights.get(key, 0)
            score += val * w
        return round(score, 1)

    def recommend(self, slot_name, weights=None, top_n=10, min_rarity=0):
        if weights is None:
            weights = self.SRAM_MELEE_WEIGHTS

        # Map display slot to base slot(s)
        slot_map = {
            "weapon": ["weapon_1h", "weapon_2h"],
            "ring1": ["ring"], "ring2": ["ring"],
        }
        base_slots = slot_map.get(slot_name, [slot_name])

        candidates = []
        for bs in base_slots:
            candidates.extend(self.by_slot.get(bs, []))

        if min_rarity > 0:
            candidates = [c for c in candidates if c["rarity"] >= min_rarity]

        scored = [(item, self.score_item(item, weights)) for item in candidates]
        scored.sort(key=lambda x: -x[1])
        return scored[:top_n]

    def recommend_full_build(self, weights=None, min_rarity=3):
        if weights is None:
            weights = self.SRAM_MELEE_WEIGHTS

        build = {}
        used_relic = False
        used_epic = False

        slots = [
            ("weapon", ["weapon_1h", "weapon_2h"]),
            ("amulet", ["amulet"]),
            ("ring1", ["ring"]),
            ("ring2", ["ring"]),
            ("helmet", ["helmet"]),
            ("cloak", ["cloak"]),
            ("epaulettes", ["epaulettes"]),
            ("breastplate", ["breastplate"]),
            ("belt", ["belt"]),
            ("boots", ["boots"]),
            ("second_hand", ["second_hand"]),
            ("emblem", ["emblem"]),
            ("pet", ["pet"]),
            ("mount", ["mount"]),
        ]

        for slot_name, base_slots in slots:
            candidates = []
            for bs in base_slots:
                candidates.extend(self.by_slot.get(bs, []))
            if min_rarity > 0:
                candidates = [c for c in candidates if c["rarity"] >= min_rarity]

            scored = [(it, self.score_item(it, weights)) for it in candidates]
            scored.sort(key=lambda x: -x[1])

            for item, score in scored:
                if item["rarity"] == 5 and used_relic:
                    continue
                if item["rarity"] == 7 and used_epic:
                    continue
                if slot_name == "ring2" and "ring1" in build:
                    if item["id"] == build["ring1"][0]["id"]:
                        continue
                # 2H weapon blocks second_hand
                if slot_name == "second_hand" and "weapon" in build:
                    w = build["weapon"][0]
                    if w["itemTypeId"] in WEAPON_2H_TYPES:
                        build[slot_name] = None
                        break
                build[slot_name] = (item, score)
                if item["rarity"] == 5:
                    used_relic = True
                if item["rarity"] == 7:
                    used_epic = True
                break

        return {k: v for k, v in build.items() if v is not None}


# ══════════════════════════════════════════════════════════
#                         M A I N
# ══════════════════════════════════════════════════════════
if __name__ == "__main__":
    log.info("=" * 60)
    log.info("WAKFU EQUIPMENT v2 — CORRECTED MAPPING")
    log.info("=" * 60)

    with open(os.path.join(DATA_DIR, "all_items.json"), "r", encoding="utf-8") as f:
        all_items = json.load(f)
    log.info(f"Loaded {len(all_items)} items")
    items_by_id = {i["id"]: i for i in all_items}

    # ── Verify mapping ─────────────────────────────────────
    log.info("\n--- SLOT VERIFICATION ---")
    for slot in sorted(SLOT_TO_TYPEIDS.keys()):
        tids = SLOT_TO_TYPEIDS[slot]
        total = sum(len([i for i in all_items if i["itemTypeId"] == t]) for t in tids)
        log.info(f"  {SLOT_DISPLAY.get(slot, slot):>16}: typeIds {tids} -> {total} items")

    # ── Recommender ────────────────────────────────────────
    rec = ItemRecommender(all_items, character_level=179)

    log.info("\n--- TOP 10 DAGGERS (typeId 112, slot=weapon) ---")
    dagger_items = [i for i in all_items if i["itemTypeId"] == 112 and i["level"] <= 179 and i["rarity"] >= 3]
    dagger_scored = [(i, rec.score_item(i, rec.SRAM_MELEE_WEIGHTS)) for i in dagger_items]
    dagger_scored.sort(key=lambda x: -x[1])
    for rank, (item, score) in enumerate(dagger_scored[:10], 1):
        rn = RARITY_NAMES.get(item["rarity"], "?")
        log.info(f"  #{rank:>2} [{rn:>9}] {item['name_fr']} (Lvl {item['level']}) — Score: {score:.0f}")
        for s, v in item.get("stats", {}).items():
            log.info(f"       {s}: {v}")

    log.info("\n--- TOP 5 BELTS (typeId 133) ---")
    top_belts = rec.recommend("belt", top_n=5, min_rarity=3)
    for rank, (item, score) in enumerate(top_belts, 1):
        rn = RARITY_NAMES.get(item["rarity"], "?")
        log.info(f"  #{rank:>2} [{rn:>9}] {item['name_fr']} (Lvl {item['level']}) — Score: {score:.0f}")
        for s, v in item.get("stats", {}).items():
            log.info(f"       {s}: {v}")

    log.info("\n--- TOP 5 BOOTS (typeId 119) ---")
    top_boots = rec.recommend("boots", top_n=5, min_rarity=3)
    for rank, (item, score) in enumerate(top_boots, 1):
        rn = RARITY_NAMES.get(item["rarity"], "?")
        log.info(f"  #{rank:>2} [{rn:>9}] {item['name_fr']} (Lvl {item['level']}) — Score: {score:.0f}")
        for s, v in item.get("stats", {}).items():
            log.info(f"       {s}: {v}")

    # ── Full auto-build ────────────────────────────────────
    log.info("\n" + "=" * 60)
    log.info("AUTO-BUILD: BEST SRAM MELEE (Lvl 179)")
    log.info("=" * 60)

    auto_build = rec.recommend_full_build(min_rarity=3)
    em = EquipmentManager(character_level=179, items_db=items_by_id)
    for slot, (item, score) in auto_build.items():
        ok, msg = em.equip(item, target_slot=slot)
        if not ok:
            log.warning(f"  FAILED {slot}: {msg}")

    log.info(em.summary())

    # Merged profile
    base_sram = {
        "name": "L'Immortel", "class": "sram", "level": 179,
        "hp": 4800, "ap": 6, "mp": 3, "wp": 6,
        "masteries": {}, "resistances": {"fire":0,"water":0,"earth":0,"air":0,"critical":0,"rear":0},
        "damage_inflicted": 0, "critical_hit": 3, "block": 0
    }
    fp = em.get_fighter_profile(base_sram)
    log.info(f"\n--- FIGHTER PROFILE (base + equipment) ---")
    log.info(f"  HP: {fp['hp']:.0f}  AP: {fp['ap']:.0f}  MP: {fp['mp']:.0f}  WP: {fp['wp']}")
    log.info(f"  Crit: {fp['critical_hit']:.0f}%  Block: {fp['block']:.0f}%")
    log.info(f"  Masteries:")
    for k in sorted(fp["masteries"].keys()):
        v = fp["masteries"][k]
        if v != 0:
            log.info(f"    {k}: {v:.0f}")
    log.info(f"  Resistances:")
    for k in sorted(fp["resistances"].keys()):
        v = fp["resistances"][k]
        if v != 0:
            log.info(f"    {k}: {v:.0f}")

    # ── Save engine module ─────────────────────────────────
    module_path = os.path.join(ENGINE, "equipment.py")
    with open(__file__, "r", encoding="utf-8") as f:
        source = f.read()
    marker = 'if __name__ == "__main__":'
    idx = source.find(marker)
    if idx > 0:
        module_code = source[:idx]
        module_code += "\n# Auto-extracted from rebuild_equipment_fixed.py\n"
        with open(module_path, "w", encoding="utf-8") as f:
            f.write(module_code)
        log.info(f"\nSaved engine/equipment.py ({os.path.getsize(module_path):,} bytes)")

    log.info("DONE")
