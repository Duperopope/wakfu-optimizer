###############################################################################
# H:\Code\Ankama Dev\wakfu-optimizer\scripts\test_integral_v3.py
#
# Test intégral V3 — FINAL — pipeline complet
#
# Correction unique par rapport à V2: le mapping EQUIP_TO_PROFILE
# utilise les clés EXACTES retournées par EquipmentManager.calculate_stats():
#   'hp', 'ap', 'mp', 'wp', 'melee_mastery', 'air_resistance', etc.
#
# Sources:
#   - Wakfu damage: https://wakfu.wiki.gg/wiki/Damage
#   - CDN: https://wakfu.cdn.ankama.com/gamedata/config.json
#   - Effects: https://dev.to/heymarkkop/decoding-wakfu-s-action-effects-with-javascript-1nm2
#
# Usage:  cd "H:\Code\Ankama Dev\wakfu-optimizer"
#         python scripts\test_integral_v3.py
###############################################################################

import json
import sys
import logging
from pathlib import Path
from datetime import datetime
from collections import defaultdict

PROJECT_ROOT = Path(r"H:\Code\Ankama Dev\wakfu-optimizer")
DATA_DIR = PROJECT_ROOT / "data" / "extracted"
ENGINE_DIR = PROJECT_ROOT / "engine"
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(ENGINE_DIR))
sys.path.insert(0, str(PROJECT_ROOT))

log_file = LOG_DIR / f"test_integral_v3_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_file, encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)
log = logging.getLogger("test_v3")

results = {"pass": 0, "fail": 0, "tests": []}


def test(name, condition, detail=""):
    status = "PASS" if condition else "FAIL"
    results["pass" if condition else "fail"] += 1
    results["tests"].append({"name": name, "status": status, "detail": detail})
    icon = "+" if condition else "X"
    log.info(f"  [{icon}] {name}" + (f" — {detail}" if detail else ""))
    return condition


def section(title):
    log.info("")
    log.info("=" * 70)
    log.info(f"  {title}")
    log.info("=" * 70)


# =========================================================================
#  PHASE 0 — IMPORTS
# =========================================================================
section("PHASE 0 — IMPORTS")

from fighter import Fighter
test("Import Fighter", True)

from effect_bridge import SpellExecutor, ACTION_HANDLERS
test("Import SpellExecutor", True, f"{len(ACTION_HANDLERS)} handlers")

from equipment import EquipmentManager, ItemRecommender
test("Import Equipment", True)


# =========================================================================
#  PHASE 1 — DONNÉES
# =========================================================================
section("PHASE 1 — CHARGEMENT DONNÉES")

with open(DATA_DIR / "all_items.json", "r", encoding="utf-8") as f:
    items = json.load(f)
test("Items", len(items) > 0, f"{len(items)} items")

with open(DATA_DIR / "all_spells.json", "r", encoding="utf-8") as f:
    spells = json.load(f)
test("Spells", len(spells) > 0, f"{len(spells)} sorts")

with open(DATA_DIR / "all_static_effects.json", "r", encoding="utf-8") as f:
    static_effects = json.load(f)
test("Static Effects", len(static_effects) > 0, f"{len(static_effects)} effets")

with open(DATA_DIR / "all_states.json", "r", encoding="utf-8") as f:
    states = json.load(f)
test("States", len(states) > 0, f"{len(states)} états")

with open(DATA_DIR / "action_map.json", "r", encoding="utf-8") as f:
    action_map = json.load(f)
test("Action Map", len(action_map) > 0, f"{len(action_map)} actions")


# =========================================================================
#  PHASE 2 — ÉQUIPEMENT
# =========================================================================
section("PHASE 2 — BUILD ÉQUIPEMENT SRAM LVL 179")

CHARACTER_LEVEL = 179

recommender = ItemRecommender(items, CHARACTER_LEVEL)
manager = EquipmentManager(CHARACTER_LEVEL)

raw_build = recommender.recommend_full_build(min_rarity=3)

build_items = {}
build_scores = {}
for slot, value in raw_build.items():
    if value is None:
        continue
    if isinstance(value, tuple):
        item_dict, score = value
        build_items[slot] = item_dict
        build_scores[slot] = score
    elif isinstance(value, dict):
        build_items[slot] = value
        build_scores[slot] = 0

for slot, item in build_items.items():
    manager.equip(item, target_slot=slot)

build_stats = manager.calculate_stats()
equipped_count = len(build_items)

test("Auto-build", equipped_count >= 10, f"{equipped_count} slots")
test("Stats calculées", len(build_stats) > 0, f"{len(build_stats)} stats")

log.info("\n  --- Build ---")
for slot in sorted(build_items.keys()):
    item = build_items[slot]
    log.info(f"    {slot:15s} [{item.get('rarity_name','?'):10s}] "
             f"{item.get('name_fr','?')} (L{item.get('level','?')})")

log.info("\n  --- Stats Brutes ---")
for stat, val in sorted(build_stats.items()):
    if val != 0:
        log.info(f"    {stat:45s} : {val:+.0f}")


# =========================================================================
#  PHASE 3 — FIGHTERS
# =========================================================================
section("PHASE 3 — CRÉATION FIGHTERS")

# -----------------------------------------------------------------------
# MAPPING CORRIGÉ: clés EXACTES de build_stats -> clés profile_to_stats
#
# build_stats retourne (minuscule snake_case):
#   hp, ap, mp, wp, critical_hit, block, dodge, lock,
#   melee_mastery, berserk_mastery, elemental_mastery,
#   random_elemental_mastery, fire_resistance, air_resistance, etc.
#
# profile_to_stats() attend:
#   hp, ap, mp, wp, critical_hit, block, dodge, lock,
#   mastery_fire, mastery_melee, mastery_berserk,
#   res_fire, res_air, damage_inflicted, etc.
# -----------------------------------------------------------------------
EQUIP_TO_PROFILE = {
    # Directs (même nom)
    "hp": "hp",
    "ap": "ap",
    "mp": "mp",
    "wp": "wp",
    "critical_hit": "critical_hit",
    "block": "block",
    "dodge": "dodge",
    "lock": "lock",
    "initiative": "initiative",
    "force_of_will": "force_of_will",
    "wisdom": "wisdom",
    "damage_inflicted": "damage_inflicted",
    # Masteries: build "xxx_mastery" -> profile "mastery_xxx"
    "melee_mastery": "mastery_melee",
    "distance_mastery": "mastery_distance",
    "rear_mastery": "mastery_rear",
    "critical_mastery": "mastery_critical",
    "berserk_mastery": "mastery_berserk",
    "healing_mastery": "mastery_healing",
    "area_mastery": "mastery_area",
    "single_target_mastery": "mastery_single_target",
    # Résistances: build "xxx_resistance" -> profile "res_xxx"
    "fire_resistance": "res_fire",
    "water_resistance": "res_water",
    "earth_resistance": "res_earth",
    "air_resistance": "res_air",
}

base_profile = {
    "hp": 4800, "ap": 6, "mp": 3, "wp": 6,
    "level": CHARACTER_LEVEL, "class": "sram",
    "mastery_fire": 0, "mastery_water": 0,
    "mastery_earth": 0, "mastery_air": 0,
    "mastery_melee": 0, "mastery_distance": 0,
    "mastery_critical": 0, "mastery_berserk": 0,
    "mastery_rear": 0, "mastery_healing": 0,
    "mastery_area": 0, "mastery_single_target": 0,
    "res_fire": 55, "res_water": 55,
    "res_earth": 55, "res_air": 55,
    "critical_hit": 3, "block": 0,
    "dodge": 30, "lock": 30,
    "initiative": 50, "force_of_will": 0,
    "damage_inflicted": 0,
}

equipped_profile = dict(base_profile)

# Appliquer les stats d'équipement
unmapped_keys = []
for stat_key, stat_val in build_stats.items():
    profile_key = EQUIP_TO_PROFILE.get(stat_key)

    if profile_key and profile_key in equipped_profile:
        equipped_profile[profile_key] += stat_val

    elif stat_key == "elemental_mastery":
        # Mastery fixe sur les 4 éléments
        for elem in ["mastery_fire", "mastery_water", "mastery_earth", "mastery_air"]:
            equipped_profile[elem] += stat_val

    elif stat_key == "random_elemental_mastery":
        # Mastery aléatoire sur N éléments -> on distribue sur les 4
        # (approximation: en jeu c'est sur 3 éléments choisis)
        for elem in ["mastery_fire", "mastery_water", "mastery_earth", "mastery_air"]:
            equipped_profile[elem] += stat_val

    elif stat_key == "elemental_resistance":
        # Résistance fixe sur les 4 éléments
        for elem in ["res_fire", "res_water", "res_earth", "res_air"]:
            equipped_profile[elem] += stat_val

    elif stat_key == "random_elemental_mastery_nb_elements":
        pass  # Métadonnée, pas une stat

    elif stat_key == "range":
        pass  # Non utilisé dans le profil combat

    else:
        unmapped_keys.append(stat_key)

if unmapped_keys:
    log.warning(f"  Clés non mappées: {unmapped_keys}")

# Dummy avec résistances
dummy_profile = {
    "hp": 10000, "ap": 0, "mp": 0, "wp": 0,
    "level": CHARACTER_LEVEL, "class": "dummy",
    "res_fire": 200, "res_water": 200,
    "res_earth": 200, "res_air": 200,
    "critical_hit": 0, "block": 0,
}

# Créer les fighters
sram_base = Fighter(
    name="Sram_Base", team="A", fighter_type="player",
    level=CHARACTER_LEVEL, class_name="sram", profile=base_profile
)
test("Sram_Base", sram_base.hp == 4800,
     f"HP:{sram_base.hp} AP:{sram_base.ap} "
     f"m.fire:{sram_base.stats['masteries']['fire']} "
     f"res:{sram_base.stats['res_fire']}")

sram_equipped = Fighter(
    name="Sram_Equipped", team="A", fighter_type="player",
    level=CHARACTER_LEVEL, class_name="sram", profile=equipped_profile
)

eq_hp = sram_equipped.max_hp
eq_ap = sram_equipped.ap
eq_mf = sram_equipped.stats["masteries"]["fire"]
eq_mm = sram_equipped.stats["masteries"]["melee"]
eq_rf = sram_equipped.stats["res_fire"]

test("Sram_Equipped HP up", eq_hp > 4800,
     f"HP:{eq_hp} (base 4800 + {build_stats.get('hp',0):.0f})")
test("Sram_Equipped AP up", eq_ap > 6,
     f"AP:{eq_ap} (base 6 + {build_stats.get('ap',0):.0f})")
test("Masteries > 0", eq_mf > 0,
     f"fire:{eq_mf} melee:{eq_mm}")
test("Résistances équipées > base", eq_rf > 55,
     f"res_fire:{eq_rf}")

# Comparaison
log.info("\n  --- Comparaison Base vs Équipé ---")
compare = [
    ("HP", sram_base.max_hp, eq_hp),
    ("AP", sram_base.ap, eq_ap),
    ("MP", sram_base.mp, sram_equipped.mp),
    ("WP", sram_base.wp, sram_equipped.wp),
    ("Crit", sram_base.stats.get("critical_hit", 0), sram_equipped.stats.get("critical_hit", 0)),
    ("Block", sram_base.stats.get("block", 0), sram_equipped.stats.get("block", 0)),
    ("Dodge", sram_base.stats.get("dodge", 0), sram_equipped.stats.get("dodge", 0)),
    ("Lock", sram_base.stats.get("lock", 0), sram_equipped.stats.get("lock", 0)),
    ("DI%", sram_base.stats.get("damage_inflicted", 0), sram_equipped.stats.get("damage_inflicted", 0)),
]
for e in ["fire", "water", "earth", "air", "melee", "rear", "critical", "berserk"]:
    compare.append((f"M.{e}",
                     sram_base.stats["masteries"].get(e, 0),
                     sram_equipped.stats["masteries"].get(e, 0)))
for e in ["fire", "water", "earth", "air"]:
    compare.append((f"R.{e}",
                     sram_base.stats.get(f"res_{e}", 0),
                     sram_equipped.stats.get(f"res_{e}", 0)))

for name, bv, ev in compare:
    diff = ev - bv
    marker = f"(+{diff:.0f})" if diff > 0 else f"({diff:.0f})" if diff < 0 else ""
    log.info(f"    {name:20s} : {bv:>8.0f} -> {ev:>8.0f}  {marker}")


# =========================================================================
#  PHASE 4 — COMBAT
# =========================================================================
section("PHASE 4 — SIMULATION DE COMBAT")

executor = SpellExecutor()
spell_lookup = {s["id"]: s for s in spells if isinstance(s, dict) and "id" in s}
sram_spell_ids = [3115, 3101, 3116, 3146, 4581]
found_spells = [sid for sid in sram_spell_ids if sid in spell_lookup]
test("Sorts trouvés", len(found_spells) >= 3, f"{found_spells}")

def run_combat(fighter, label):
    """Lance tous les sorts et retourne le total de dégâts."""
    total = 0.0
    log.info(f"\n  --- {label} ---")
    log.info(f"  Caster: m.fire={fighter.stats['masteries']['fire']} "
             f"m.melee={fighter.stats['masteries']['melee']} "
             f"DI={fighter.stats.get('damage_inflicted',0)}")
    for sid in found_spells:
        d = Fighter(name=f"D_{sid}", team="B", fighter_type="monster",
                    level=CHARACTER_LEVEL, class_name="dummy",
                    profile={"hp": 10000, "ap": 0, "mp": 0, "wp": 0})
        hp_before = d.hp
        executor.cast(caster=fighter, spell_id=sid, target=d)
        dmg = round(hp_before - d.hp, 1)
        total += dmg
        log.info(f"    Sort {sid}: {dmg} dmg")
    log.info(f"  Total: {total}")
    return total

total_base = run_combat(sram_base, "Sram_Base vs Dummy (0 res)")
test("Base > 0 dmg", total_base > 0, f"{total_base}")

total_equipped = run_combat(sram_equipped, "Sram_Equipped vs Dummy (0 res)")
test("Équipé > 0 dmg", total_equipped > 0, f"{total_equipped}")

if total_base > 0:
    ratio = total_equipped / total_base
    log.info(f"\n  RATIO: x{ratio:.2f} (+{(ratio-1)*100:.1f}%)")
    test("Équipement boost dmg", total_equipped > total_base * 2,
         f"x{ratio:.2f} ({total_base:.0f} -> {total_equipped:.0f})")

# Vs Résistant
log.info("")
total_vs_resist = 0.0
log.info("  --- Sram_Equipped vs Dummy Résistant (200 flat res) ---")
for sid in found_spells:
    d = Fighter(name=f"D_r_{sid}", team="B", fighter_type="monster",
                level=CHARACTER_LEVEL, class_name="dummy",
                profile=dummy_profile)
    hp_before = d.hp
    executor.cast(caster=sram_equipped, spell_id=sid, target=d)
    dmg = round(hp_before - d.hp, 1)
    total_vs_resist += dmg
    log.info(f"    Sort {sid}: {dmg} dmg")
log.info(f"  Total vs résistant: {total_vs_resist}")
if total_equipped > 0:
    red = (1 - total_vs_resist / total_equipped) * 100
    test("Résistances réduisent dmg", total_vs_resist < total_equipped,
         f"-{red:.1f}% ({total_equipped:.0f} -> {total_vs_resist:.0f})")


# =========================================================================
#  PHASE 5 — STATES
# =========================================================================
section("PHASE 5 — ÉTATS SRAM")

executor_s = SpellExecutor()
for sid in [3114, 3129, 3136, 2956, 1579]:
    try:
        desc = executor_s.describe_state(sid)
        test(f"State {sid}", desc is not None, str(desc)[:120])
    except Exception as e:
        test(f"State {sid}", False, str(e))


# =========================================================================
#  PHASE 6 — COUVERTURE
# =========================================================================
section("PHASE 6 — COUVERTURE EFFECT BRIDGE")

unique_aids = set()
for eff in static_effects:
    if isinstance(eff, dict) and "m_actionId" in eff:
        unique_aids.add(eff["m_actionId"])

covered = unique_aids & set(ACTION_HANDLERS.keys())
coverage = len(covered) / len(unique_aids) * 100 if unique_aids else 0
test("Couverture > 20%", coverage > 20,
     f"{len(covered)}/{len(unique_aids)} ({coverage:.1f}%)")

not_covered = unique_aids - set(ACTION_HANDLERS.keys())
freq = defaultdict(int)
for eff in static_effects:
    if isinstance(eff, dict):
        aid = eff.get("m_actionId")
        if aid in not_covered:
            freq[aid] += 1

log.info(f"\n  Top 10 manquants:")
for aid, count in sorted(freq.items(), key=lambda x: -x[1])[:10]:
    name = action_map.get(str(aid), {}).get("effect", "???")
    log.info(f"    {aid:>5d} : {count:>5d}x — {name}")


# =========================================================================
#  RAPPORT FINAL
# =========================================================================
section("RAPPORT FINAL")

total_tests = results["pass"] + results["fail"]
log.info(f"  Tests passés:  {results['pass']} / {total_tests}")
log.info(f"  Tests échoués: {results['fail']} / {total_tests}")

if results["fail"] > 0:
    log.info("\n  Tests en échec:")
    for t in results["tests"]:
        if t["status"] == "FAIL":
            log.info(f"    [X] {t['name']} — {t['detail']}")

log.info(f"\n  --- Résumé Combat ---")
log.info(f"  Base  (m=0)           : {total_base:.0f} dmg")
log.info(f"  Équipé (m.fire={eq_mf} m.melee={eq_mm}): {total_equipped:.0f} dmg")
if total_base > 0:
    log.info(f"  Boost équipement      : x{total_equipped/total_base:.2f}")
log.info(f"  Vs Résistant (200 res): {total_vs_resist:.0f} dmg")

log.info(f"\n  --- Profil Final Sram Équipé ---")
log.info(f"  HP:{eq_hp} AP:{eq_ap} MP:{sram_equipped.mp} WP:{sram_equipped.wp}")
log.info(f"  Crit:{sram_equipped.stats.get('critical_hit',0)}% "
         f"Block:{sram_equipped.stats.get('block',0)}")
log.info(f"  Masteries: fire={eq_mf} water={sram_equipped.stats['masteries']['water']} "
         f"earth={sram_equipped.stats['masteries']['earth']} "
         f"air={sram_equipped.stats['masteries']['air']}")
log.info(f"  Melee={eq_mm} Berserk={sram_equipped.stats['masteries']['berserk']}")
log.info(f"  Res: fire={eq_rf} water={sram_equipped.stats.get('res_water',0)} "
         f"earth={sram_equipped.stats.get('res_earth',0)} "
         f"air={sram_equipped.stats.get('res_air',0)}")

log.info(f"\n  Log: {log_file}")

if results["fail"] == 0:
    log.info("\n  === PIPELINE 100% OPÉRATIONNEL ===")
else:
    log.info(f"\n  === {results['fail']} ÉCHEC(S) RESTANT(S) ===")
