"""
ENGINE / DAMAGE.PY
Formule officielle de calcul des degats de Wakfu.

Formule complete:
    Degats = Base x (1 + Maitrises/100) x Orientation x Crit x (1 + DI%/100) x (1 - Res%) x Pi(df%) - Barriere

Sources:
- MethodWakfu: https://methodwakfu.com/bien-debuter/informations-generales/
- Wiki Fandom: https://wakfu.fandom.com/wiki/Damage
- Formules officielles: https://sites.google.com/view/wakfucalc/en/guides/formulas

Termes:
- Maitrises: elementaire + melee/distance + dos + critique + berserk + zone/mono (tous additifs)
- DI%: tous additifs entre eux (Carnage, Assaut Brutal, Maitre des Ombres, etc.)
- df%: multiplicateurs SEPARES, se multiplient entre eux (Isole x1.5, bonus Mise a Mort, orientation, crit)
- Res%: 1 - 0.8^(flat/100), cap 90%
"""

import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import config
from utils.logger import setup_logger

logger = setup_logger(__name__)


# ============================================================
# RESISTANCE
# ============================================================

def flat_res_to_percent(flat_res):
    """
    Convertit la resistance plate en pourcentage.
    Formule: %Res = 1 - 0.8^(flat/100)
    Cap a 90% (soit 1032 flat).
    Les valeurs negatives (debuff) sont possibles.
    Source: https://methodwakfu.com/bien-debuter/informations-generales/
    """
    percent = (1.0 - math.pow(0.8, flat_res / 100.0)) * 100.0
    return min(percent, config.RESISTANCE_CAP)


def percent_res_to_flat(percent_res):
    """Conversion inverse: % vers flat."""
    if percent_res >= 100:
        return float("inf")
    return 100.0 * math.log(1.0 - percent_res / 100.0) / math.log(0.8)


# ============================================================
# MAITRISES (toutes additives entre elles)
# ============================================================

def compute_total_mastery(stats, spell_element, is_melee, is_rear, is_critical,
                          is_berserk=False, is_area=False):
    """
    Calcule la somme des maitrises applicables.
    Toutes les maitrises sont additives entre elles.
    
    Parametres:
        stats: dict des stats du personnage
        spell_element: "fire", "water", "air", "earth"
        is_melee: True si distance <= 2 cases
        is_rear: True si attaque de dos
        is_critical: True si coup critique
        is_berserk: True si PV <= 50%
        is_area: True si sort de zone
    """
    total = 0

    # Maitrise elementaire
    element_key = f"mastery_{spell_element}"
    total += stats.get(element_key, 0)

    # Melee ou Distance
    if is_melee:
        total += stats.get("mastery_melee", 0)
    else:
        total += stats.get("mastery_distance", 0)

    # Dos (si applicable et pas Localisation Quantique)
    if is_rear:
        total += stats.get("mastery_rear", 0)

    # Critique (si coup critique)
    if is_critical:
        total += stats.get("mastery_critical", 0)

    # Berserk (si PV <= 50%)
    if is_berserk:
        total += stats.get("mastery_berserk", 0)

    # Zone ou Monocible
    if is_area:
        total += stats.get("mastery_area", 0)
    else:
        total += stats.get("mastery_single_target", 0)

    return total


# ============================================================
# CALCUL DES DEGATS
# ============================================================

def calculate_damage(base_damage, stats, spell_element, target_res_percent,
                     is_melee=True, is_rear=False, is_critical=False,
                     is_berserk=False, is_area=False,
                     di_percent=0, final_damage_multipliers=None,
                     barrier=0, orientation_override=None):
    """
    Calcul complet des degats selon la formule officielle de Wakfu.
    
    Formule:
        Base x (1 + Maitrises/100) x Orientation x Crit x (1 + DI%/100) x (1 - Res%) x Pi(df%) - Barriere
    
    Parametres:
        base_damage: valeur de base du sort
        stats: dict des stats du personnage
        spell_element: "fire", "water", "air", "earth"
        target_res_percent: resistance de la cible en % (0-90)
        is_melee: distance <= 2 cases
        is_rear: attaque de dos
        is_critical: coup critique
        is_berserk: PV <= 50%
        is_area: sort de zone
        di_percent: somme de tous les %DI (additifs entre eux)
        final_damage_multipliers: liste de %df individuels [50, 10, 20] -> x1.5 x1.1 x1.2
        barrier: armure de la cible (soustraction plate)
        orientation_override: force une orientation (pour Localisation Quantique)
    
    Retourne:
        dict avec le detail de chaque etape du calcul
    """
    if final_damage_multipliers is None:
        final_damage_multipliers = []

    # Etape 1: Maitrises
    total_mastery = compute_total_mastery(
        stats, spell_element, is_melee, is_rear, is_critical, is_berserk, is_area
    )
    mastery_factor = 1.0 + total_mastery / 100.0

    # Etape 2: Orientation
    if orientation_override is not None:
        orientation_factor = orientation_override
    elif is_rear:
        orientation_factor = config.ORIENTATION_REAR
    else:
        orientation_factor = config.ORIENTATION_FRONT

    # Etape 3: Critique
    crit_factor = config.CRITICAL_MULTIPLIER if is_critical else 1.0

    # Etape 4: DI% (plancher a -50%)
    effective_di = max(di_percent, config.DI_FLOOR)
    di_factor = 1.0 + effective_di / 100.0

    # Etape 5: Resistance
    capped_res = min(target_res_percent, config.RESISTANCE_CAP)
    res_factor = 1.0 - capped_res / 100.0

    # Etape 6: Dommages finaux (multiplicateurs separes)
    df_product = 1.0
    for df in final_damage_multipliers:
        df_product *= (1.0 + df / 100.0)

    # Calcul final
    raw_damage = base_damage * mastery_factor * orientation_factor * crit_factor
    after_di = raw_damage * di_factor
    after_res = after_di * res_factor
    after_df = after_res * df_product
    final = max(0, after_df - barrier)

    result = {
        "base_damage": base_damage,
        "total_mastery": total_mastery,
        "mastery_factor": round(mastery_factor, 4),
        "orientation_factor": orientation_factor,
        "is_critical": is_critical,
        "crit_factor": crit_factor,
        "di_percent": effective_di,
        "di_factor": round(di_factor, 4),
        "target_res_percent": capped_res,
        "res_factor": round(res_factor, 4),
        "final_damage_multipliers": final_damage_multipliers,
        "df_product": round(df_product, 4),
        "barrier": barrier,
        "raw_damage": round(raw_damage, 1),
        "after_di": round(after_di, 1),
        "after_res": round(after_res, 1),
        "after_df": round(after_df, 1),
        "final_damage": round(final, 1),
    }

    return result


# ============================================================
# TEST RAPIDE
# ============================================================

if __name__ == "__main__":
    print("=== Test de la formule de degats ===")
    print()

    # Test sur Sacapatate 0% res avec les stats de L'Immortel
    # Sort fictif: 100 de base, feu, melee, de face, non-critique
    from data.profiles.limmortel import PROFILE

    result = calculate_damage(
        base_damage=100,
        stats=PROFILE,
        spell_element="fire",
        target_res_percent=0,
        is_melee=True,
        is_rear=False,
        is_critical=False,
        di_percent=PROFILE["damage_inflicted"],
    )

    print("Sort: 100 base, Feu, Melee, Face, Non-crit, Sacapatate 0%")
    for key, val in result.items():
        print(f"  {key}: {val}")

    print()
    print(f"  Degats finaux: {result['final_damage']}")

    # Meme chose mais critique + dos + isole
    result2 = calculate_damage(
        base_damage=100,
        stats=PROFILE,
        spell_element="fire",
        target_res_percent=0,
        is_melee=True,
        is_rear=True,
        is_critical=True,
        di_percent=PROFILE["damage_inflicted"],
        final_damage_multipliers=[50],  # Isole = x1.5
    )

    print("Sort: 100 base, Feu, Melee, Dos, Crit, Isole, Sacapatate 0%")
    for key, val in result2.items():
        print(f"  {key}: {val}")

    print()
    print(f"  Degats finaux: {result2['final_damage']}")
