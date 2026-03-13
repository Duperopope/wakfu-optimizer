"""
engine/damage.py - Moteur de calcul de degats WAKFU
Version 5.1 - Formule complete officielle

Formule de degats directs:
  Degats = (((Base * (1 + Sigma_Mastery/100) * Orientation * Crit
             * (1 + Sigma_DI/100) * (1 - %Res/100))
             + Degats_fixes)
             - Barriere)
             * Coeff_Blocage
             * Produit(%df)

Sources:
  - MethodWakfu: https://methodwakfu.com/bien-debuter/informations-generales/
  - WakfuCalc (Ectawem): https://sites.google.com/view/wakfucalc/en/guides/formulas
  - Wiki Damage: https://wakfu.fandom.com/wiki/Damage
"""

import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import config
from utils.logger import setup_logger

logger = setup_logger(__name__)


# ============================================================
# ADAPTATEUR DE PROFIL
# ============================================================

def profile_to_stats(profile):
    """Convertit un profil plat (data/profiles/*.py) en dict 'stats'
    avec sous-dict 'masteries' attendu par les fonctions de calcul.
    Permet de garder les profils simples et lisibles pour Sam
    tout en ayant une structure propre pour le moteur.
    """
    return {
        "masteries": {
            "fire": profile.get("mastery_fire", 0),
            "water": profile.get("mastery_water", 0),
            "earth": profile.get("mastery_earth", 0),
            "air": profile.get("mastery_air", 0),
            "melee": profile.get("mastery_melee", 0),
            "distance": profile.get("mastery_distance", 0),
            "rear": profile.get("mastery_rear", 0),
            "critical": profile.get("mastery_critical", 0),
            "berserk": profile.get("mastery_berserk", 0),
            "healing": profile.get("mastery_healing", 0),
            "area": profile.get("mastery_area", 0),
            "single_target": profile.get("mastery_single_target", 0),
        },
        "hp": profile.get("hp", 0),
        "ap": profile.get("ap", 0),
        "mp": profile.get("mp", 0),
        "wp": profile.get("wp", 0),
        "critical_hit": profile.get("critical_hit", 0),
        "block": profile.get("block", 0),
        "dodge": profile.get("dodge", 0),
        "lock": profile.get("lock", 0),
        "initiative": profile.get("initiative", 0),
        "wisdom": profile.get("wisdom", 0),
        "force_of_will": profile.get("force_of_will", 0),
        "damage_inflicted": profile.get("damage_inflicted", 0),
        "heals_performed": profile.get("heals_performed", 0),
        "res_fire": profile.get("res_fire", 0),
        "res_water": profile.get("res_water", 0),
        "res_earth": profile.get("res_earth", 0),
        "res_air": profile.get("res_air", 0),
    }


# ============================================================
# RESISTANCE
# ============================================================

def flat_res_to_percent(flat_res):
    """Convertit resistance flat en % resistance.
    Formule: %Res = 1 - 0.8^(flat / 100), arrondi vers le bas.
    Cap joueurs/invocations: 90% (atteint a 1032 flat).
    Monstres: pas de cap.
    Source: WakfuCalc 'Resistances'
    """
    if flat_res == 0:
        return 0.0
    percent = (1 - 0.8 ** (flat_res / 100)) * 100
    return percent


def percent_res_to_flat(percent_res):
    """Convertit % resistance en resistance flat.
    Formule: flat = 100 * log(1 - %Res/100) / log(0.8), arrondi vers le haut.
    Source: WakfuCalc 'Resistances'
    """
    if percent_res <= 0:
        return 0.0
    if percent_res >= 100:
        return float('inf')
    flat = 100 * math.log(1 - percent_res / 100) / math.log(0.8)
    return math.ceil(flat)


def compute_effective_resistance(target_elemental_res, is_critical=False, target_critical_res=0,
                                  is_rear=False, target_rear_res=0, is_player=True,
                                  resistance_removal=0):
    """Calcule la resistance effective totale.
    La resistance effective additionne:
      - Resistance elementaire correspondant a l'element du sort
      - Resistance critique SI coup critique
      - Resistance dos SI attaque de dos
    Puis on soustrait les retraits de resistance (cap -200 par joueur).
    Source: WakfuCalc, MethodWakfu section 1.1
    """
    total_flat = target_elemental_res

    if is_critical:
        total_flat += target_critical_res

    if is_rear:
        total_flat += target_rear_res

    total_flat -= min(abs(resistance_removal), 200)

    percent = flat_res_to_percent(total_flat)

    if is_player and percent > config.RESISTANCE_CAP:
        percent = config.RESISTANCE_CAP

    return {
        "total_flat": total_flat,
        "percent": round(percent, 2),
        "capped": is_player and percent >= config.RESISTANCE_CAP
    }


# ============================================================
# MAITRISES
# ============================================================

def compute_total_mastery(stats, element, is_melee=True, is_rear=False,
                          is_critical=False, is_berserk=False,
                          is_area=False, is_healing=False):
    """Calcule la somme additive des maitrises pertinentes.
    Source: WakfuCalc 'Sum of relevant masteries'

    Accepte soit un dict avec sous-dict 'masteries', soit un profil plat.
    """
    if "masteries" in stats:
        masteries = stats["masteries"]
    else:
        masteries = {
            "fire": stats.get("mastery_fire", 0),
            "water": stats.get("mastery_water", 0),
            "earth": stats.get("mastery_earth", 0),
            "air": stats.get("mastery_air", 0),
            "melee": stats.get("mastery_melee", 0),
            "distance": stats.get("mastery_distance", 0),
            "rear": stats.get("mastery_rear", 0),
            "critical": stats.get("mastery_critical", 0),
            "berserk": stats.get("mastery_berserk", 0),
            "healing": stats.get("mastery_healing", 0),
            "area": stats.get("mastery_area", 0),
            "single_target": stats.get("mastery_single_target", 0),
        }

    if element in ("light", "stasis"):
        elem_mastery = max(
            masteries.get("fire", 0),
            masteries.get("water", 0),
            masteries.get("earth", 0),
            masteries.get("air", 0)
        )
    else:
        elem_mastery = masteries.get(element, 0)

    total = elem_mastery

    if is_melee:
        total += masteries.get("melee", 0)
    else:
        total += masteries.get("distance", 0)

    if is_rear and not is_healing:
        total += masteries.get("rear", 0)

    if is_critical:
        total += masteries.get("critical", 0)

    if is_berserk:
        total += masteries.get("berserk", 0)

    if is_area:
        total += masteries.get("area", 0)
    else:
        total += masteries.get("single_target", 0)

    if is_healing:
        total += masteries.get("healing", 0)

    return total


# ============================================================
# %DI (DOMMAGES INFLIGES)
# ============================================================

def compute_total_di(caster_di=0, target_damage_received=0, conditional_di=0,
                     indirect_di=0, is_indirect=False, target_echaude=False):
    """Calcule le Sigma_%DI total (additif).
    Source: MethodWakfu section 2.2

    Regles:
      - %di du personnage (fiche)
      - %dommages recus de la cible (additif avec %di lanceur)
      - %di conditionnels (distance, melee, zone, monocible, etc.)
      - %di indirects si degats indirects
      - Echauffe (+30% dommages indirects recus) si indirect
      - Plancher: -50% (les conditionnels s'ajoutent APRES le plancher)
    """
    base_di = caster_di + target_damage_received

    if base_di < config.DI_FLOOR:
        base_di = config.DI_FLOOR

    total = base_di + conditional_di

    if is_indirect:
        total += indirect_di
        if target_echaude:
            total += 30

    return total


# ============================================================
# CALCUL DE DEGATS PRINCIPAL
# ============================================================

def calculate_damage(base_damage, stats, element="fire",
                     target_elemental_res=0, target_critical_res=0, target_rear_res=0,
                     target_is_player=True, resistance_removal=0,
                     is_melee=True, is_rear=False, is_critical=False,
                     is_berserk=False, is_area=False, is_indirect=False,
                     caster_di=0, target_damage_received=0, conditional_di=0,
                     indirect_di=0, target_echaude=False,
                     final_damage_multipliers=None,
                     fixed_damage=0, barrier=0,
                     block_type="none",
                     orientation_override=None):
    """Calcul de degats complet selon la formule officielle.

    Source: WakfuCalc + MethodWakfu + DESIGN_DOC.md section 3

    Parametres:
      stats : dict profil plat OU dict avec sous-dict 'masteries'
              (les deux formats sont acceptes)
    """

    total_mastery = compute_total_mastery(
        stats, element,
        is_melee=is_melee,
        is_rear=is_rear,
        is_critical=is_critical,
        is_berserk=is_berserk,
        is_area=is_area
    )
    mastery_factor = 1 + (total_mastery / 100)

    if orientation_override:
        orientation_key = orientation_override.upper()
    elif is_rear:
        orientation_key = "REAR"
    else:
        orientation_key = "FRONT"

    if is_indirect:
        orientation_factor = 1.0
    else:
        orientation_factor = config.ORIENTATION_MULTIPLIERS.get(orientation_key, 1.0)

    if is_critical:
        crit_factor = config.CRITICAL_MULTIPLIER
    else:
        crit_factor = 1.0

    total_di = compute_total_di(
        caster_di=caster_di,
        target_damage_received=target_damage_received,
        conditional_di=conditional_di,
        indirect_di=indirect_di,
        is_indirect=is_indirect,
        target_echaude=target_echaude
    )
    di_factor = 1 + (total_di / 100)

    res_data = compute_effective_resistance(
        target_elemental_res=target_elemental_res,
        is_critical=is_critical,
        target_critical_res=target_critical_res,
        is_rear=is_rear,
        target_rear_res=target_rear_res,
        is_player=target_is_player,
        resistance_removal=resistance_removal
    )
    res_factor = 1 - (res_data["percent"] / 100)

    core_damage = base_damage * mastery_factor * orientation_factor * crit_factor * di_factor * res_factor

    after_fixed = core_damage + fixed_damage

    after_barrier = max(0, after_fixed - barrier)

    block_coefficients = {
        "none": 1.0,
        "block": 0.80,
        "block_expert": 0.68
    }
    block_coeff = block_coefficients.get(block_type, 1.0)
    after_block = after_barrier * block_coeff

    df_product = 1.0
    df_list = final_damage_multipliers or []
    for df_val in df_list:
        df_product *= (1 + df_val / 100)
    final_damage = after_block * df_product

    final_damage = max(0, final_damage)

    result = {
        "base_damage": base_damage,
        "element": element,
        "total_mastery": total_mastery,
        "mastery_factor": round(mastery_factor, 4),
        "orientation": orientation_key,
        "orientation_factor": orientation_factor,
        "is_critical": is_critical,
        "crit_factor": crit_factor,
        "total_di": round(total_di, 2),
        "di_factor": round(di_factor, 4),
        "resistance_flat": res_data["total_flat"],
        "resistance_percent": res_data["percent"],
        "resistance_capped": res_data["capped"],
        "res_factor": round(res_factor, 4),
        "core_damage": round(core_damage, 2),
        "fixed_damage": fixed_damage,
        "after_fixed": round(after_fixed, 2),
        "barrier": barrier,
        "after_barrier": round(after_barrier, 2),
        "block_type": block_type,
        "block_coeff": block_coeff,
        "after_block": round(after_block, 2),
        "df_multipliers": df_list,
        "df_product": round(df_product, 4),
        "final_damage": round(final_damage, 1),
        "is_indirect": is_indirect,
    }

    logger.info(
        f"DMG: {base_damage} base | {element} | mastery {total_mastery} "
        f"| {orientation_key} x{orientation_factor} | crit={is_critical} "
        f"| DI={total_di}% | Res={res_data['percent']}% "
        f"| fixed={fixed_damage} | barrier={barrier} | block={block_type} "
        f"| df={df_list} | FINAL={round(final_damage, 1)}"
    )

    return result


# ============================================================
# CALCUL DE SOIN
# ============================================================

def calculate_heal(base_heal, stats, element="water",
                   is_melee=True, is_critical=False, is_berserk=False,
                   heals_performed=0, heals_received=0,
                   heal_resistance=0, incurable_level=0):
    """Calcul de soin selon la formule officielle.

    Source: WakfuCalc 'Heals', MethodWakfu section 2.3

    Formule:
      Soin = Base * (1 + Mastery/100) * Crit
             * (1 + (% Soins Realises + % Soins Recus)/100)
             * (1 - % Resistance Soin/100)
             * (1 - Incurable*10%/100)
    """

    total_mastery = compute_total_mastery(
        stats, element,
        is_melee=is_melee,
        is_rear=False,
        is_critical=is_critical,
        is_berserk=is_berserk,
        is_healing=True
    )
    mastery_factor = 1 + (total_mastery / 100)

    crit_factor = config.CRITICAL_MULTIPLIER if is_critical else 1.0

    heal_bonus_factor = 1 + ((heals_performed + heals_received) / 100)

    heal_res_factor = max(0, 1 - (heal_resistance / 100))

    incurable_factor = max(0, 1 - (incurable_level * 10 / 100))

    final_heal = (base_heal * mastery_factor * crit_factor
                  * heal_bonus_factor * heal_res_factor * incurable_factor)

    final_heal = max(0, final_heal)

    result = {
        "base_heal": base_heal,
        "total_mastery": total_mastery,
        "mastery_factor": round(mastery_factor, 4),
        "crit_factor": crit_factor,
        "heals_performed": heals_performed,
        "heals_received": heals_received,
        "heal_bonus_factor": round(heal_bonus_factor, 4),
        "heal_resistance": heal_resistance,
        "heal_res_factor": round(heal_res_factor, 4),
        "incurable_level": incurable_level,
        "incurable_factor": round(incurable_factor, 4),
        "final_heal": round(final_heal, 1),
    }

    logger.info(
        f"HEAL: {base_heal} base | mastery {total_mastery} "
        f"| crit={is_critical} | soins={heals_performed}%+{heals_received}% "
        f"| res_soin={heal_resistance}% | incurable={incurable_level} "
        f"| FINAL={round(final_heal, 1)}"
    )

    return result


# ============================================================
# CALCUL D'ARMURE
# ============================================================

def calculate_armor(base_armor, is_critical=False,
                    armor_given=0, armor_received=0,
                    friable_level=0, target_max_hp=0,
                    target_is_summon=False):
    """Calcul d'armure selon la formule officielle.

    Source: WakfuCalc 'Armors', MethodWakfu section 2.3

    Formule:
      Armure = Base * Crit * (1 + (% Armure Donnee + % Armure Recue)/100)
               * (1 - Friable*10%/100)
    """

    crit_factor = config.CRITICAL_MULTIPLIER if is_critical else 1.0

    armor_bonus_factor = 1 + ((armor_given + armor_received) / 100)

    friable_factor = max(0, 1 - (friable_level * 10 / 100))

    armor = base_armor * crit_factor * armor_bonus_factor * friable_factor

    if target_max_hp > 0:
        cap_percent = 1.0 if target_is_summon else 0.5
        cap = target_max_hp * cap_percent
        armor = min(armor, cap)

    armor = max(0, armor)

    return {
        "base_armor": base_armor,
        "crit_factor": crit_factor,
        "armor_given": armor_given,
        "armor_received": armor_received,
        "friable_level": friable_level,
        "friable_factor": round(friable_factor, 4),
        "final_armor": round(armor, 1),
        "cap_applied": target_max_hp > 0,
    }


# ============================================================
# FORMULES UTILITAIRES
# ============================================================

def compute_ehp(hp, resistance_percent, block_percent=0, has_block_expert=False):
    """Calcule les Effective Hit Points (EHP).
    Source: WakfuCalc 'EHP'

    EHP = (HP * 10000) / ((100 - %Res) * (100 - (1 - block_coeff) * %Block))
    """
    block_coeff = 0.68 if has_block_expert else 0.80
    res_term = max(1, 100 - resistance_percent)
    block_term = max(1, 100 - (1 - block_coeff) * block_percent)
    ehp = (hp * 10000) / (res_term * block_term)
    return round(ehp, 1)


def compute_em(total_mastery, total_di, critical_mastery=0, critical_di=0,
               crit_chance=0):
    """Calcule les Effective Masteries (EM, EMcrit, EM moyen).
    Source: WakfuCalc 'EM'
    """
    em = ((total_mastery + 100) * (total_di + 100) / 10000) - 100
    em_crit = (((total_mastery + critical_mastery + 100) * (total_di + critical_di + 100) / 10000) * 1.25) - 100
    cc = min(crit_chance, 100) / 100
    em_avg = em + ((em_crit - em) * cc)

    return {
        "em": round(em, 1),
        "em_crit": round(em_crit, 1),
        "em_average": round(em_avg, 1),
        "crit_chance_used": round(cc * 100, 1)
    }


def compute_hp(level, flat_hp_bonus=0, percent_hp_bonus=0):
    """Calcule les PV totaux.
    Source: WakfuCalc 'HP'

    Total HP = (50 + Level * 10 + flat_hp) * (1 + %hp/100)
    """
    base = 50 + (level * 10) + flat_hp_bonus
    total = base * (1 + percent_hp_bonus / 100)
    return round(total)


# ============================================================
# TESTS
# ============================================================

if __name__ == "__main__":
    from data.profiles.limmortel import PROFILE

    stats = profile_to_stats(PROFILE)

    print("=" * 60)
    print("  TESTS ENGINE/DAMAGE.PY V5.1")
    print("=" * 60)

    # --- Test 1: Face, non-crit, monstre 0% res ---
    r1 = calculate_damage(
        base_damage=100, stats=stats, element="fire",
        target_elemental_res=0, target_is_player=False,
        is_melee=True, is_rear=False, is_critical=False,
        caster_di=PROFILE["damage_inflicted"],
        orientation_override="front"
    )
    print(f"\nTest 1 - Face, non-crit, 0% res:")
    print(f"  Mastery: {r1['total_mastery']} | DI: {r1['total_di']}%")
    print(f"  Final: {r1['final_damage']}")

    # --- Test 2: Dos, crit, isole, monstre 0% res ---
    r2 = calculate_damage(
        base_damage=100, stats=stats, element="fire",
        target_elemental_res=0, target_is_player=False,
        is_melee=True, is_rear=True, is_critical=True,
        caster_di=PROFILE["damage_inflicted"],
        final_damage_multipliers=[50],
        orientation_override="rear"
    )
    print(f"\nTest 2 - Dos, crit, isole x1.5, 0% res:")
    print(f"  Mastery: {r2['total_mastery']} | DI: {r2['total_di']}%")
    print(f"  Final: {r2['final_damage']}")

    # --- Test 3: Avec resistance, blocage, barriere ---
    r3 = calculate_damage(
        base_damage=100, stats=stats, element="fire",
        target_elemental_res=400, target_critical_res=50, target_rear_res=0,
        target_is_player=False,
        is_melee=True, is_rear=False, is_critical=True,
        caster_di=PROFILE["damage_inflicted"],
        fixed_damage=20, barrier=100, block_type="block",
        orientation_override="front"
    )
    print(f"\nTest 3 - Crit, 400+50 res flat, +20 fixed, -100 barrier, bloque:")
    print(f"  Res flat: {r3['resistance_flat']} | Res%: {r3['resistance_percent']}%")
    print(f"  Core: {r3['core_damage']} | +fixed: {r3['after_fixed']}")
    print(f"  -barrier: {r3['after_barrier']} | x0.8 block: {r3['after_block']}")
    print(f"  Final: {r3['final_damage']}")

    # --- Test 4: %dommages recus de la cible ---
    r4 = calculate_damage(
        base_damage=100, stats=stats, element="fire",
        target_elemental_res=0, target_is_player=False,
        is_melee=True, is_rear=False, is_critical=False,
        caster_di=PROFILE["damage_inflicted"],
        target_damage_received=30,
        orientation_override="front"
    )
    print(f"\nTest 4 - Cible avec +30% dommages recus:")
    print(f"  DI total: {r4['total_di']}% (18 + 30 = 48)")
    print(f"  Final: {r4['final_damage']} (vs {r1['final_damage']} sans)")

    # --- Test 5: Degats indirects + Echauffe ---
    r5 = calculate_damage(
        base_damage=100, stats=stats, element="fire",
        target_elemental_res=0, target_is_player=False,
        is_melee=True, is_rear=True, is_critical=False,
        is_indirect=True,
        caster_di=PROFILE["damage_inflicted"],
        indirect_di=20, target_echaude=True,
        orientation_override="rear"
    )
    print(f"\nTest 5 - Indirect, dos, Echauffe:")
    print(f"  Orientation: {r5['orientation']} x{r5['orientation_factor']} (ignore en indirect)")
    print(f"  DI total: {r5['total_di']}% (18 + 20 indirect + 30 echauffe = 68)")
    print(f"  Mastery: {r5['total_mastery']} (pas de mastery dos en indirect)")
    print(f"  Final: {r5['final_damage']}")

    # --- Test 6: EHP ---
    ehp = compute_ehp(hp=PROFILE["hp"], resistance_percent=71, block_percent=0)
    print(f"\nTest 6 - EHP de L'Immortel (feu 71% res):")
    print(f"  EHP: {ehp}")

    # --- Test 7: EM ---
    mastery_face_fire = compute_total_mastery(stats, "fire", is_melee=True)
    em = compute_em(
        total_mastery=mastery_face_fire,
        total_di=PROFILE["damage_inflicted"],
        critical_mastery=PROFILE["mastery_critical"],
        critical_di=0,
        crit_chance=PROFILE["critical_hit"]
    )
    print(f"\nTest 7 - EM de L'Immortel (feu, face, melee):")
    print(f"  Mastery base: {mastery_face_fire}")
    print(f"  EM: {em['em']} | EMcrit: {em['em_crit']} | EM moyen: {em['em_average']}")

    # --- Test 8: HP ---
    hp = compute_hp(level=PROFILE["level"], flat_hp_bonus=0, percent_hp_bonus=0)
    print(f"\nTest 8 - PV base niveau {PROFILE['level']}: {hp}")

    # --- Test 9: Soin ---
    heal = calculate_heal(
        base_heal=50, stats=stats, element="water",
        is_melee=True, is_critical=False,
        heals_performed=PROFILE["heals_performed"], heals_received=0,
        heal_resistance=0, incurable_level=0
    )
    print(f"\nTest 9 - Soin eau 50 base, +{PROFILE['heals_performed']}% soins:")
    print(f"  Mastery: {heal['total_mastery']} | Final: {heal['final_heal']}")

    # --- Test 10: Armure ---
    armor = calculate_armor(
        base_armor=500, is_critical=True,
        armor_given=0, armor_received=0,
        friable_level=3, target_max_hp=PROFILE["hp"],
        target_is_summon=False
    )
    print(f"\nTest 10 - Armure 500 base, crit, Friable 3:")
    print(f"  Crit x{armor['crit_factor']} | Friable x{armor['friable_factor']}")
    print(f"  Final: {armor['final_armor']} (cap 50% de {PROFILE['hp']} = {PROFILE['hp']*0.5})")

    print(f"\n{'=' * 60}")
    print("  TOUS LES TESTS TERMINES")
    print(f"{'=' * 60}")
