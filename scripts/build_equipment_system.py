"""
=============================================================
  WAKFU EQUIPMENT MANAGER + ITEM RECOMMENDER
  Module A: Build Simulator (calculate total stats from gear)
  Module B: Item Filter/Recommender (find best items per slot)
  
  Sources:
    - https://wakfu.wiki.gg/wiki/Equipment (slots, constraints)
    - https://wakfu.cdn.ankama.com/gamedata/ (items data)
    - https://dev.to/heymarkkop/decoding-wakfu-s-action-effects-with-javascript-1nm2
  
  Constraints (wiki):
    - 1 Relic max per character
    - 1 Epic max per character
    - No duplicate ring (same item)
    - Item level <= character level
    - 2H weapon blocks Second Hand slot
  
  Date: 2026-03-14
=============================================================
"""
import os, sys, json, logging, copy
from collections import defaultdict
from datetime import datetime

# ── Paths ──────────────────────────────────────────────────
PROJECT  = r"H:\Code\Ankama Dev\wakfu-optimizer"
DATA_DIR = os.path.join(PROJECT, "data", "extracted")
ENGINE   = os.path.join(PROJECT, "engine")
LOG_DIR  = os.path.join(PROJECT, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, "equipment_system.log"), encoding="utf-8"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger("EquipSystem")

# ══════════════════════════════════════════════════════════
#  CONSTANTS
# ══════════════════════════════════════════════════════════

# Slot definitions: slot_name -> list of accepted itemTypeIds
# Based on wakfu.wiki.gg/wiki/Equipment + our parsed typeIds
SLOT_TYPES = {
    "helmet":      [108],
    "cloak":       [110],
    "amulet":      [101, 134],       # 101=old Amulet, 134=new Amulet
    "epaulettes":  [114],
    "breastplate": [113, 120],       # 113=Plastron, 120=Plastron(old)
    "belt":        [115, 119],       # 115=Ceinture, 119=Ceinture(old)
    "ring1":       [103, 136],       # 103=Anneau, 136=Anneau(new)
    "ring2":       [103, 136],
    "boots":       [112, 138],       # 112=Bottes, 138=Bottes(new)
    "weapon_1h":   [223, 133, 480, 537, 582],  # Sword1H, Dagger, Wand, Pistol, Cards
    "weapon_2h":   [253, 254, 518, 519, 520, 521, 522],  # Greatsword, Staff, Shovel, Hammer, Bow, Axe, Staff2H
    "second_hand": [111, 132],       # SecondHand, Shield
    "emblem":      [189],
    "mount":       [811],
    "pet":         [812],
    "accessory":   [647],
    "torch":       [611],
    "tool":        [646],
}

# Merge all weapon types for slot matching
WEAPON_1H_TYPES = set(SLOT_TYPES["weapon_1h"])
WEAPON_2H_TYPES = set(SLOT_TYPES["weapon_2h"])
ALL_WEAPON_TYPES = WEAPON_1H_TYPES | WEAPON_2H_TYPES

# ActionId -> stat key mapping for aggregation
STAT_KEY_MAP = {
    20: "hp", 21: "hp",  # 21 is -HP but value already negative in some contexts
    31: "ap", 41: "mp", 56: "ap", 57: "mp",
    191: "wp", 192: "wp", 193: "wp",
    80: "elemental_resistance",
    82: "fire_resistance", 83: "water_resistance",
    84: "earth_resistance", 85: "air_resistance",
    90: "elemental_resistance",
    96: "earth_resistance", 97: "fire_resistance",
    98: "water_resistance", 100: "elemental_resistance",
    120: "elemental_mastery",
    122: "fire_mastery", 123: "earth_mastery",
    124: "water_mastery", 125: "air_mastery",
    130: "elemental_mastery",
    149: "critical_mastery", 150: "critical_hit",
    160: "range", 161: "range",
    162: "prospecting", 166: "wisdom",
    168: "critical_hit",
    171: "initiative", 172: "initiative",
    173: "lock", 174: "lock",
    175: "dodge", 176: "dodge",
    177: "force_of_will",
    180: "rear_mastery", 181: "rear_mastery",
    875: "block", 876: "block",
    988: "critical_resistance",
    1052: "melee_mastery", 1053: "distance_mastery",
    1055: "berserk_mastery",
    1056: "critical_mastery",
    1059: "melee_mastery", 1060: "distance_mastery",
    1061: "berserk_mastery",
    1062: "critical_resistance", 1063: "rear_resistance",
    1068: "random_elemental_mastery",
    1069: "random_elemental_resistance",
    26: "healing_mastery",
    71: "rear_resistance",
}

# Negative actionIds (debuffs)
NEGATIVE_ACTIONS = {21, 56, 57, 90, 96, 97, 98, 100, 130, 161, 168,
                    172, 174, 176, 181, 192, 876, 1056, 1059, 1060,
                    1061, 1062, 1063}

RARITY_NAMES = {0:"Common", 1:"Unusual", 2:"Rare", 3:"Mythical",
                4:"Legendary", 5:"Relic", 6:"Souvenir", 7:"Epic"}

# ══════════════════════════════════════════════════════════
#  MODULE A: EQUIPMENT MANAGER
# ══════════════════════════════════════════════════════════

class EquipmentManager:
    """
    Manages a character's equipment build.
    Calculates total stats from all equipped items.
    Enforces Wakfu equipment constraints.
    """
    
    EQUIP_SLOTS = [
        "helmet", "cloak", "amulet", "epaulettes", "breastplate",
        "belt", "ring1", "ring2", "boots", "weapon", "second_hand",
        "emblem", "pet", "mount", "accessory", "torch"
    ]
    
    def __init__(self, character_level, items_db):
        self.character_level = character_level
        self.items_db = items_db  # dict: item_id -> item_data
        self.equipped = {}        # slot_name -> item_data or None
        for slot in self.EQUIP_SLOTS:
            self.equipped[slot] = None
        self._stats_cache = None
        log.info(f"EquipmentManager created for level {character_level}")
    
    def get_slot_for_item(self, item):
        """Determine which slot(s) an item can go into."""
        tid = item["itemTypeId"]
        possible = []
        for slot_name, type_ids in SLOT_TYPES.items():
            if tid in type_ids:
                possible.append(slot_name)
        # Merge ring1/ring2 into generic "ring"
        if "ring1" in possible or "ring2" in possible:
            possible = ["ring1", "ring2"]
        # Merge weapon_1h/weapon_2h into "weapon"
        if "weapon_1h" in possible or "weapon_2h" in possible:
            possible = ["weapon"]
        return possible
    
    def can_equip(self, item, target_slot=None):
        """
        Check if an item can be equipped. Returns (ok, reason).
        Constraints:
          - Level <= character level
          - Max 1 Relic across all slots
          - Max 1 Epic across all slots
          - No duplicate ring item
          - 2H weapon blocks second_hand
        """
        if item["level"] > self.character_level:
            return False, f"Item level {item['level']} > character level {self.character_level}"
        
        rarity = item["rarity"]
        
        # Check Relic constraint
        if rarity == 5:
            for slot, eq in self.equipped.items():
                if eq and eq["id"] != item["id"] and eq["rarity"] == 5:
                    if target_slot and slot == target_slot:
                        continue  # replacing this slot is ok
                    return False, f"Already have a Relic in slot {slot}: {eq['name_fr']}"
        
        # Check Epic constraint
        if rarity == 7:
            for slot, eq in self.equipped.items():
                if eq and eq["id"] != item["id"] and eq["rarity"] == 7:
                    if target_slot and slot == target_slot:
                        continue
                    return False, f"Already have an Epic in slot {slot}: {eq['name_fr']}"
        
        # Check duplicate ring
        if target_slot in ("ring1", "ring2"):
            other_slot = "ring2" if target_slot == "ring1" else "ring1"
            other = self.equipped.get(other_slot)
            if other and other["id"] == item["id"]:
                return False, f"Cannot equip same ring in both slots: {item['name_fr']}"
        
        return True, "OK"
    
    def equip(self, item, target_slot=None):
        """
        Equip an item. Auto-detects slot if not specified.
        Returns (success, message).
        """
        self._stats_cache = None
        
        # Determine slot
        if target_slot is None:
            possible = self.get_slot_for_item(item)
            if not possible:
                return False, f"No valid slot for itemTypeId {item['itemTypeId']}"
            # Pick first empty slot, or first slot
            target_slot = possible[0]
            for s in possible:
                if self.equipped.get(s) is None:
                    target_slot = s
                    break
        
        # Handle weapon (1H vs 2H)
        tid = item["itemTypeId"]
        if tid in WEAPON_2H_TYPES:
            target_slot = "weapon"
            # 2H weapon clears second hand
            if self.equipped.get("second_hand"):
                log.info(f"  2H weapon: unequipping second hand ({self.equipped['second_hand']['name_fr']})")
                self.equipped["second_hand"] = None
        elif tid in WEAPON_1H_TYPES:
            target_slot = "weapon"
        
        # Validate
        ok, reason = self.can_equip(item, target_slot)
        if not ok:
            return False, reason
        
        old = self.equipped.get(target_slot)
        self.equipped[target_slot] = item
        
        msg = f"Equipped [{RARITY_NAMES.get(item['rarity'],'?')}] {item['name_fr']} in {target_slot}"
        if old:
            msg += f" (replaced {old['name_fr']})"
        log.info(f"  {msg}")
        return True, msg
    
    def unequip(self, slot):
        """Remove item from a slot."""
        self._stats_cache = None
        old = self.equipped.get(slot)
        self.equipped[slot] = None
        if old:
            log.info(f"  Unequipped {old['name_fr']} from {slot}")
        return old
    
    def calculate_stats(self):
        """
        Calculate total stats from all equipped items.
        Returns a dict of stat_key -> total_value.
        """
        if self._stats_cache is not None:
            return self._stats_cache
        
        stats = defaultdict(float)
        
        for slot, item in self.equipped.items():
            if item is None:
                continue
            
            for eff in item.get("equipEffects", []):
                action_id = eff.get("actionId", 0)
                value = eff.get("value", 0)
                
                stat_key = STAT_KEY_MAP.get(action_id)
                if stat_key is None:
                    continue
                
                # Handle sign: negative actions make value negative
                if action_id in NEGATIVE_ACTIONS and value > 0:
                    value = -value
                
                # Random mastery/resistance: counts as elemental mastery/res
                # but distributed across N elements (handled by optimizer later)
                if action_id in (1068, 1069):
                    nb_elem = eff.get("nb_elements", 1)
                    stats[stat_key] += value
                    stats[f"{stat_key}_nb_elements"] = max(
                        stats.get(f"{stat_key}_nb_elements", 0), nb_elem
                    )
                else:
                    stats[stat_key] += value
        
        # Round all values
        result = {k: round(v, 1) for k, v in stats.items()}
        self._stats_cache = result
        return result
    
    def get_fighter_profile(self, base_profile):
        """
        Merge equipment stats into a base character profile.
        Returns a complete profile dict ready for Fighter().
        """
        equip_stats = self.calculate_stats()
        profile = copy.deepcopy(base_profile)
        
        # Add HP
        profile["hp"] = profile.get("hp", 0) + equip_stats.get("hp", 0)
        
        # Add AP/MP/WP
        profile["ap"] = profile.get("ap", 0) + equip_stats.get("ap", 0)
        profile["mp"] = profile.get("mp", 0) + equip_stats.get("mp", 0)
        profile["wp"] = profile.get("wp", 0) + equip_stats.get("wp", 0)
        
        # Add masteries
        masteries = profile.get("masteries", {})
        for key in ["elemental_mastery", "fire_mastery", "water_mastery",
                     "earth_mastery", "air_mastery", "melee_mastery",
                     "distance_mastery", "critical_mastery", "rear_mastery",
                     "berserk_mastery", "healing_mastery"]:
            masteries[key] = masteries.get(key, 0) + equip_stats.get(key, 0)
        
        # Random elemental mastery: add to all elements equally
        rem = equip_stats.get("random_elemental_mastery", 0)
        if rem > 0:
            for key in ["fire_mastery", "water_mastery", "earth_mastery", "air_mastery"]:
                masteries[key] = masteries.get(key, 0) + rem
        
        profile["masteries"] = masteries
        
        # Add resistances
        resistances = profile.get("resistances", {})
        for key in ["fire", "water", "earth", "air"]:
            full_key = f"{key}_resistance"
            resistances[key] = resistances.get(key, 0) + equip_stats.get(full_key, 0)
        elem_res = equip_stats.get("elemental_resistance", 0)
        if elem_res != 0:
            for key in ["fire", "water", "earth", "air"]:
                resistances[key] = resistances.get(key, 0) + elem_res
        rer = equip_stats.get("random_elemental_resistance", 0)
        if rer > 0:
            for key in ["fire", "water", "earth", "air"]:
                resistances[key] = resistances.get(key, 0) + rer
        
        resistances["critical"] = resistances.get("critical", 0) + equip_stats.get("critical_resistance", 0)
        resistances["rear"] = resistances.get("rear", 0) + equip_stats.get("rear_resistance", 0)
        profile["resistances"] = resistances
        
        # Other stats
        profile["critical_hit"] = profile.get("critical_hit", 0) + equip_stats.get("critical_hit", 0)
        profile["block"] = profile.get("block", 0) + equip_stats.get("block", 0)
        profile["range"] = profile.get("range", 0) + equip_stats.get("range", 0)
        profile["dodge"] = profile.get("dodge", 0) + equip_stats.get("dodge", 0)
        profile["lock"] = profile.get("lock", 0) + equip_stats.get("lock", 0)
        profile["initiative"] = profile.get("initiative", 0) + equip_stats.get("initiative", 0)
        profile["force_of_will"] = profile.get("force_of_will", 0) + equip_stats.get("force_of_will", 0)
        
        return profile
    
    def summary(self):
        """Print a readable summary of equipped items and total stats."""
        lines = []
        lines.append(f"\n{'='*60}")
        lines.append(f"  EQUIPMENT BUILD (Level {self.character_level})")
        lines.append(f"{'='*60}")
        
        count = 0
        for slot in self.EQUIP_SLOTS:
            item = self.equipped.get(slot)
            if item:
                rname = RARITY_NAMES.get(item["rarity"], "?")
                lines.append(f"  {slot:>14}: [{rname}] {item['name_fr']} (Lvl {item['level']})")
                count += 1
            else:
                lines.append(f"  {slot:>14}: (empty)")
        
        stats = self.calculate_stats()
        lines.append(f"\n  --- TOTAL EQUIPMENT STATS ({count} items) ---")
        for key in sorted(stats.keys()):
            val = stats[key]
            if val != 0:
                lines.append(f"  {key:>30}: {val:>+.1f}")
        
        return "\n".join(lines)


# ══════════════════════════════════════════════════════════
#  MODULE B: ITEM RECOMMENDER
# ══════════════════════════════════════════════════════════

class ItemRecommender:
    """
    Finds the best items for a given slot and character profile.
    Supports weighted scoring based on desired stats.
    """
    
    # Default Sram melee DPS weights
    SRAM_MELEE_WEIGHTS = {
        "melee_mastery": 1.0,
        "elemental_mastery": 1.0,
        "fire_mastery": 0.8,
        "water_mastery": 0.8,
        "air_mastery": 0.8,
        "earth_mastery": 0.5,
        "critical_mastery": 0.7,
        "critical_hit": 10.0,    # 1% crit ~ 10 mastery points
        "rear_mastery": 0.9,
        "berserk_mastery": 0.6,
        "hp": 0.1,
        "ap": 200.0,             # 1 AP ~ 200 mastery points
        "mp": 100.0,
        "wp": 50.0,
        "range": 15.0,
        "dodge": 0.3,
        "lock": 0.3,
        "block": 5.0,
        "random_elemental_mastery": 0.9,
    }
    
    def __init__(self, all_items, character_level):
        self.all_items = all_items
        self.character_level = character_level
        # Pre-index items by typeId
        self.by_type = defaultdict(list)
        for item in all_items:
            if item["level"] <= character_level:
                self.by_type[item["itemTypeId"]].append(item)
        log.info(f"ItemRecommender: {len(all_items)} items, {sum(len(v) for v in self.by_type.values())} eligible at level {character_level}")
    
    def score_item(self, item, weights):
        """Calculate a weighted score for an item."""
        score = 0.0
        for eff in item.get("equipEffects", []):
            action_id = eff.get("actionId", 0)
            value = eff.get("value", 0)
            
            stat_key = STAT_KEY_MAP.get(action_id)
            if stat_key is None:
                continue
            
            # Handle negative actions
            if action_id in NEGATIVE_ACTIONS and value > 0:
                value = -value
            
            weight = weights.get(stat_key, 0)
            score += value * weight
        
        return round(score, 1)
    
    def recommend(self, slot_name, weights=None, top_n=10, min_rarity=0, elements=None):
        """
        Find the best items for a given slot.
        
        Args:
            slot_name: Equipment slot (e.g., "weapon", "ring1", "amulet")
            weights: Dict of stat_key -> weight. Defaults to SRAM_MELEE_WEIGHTS.
            top_n: Number of results to return.
            min_rarity: Minimum rarity filter (0-7).
            elements: List of preferred elements (e.g., ["fire", "water"]).
        
        Returns:
            List of (item, score) tuples, sorted by score descending.
        """
        if weights is None:
            weights = self.SRAM_MELEE_WEIGHTS
        
        # Get valid typeIds for this slot
        if slot_name == "weapon":
            type_ids = list(WEAPON_1H_TYPES | WEAPON_2H_TYPES)
        elif slot_name in SLOT_TYPES:
            type_ids = SLOT_TYPES[slot_name]
        else:
            log.warning(f"Unknown slot: {slot_name}")
            return []
        
        # Collect candidates
        candidates = []
        for tid in type_ids:
            candidates.extend(self.by_type.get(tid, []))
        
        # Filter by rarity
        if min_rarity > 0:
            candidates = [c for c in candidates if c["rarity"] >= min_rarity]
        
        # Score each
        scored = []
        for item in candidates:
            s = self.score_item(item, weights)
            scored.append((item, s))
        
        # Sort by score descending
        scored.sort(key=lambda x: -x[1])
        
        return scored[:top_n]
    
    def recommend_full_build(self, weights=None, min_rarity=3):
        """
        Recommend best item for each slot.
        Respects Relic/Epic constraints.
        """
        if weights is None:
            weights = self.SRAM_MELEE_WEIGHTS
        
        build = {}
        used_relic = False
        used_epic = False
        
        slots_order = [
            "weapon", "amulet", "ring1", "ring2", "boots",
            "belt", "breastplate", "epaulettes", "helmet", "cloak",
            "second_hand", "emblem", "pet", "mount"
        ]
        
        for slot in slots_order:
            candidates = self.recommend(slot, weights, top_n=50, min_rarity=min_rarity)
            
            for item, score in candidates:
                # Check constraints
                if item["rarity"] == 5 and used_relic:
                    continue
                if item["rarity"] == 7 and used_epic:
                    continue
                # No duplicate ring
                if slot == "ring2" and "ring1" in build:
                    if item["id"] == build["ring1"][0]["id"]:
                        continue
                # 2H weapon blocks second_hand
                if slot == "second_hand" and "weapon" in build:
                    w = build["weapon"][0]
                    if w["itemTypeId"] in WEAPON_2H_TYPES:
                        break
                
                build[slot] = (item, score)
                if item["rarity"] == 5:
                    used_relic = True
                if item["rarity"] == 7:
                    used_epic = True
                break
        
        return build


# ══════════════════════════════════════════════════════════
#                         M A I N
# ══════════════════════════════════════════════════════════
if __name__ == "__main__":
    log.info("=" * 60)
    log.info("WAKFU EQUIPMENT SYSTEM — BUILD + RECOMMEND")
    log.info("=" * 60)
    
    # Load items
    items_path = os.path.join(DATA_DIR, "all_items.json")
    log.info(f"Loading items from {items_path}")
    with open(items_path, "r", encoding="utf-8") as f:
        all_items = json.load(f)
    log.info(f"Loaded {len(all_items)} items")
    
    # Build items index by ID
    items_by_id = {item["id"]: item for item in all_items}
    
    # ── TEST MODULE A: EquipmentManager ────────────────────
    log.info("\n" + "=" * 60)
    log.info("TEST MODULE A: EQUIPMENT MANAGER")
    log.info("=" * 60)
    
    em = EquipmentManager(character_level=179, items_db=items_by_id)
    
    # Find and equip a sample dagger for Sram
    daggers = [i for i in all_items if i["itemTypeId"] == 133 
               and i["level"] <= 179 and i["rarity"] >= 4]
    daggers.sort(key=lambda x: (-x["rarity"], -x["level"]))
    
    if daggers:
        ok, msg = em.equip(daggers[0])
        log.info(f"  -> {msg}")
    
    # Find and equip best items for other slots
    for slot_name, type_ids in [
        ("amulet", [101, 134]), ("ring1", [103, 136]), ("ring2", [103, 136]),
        ("boots", [112, 138]), ("belt", [115, 119]), ("breastplate", [113, 120]),
        ("epaulettes", [114]), ("helmet", [108]), ("cloak", [110]),
        ("emblem", [189])
    ]:
        candidates = [i for i in all_items 
                     if i["itemTypeId"] in type_ids 
                     and i["level"] <= 179 
                     and i["rarity"] >= 3]
        candidates.sort(key=lambda x: (-x["rarity"], -x["level"]))
        if candidates:
            ok, msg = em.equip(candidates[0], target_slot=slot_name)
    
    # Print full build summary
    log.info(em.summary())
    
    # ── TEST MODULE B: ItemRecommender ─────────────────────
    log.info("\n" + "=" * 60)
    log.info("TEST MODULE B: ITEM RECOMMENDER (Sram Melee DPS)")
    log.info("=" * 60)
    
    rec = ItemRecommender(all_items, character_level=179)
    
    # Top daggers for Sram
    log.info("\n--- TOP 10 DAGGERS (Sram Melee) ---")
    top_daggers = rec.recommend("weapon", top_n=10, min_rarity=3)
    for i, (item, score) in enumerate(top_daggers):
        rname = RARITY_NAMES.get(item["rarity"], "?")
        log.info(f"  #{i+1:>2} [{rname:>9}] {item['name_fr']} (Lvl {item['level']}) — Score: {score:.0f}")
        for stat, val in item.get("stats", {}).items():
            log.info(f"       {stat}: {val}")
    
    # Top amulets
    log.info("\n--- TOP 5 AMULETS (Sram Melee) ---")
    top_amulets = rec.recommend("amulet", top_n=5, min_rarity=3)
    for i, (item, score) in enumerate(top_amulets):
        rname = RARITY_NAMES.get(item["rarity"], "?")
        log.info(f"  #{i+1:>2} [{rname:>9}] {item['name_fr']} (Lvl {item['level']}) — Score: {score:.0f}")
        for stat, val in item.get("stats", {}).items():
            log.info(f"       {stat}: {val}")
    
    # Top boots
    log.info("\n--- TOP 5 BOOTS (Sram Melee) ---")
    top_boots = rec.recommend("boots", top_n=5, min_rarity=3)
    for i, (item, score) in enumerate(top_boots):
        rname = RARITY_NAMES.get(item["rarity"], "?")
        log.info(f"  #{i+1:>2} [{rname:>9}] {item['name_fr']} (Lvl {item['level']}) — Score: {score:.0f}")
        for stat, val in item.get("stats", {}).items():
            log.info(f"       {stat}: {val}")
    
    # ── FULL AUTO-BUILD ────────────────────────────────────
    log.info("\n" + "=" * 60)
    log.info("AUTO-BUILD: BEST SRAM MELEE BUILD (Lvl 179)")
    log.info("=" * 60)
    
    auto_build = rec.recommend_full_build(min_rarity=3)
    
    auto_em = EquipmentManager(character_level=179, items_db=items_by_id)
    for slot, (item, score) in auto_build.items():
        auto_em.equip(item, target_slot=slot)
    
    log.info(auto_em.summary())
    
    # Generate fighter profile
    base_sram = {
        "name": "L'Immortel",
        "class": "sram",
        "level": 179,
        "hp": 4800,      # Base HP without equipment
        "ap": 6,          # Base AP
        "mp": 3,          # Base MP
        "wp": 6,          # Base WP
        "masteries": {},
        "resistances": {"fire": 0, "water": 0, "earth": 0, "air": 0, "critical": 0, "rear": 0},
        "damage_inflicted": 0,
        "critical_hit": 3,
        "block": 0
    }
    
    full_profile = auto_em.get_fighter_profile(base_sram)
    log.info(f"\n--- MERGED FIGHTER PROFILE ---")
    log.info(f"  HP:  {full_profile['hp']}")
    log.info(f"  AP:  {full_profile['ap']}")
    log.info(f"  MP:  {full_profile['mp']}")
    log.info(f"  WP:  {full_profile['wp']}")
    log.info(f"  Crit Hit: {full_profile['critical_hit']}%")
    log.info(f"  Block:    {full_profile['block']}%")
    log.info(f"  Masteries:")
    for k, v in sorted(full_profile.get("masteries", {}).items()):
        if v != 0:
            log.info(f"    {k}: {v}")
    log.info(f"  Resistances:")
    for k, v in sorted(full_profile.get("resistances", {}).items()):
        if v != 0:
            log.info(f"    {k}: {v}")
    
    # ── SAVE MODULES ───────────────────────────────────────
    log.info("\n--- SAVING MODULES ---")
    
    # Save EquipmentManager + ItemRecommender as engine module
    module_path = os.path.join(ENGINE, "equipment.py")
    
    # Read this script and extract the classes
    with open(__file__, "r", encoding="utf-8") as f:
        source = f.read()
    
    # Write engine module (everything above __main__)
    marker = 'if __name__ == "__main__":'
    idx = source.find(marker)
    if idx > 0:
        module_code = source[:idx]
        module_code += '\n# Auto-extracted from build_equipment_system.py\n'
        with open(module_path, "w", encoding="utf-8") as f:
            f.write(module_code)
        log.info(f"Saved engine module: {module_path} ({os.path.getsize(module_path):,} bytes)")
    
    log.info("\nDONE")
