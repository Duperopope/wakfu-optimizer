#!/usr/bin/env python3
"""
WAKFU SRAM OPTIMIZER V4.6 — Sublimation & Armor Engine
Sram "L'Immortel" — Level 179 — Patch 1.91
================================================================
NEW in V4.6 (from V4.5):
  FIX-1  Temerite persists across turns (was reset to 0 each turn)
  FIX-2  RNG: noise applied per-damage-roll + per-action-selection (no duplicate runs)
  FIX-3  MP cap realistic: BASE_MP + refunds capped at BASE_MP + 3 (max kill/PF bonus)
  FIX-4  Log decomposed: cost line, then PF refund line, then kill refund line
  FIX-5  Attaque Perfide penalized if not enough AP left to break armor this turn
  FIX-6  Rupture PA activations: 2 total (not 4), +2AP per activation (Niv.4 scroll)
  FIX-7  Rupture Violente activations: 2 total, 40% of level per activation

PRESERVED from V4.4/V4.5:
  - Full armor tracking (Attaque Perfide gives 40% as armor)
  - Sublimation triggers: Rupture PA, Rupture Violente, Temerite, Influence Lente
  - Ivory Dofus: +15% crit dmg on >=4AP or >=1WP
  - WP capped at BASE_WP (8)
  - Saignee Mortelle replica: +6 hemo + lifesteal
  - Per-worker RNG seed
"""

import random, time, math, os, sys
from multiprocessing import Pool, cpu_count, current_process
from collections import defaultdict, Counter
from copy import deepcopy

# ═══════════════════════════════════════════════════════════════════
#  CONSTANTS
# ═══════════════════════════════════════════════════════════════════
VERSION = "4.6"
LVL = 179
GRID_W, GRID_H = 14, 10
MAX_TURNS = 8
DECK_SLOTS = 12
PASSIVE_SLOTS = 5
SIMS_PER_LOADOUT = 100

BASE_AP = 13
BASE_MP = 5
BASE_WP = 8
WP_CAP  = 8
BASE_HP = 8920
BASE_CRIT = 0.72
START_PF = 50

# V4.6 FIX-3: realistic MP cap — base + max possible refunds per turn
# PF refund can give up to +4 MP (100 PF / 25 = 4 tiers), kill gives +1 MP
# But realistically in one turn: ~2 PF tiers + 1-2 kills = +4 MP max
MP_CAP_MAX = BASE_MP + 5  # = 10, generous but not infinite (was BASE_MP + 6 = 11)

MAST = {"fire": 808, "water": 808, "air": 425, "earth": 190}
MAST_CRIT = 456
MAST_REAR = 585
MAST_MELEE = 1030
MAST_BERSERK = -90

DMG_BONUS = 0.18
INNATE_ISO_BONUS = 0.50

RES_CAP = 0.90
PF_CAP = 100
HEMO_CAP = 40

# ── Sublimations ──
RUPTURE_PA_ACTIVATIONS = 2        # V4.6 FIX-6: 2 activations total per turn
RUPTURE_PA_GAIN = 2               # +2 AP per activation (Niv.4)
RUPTURE_VIOLENTE_ACTIVATIONS = 2  # V4.6 FIX-7: 2 activations total per turn
RUPTURE_VIOLENTE_DMG_PCT = 0.40   # 40% of level per activation
TEMERITE_PER_BREAK = 0.12         # +12% dmg per full armor break
TEMERITE_CAP = 0.30               # max 30% total

# Influence Lente (Slow Influence): +2% crit per turn, max 30%
INFLUENCE_LENTE_PER_TURN = 0.02
INFLUENCE_LENTE_CAP = 0.30

# Ivory Dofus: +15% crit dmg on spells costing >=4AP or >=1WP
IVORY_CRIT_DMG_BONUS = 0.15

# ═══════════════════════════════════════════════════════════════════
#  SPELL DEFINITIONS — exact 1.91 patch notes
# ═══════════════════════════════════════════════════════════════════

def _d(ap, ratio=20):
    return int(ap * ratio * (1 + LVL / 200))

SPELLS = {
    # ── FIRE ──
    "premier_sang": {
        "name": "Premier Sang", "element": "fire", "ap": 2, "wp": 0,
        "base_dmg": _d(2, 18), "range_min": 0, "range_max": 1,
        "aoe": "staff", "pf_generate": True, "pf_consume": False,
        "uses_per_turn": 3, "uses_per_target": 99,
        "hemo_apply": 10, "hemo_apply_if_already": 2,
        "melee": True, "line": False, "no_los": False,
        "special": "premier_sang",
    },
    "ouvrir_veines": {
        "name": "Ouvrir les Veines", "element": "fire", "ap": 2, "wp": 0,
        "base_dmg": _d(2, 18), "range_min": 0, "range_max": 1,
        "pf_generate": True, "pf_consume": False,
        "uses_per_turn": 3, "uses_per_target": 1,
        "hemo_apply": 0, "melee": True,
        "special": "ouvrir_veines",
    },
    "saignee_mortelle": {
        "name": "Saignee Mortelle", "element": "fire", "ap": 3, "wp": 0,
        "base_dmg": _d(3, 19), "range_min": 1, "range_max": 5,
        "pf_generate": True, "pf_consume": False,
        "uses_per_turn": 4, "uses_per_target": 3,
        "hemo_apply": 6, "melee": False, "line": True, "no_los": False,
        "special": "saignee_mortelle",
    },
    "chatiment": {
        "name": "Chatiment", "element": "fire", "ap": 4, "wp": 0,
        "base_dmg": _d(4, 20), "range_min": 0, "range_max": 0,
        "aoe": "cross1", "pf_generate": True, "pf_consume": False,
        "uses_per_turn": 2, "uses_per_target": 99,
        "hemo_apply": 0, "melee": True,
        "special": "chatiment",
    },
    "mise_a_mort": {
        "name": "Mise a Mort", "element": "fire", "ap": 6, "wp": 0,
        "base_dmg": _d(6, 22), "range_min": 0, "range_max": 1,
        "pf_generate": False, "pf_consume": True,
        "uses_per_turn": 1, "uses_per_target": 99,
        "hemo_apply": 0, "melee": True,
        "special": "mise_a_mort",
    },
    # ── WATER ──
    "kleptosram": {
        "name": "Kleptosram", "element": "water", "ap": 2, "wp": 0,
        "base_dmg": _d(2, 18), "range_min": 1, "range_max": 2,
        "pf_generate": True, "pf_consume": False,
        "uses_per_turn": 3, "uses_per_target": 99,
        "hemo_apply": 0, "melee": False, "line": True, "no_los": True,
        "special": "kleptosram",
    },
    "arnaque": {
        "name": "Arnaque", "element": "water", "ap": 2, "wp": 0,
        "base_dmg": _d(2, 18), "range_min": 1, "range_max": 2,
        "pf_generate": False, "pf_consume": True,
        "uses_per_turn": 3, "uses_per_target": 99,
        "hemo_apply": 0, "melee": False, "no_los": True,
        "special": "arnaque",
    },
    "attaque_letale": {
        "name": "Attaque Letale", "element": "water", "ap": 4, "wp": 0,
        "base_dmg": _d(4, 20), "range_min": 1, "range_max": 2,
        "pf_generate": True, "pf_consume": False,
        "uses_per_turn": 2, "uses_per_target": 99,
        "hemo_apply": 0, "melee": False, "no_los": True,
        "special": "attaque_letale",
    },
    "attaque_perfide": {
        "name": "Attaque Perfide", "element": "water", "ap": 3, "wp": 0,
        "base_dmg": _d(3, 22), "range_min": 1, "range_max": 2,
        "pf_generate": True, "pf_consume": False,
        "uses_per_turn": 3, "uses_per_target": 2,
        "hemo_apply": 0, "melee": False, "no_los": True,
        "special": "attaque_perfide",
    },
    "attaque_mortelle": {
        "name": "Attaque Mortelle", "element": "water", "ap": 5, "wp": 0,
        "base_dmg": _d(5, 21), "range_min": 1, "range_max": 2,
        "pf_generate": True, "pf_consume": False,
        "uses_per_turn": 99, "uses_per_target": 1,
        "hemo_apply": 0, "melee": False, "no_los": True,
        "special": "attaque_mortelle",
    },
    # ── AIR ──
    "coup_penetrant": {
        "name": "Coup Penetrant", "element": "air", "ap": 4, "wp": 0,
        "base_dmg": _d(4, 19), "range_min": 0, "range_max": 1,
        "aoe": "line3", "pf_generate": True, "pf_consume": False,
        "uses_per_turn": 2, "uses_per_target": 99,
        "hemo_apply": 0, "melee": True,
        "special": "coup_penetrant",
    },
    "fourberie": {
        "name": "Fourberie", "element": "air", "ap": 3, "wp": 0,
        "base_dmg": _d(3, 19), "range_min": 1, "range_max": 4,
        "pf_generate": True, "pf_consume": False,
        "uses_per_turn": 3, "uses_per_target": 1,
        "hemo_apply": 0, "melee": False, "line": True, "no_los": True,
        "special": "fourberie",
    },
    "coup_sournois": {
        "name": "Coup Sournois", "element": "air", "ap": 3, "wp": 0,
        "base_dmg": _d(3, 19), "range_min": 0, "range_max": 1,
        "pf_generate": True, "pf_consume": False,
        "uses_per_turn": 4, "uses_per_target": 1,
        "hemo_apply": 0, "melee": True,
        "special": "coup_sournois",
    },
    "effroi": {
        "name": "Effroi", "element": "air", "ap": 3, "wp": 0,
        "base_dmg": _d(3, 19), "range_min": 0, "range_max": 1,
        "pf_generate": True, "pf_consume": False,
        "uses_per_turn": 3, "uses_per_target": 2,
        "hemo_apply": 0, "melee": True,
        "special": "effroi",
    },
    "traumatisme": {
        "name": "Traumatisme", "element": "air", "ap": 4, "wp": 0,
        "base_dmg": _d(4, 20), "range_min": 1, "range_max": 4,
        "pf_generate": False, "pf_consume": True,
        "uses_per_turn": 2, "uses_per_target": 99,
        "hemo_apply": 0, "melee": True, "line": True, "no_los": True,
        "special": "traumatisme",
    },
    # ── NEUTRAL ──
    "assassinat": {
        "name": "Assassinat", "element": "neutral", "ap": 1, "wp": 2,
        "base_dmg": 0, "range_min": 1, "range_max": 3,
        "pf_generate": False, "pf_consume": False,
        "uses_per_turn": 1, "uses_per_target": 99,
        "hemo_apply": 0, "melee": False, "line": True,
        "special": "assassinat", "cooldown": 2,
    },
    "peur": {
        "name": "Peur", "element": "neutral", "ap": 2, "wp": 0,
        "base_dmg": 0, "range_min": 2, "range_max": 5,
        "pf_generate": False, "pf_consume": False,
        "uses_per_turn": 3, "uses_per_target": 99,
        "hemo_apply": 0, "melee": False, "line": True, "no_los": True,
        "special": "peur",
    },
    "surineur": {
        "name": "Surineur", "element": "neutral", "ap": 2, "wp": 0,
        "base_dmg": 0, "range_min": 0, "range_max": 0,
        "pf_generate": False, "pf_consume": False,
        "uses_per_turn": 1, "uses_per_target": 99,
        "hemo_apply": 0, "melee": True,
        "special": "surineur", "cooldown": 2,
    },
    "galopade": {
        "name": "Galopade", "element": "neutral", "ap": 0, "wp": 1,
        "base_dmg": 0, "range_min": 0, "range_max": 3,
        "pf_generate": False, "pf_consume": False,
        "uses_per_turn": 1, "uses_per_target": 99,
        "hemo_apply": 0, "special": "galopade", "cooldown": 2,
    },
}

# ═══════════════════════════════════════════════════════════════════
#  PASSIVES
# ═══════════════════════════════════════════════════════════════════
PASSIVES_DATA = {
    "assassin": "On kill: no PF gain, +1AP/PM/WP + heal 20% max HP",
    "localisation_quantique": "Start: rear -> melee. Ignore target orientation.",
    "carnage": "+30% damage, -20% HP max",
    "evasion": "+100% level as dodge",
    "assaut_brutal": "Spells >=4AP: no PF gen, +5% dmg per AP",
    "interception": "+100% level as lock",
    "inspiration": "+2 range, -40% dmg on melee spells",
    "embuscade": "Traps: no AP refund, +1WP on trigger, traps deal 3AP melee dmg",
    "leurre": "Double explodes: 50% HP dmg circle 2, +20 hemo",
    "retenue": "Invis: can't target allies, revealed only >=4AP",
    "motivation": "+1AP, -20% dmg, +10 willpower",
    "hemophilie": "End turn: hemo -> hemophilia (4% lvl per hemo lvl, dmg start of turn)",
    "duperie": "After direct dmg: swap with Double",
    "passe_passe": "Double: 4 range line no LoS, swap on summon + end of turn",
}

# ═══════════════════════════════════════════════════════════════════
#  ENEMY CONFIGURATIONS
# ═══════════════════════════════════════════════════════════════════
COMBATS = {
    "donjon_standard": [
        {"name": "Mob Std A",    "hp": 2800, "res": 0.35, "mp": 3, "pos": (4, 4), "dmg": 150},
        {"name": "Mob Std B",    "hp": 2800, "res": 0.35, "mp": 3, "pos": (6, 3), "dmg": 150},
        {"name": "Boss Tanky",   "hp": 5500, "res": 0.50, "mp": 2, "pos": (2, 3), "dmg": 250},
        {"name": "Invoc",        "hp": 1500, "res": 0.20, "mp": 4, "pos": (5, 4), "dmg": 100},
        {"name": "Tank Phys",    "hp": 3600, "res": 0.55, "mp": 2, "pos": (3, 7), "dmg": 200},
        {"name": "DPS Fragile",  "hp": 1800, "res": 0.25, "mp": 5, "pos": (8, 5), "dmg": 300},
    ],
    "boss_rush": [
        {"name": "Boss Alpha",  "hp": 12000, "res": 0.55, "mp": 2, "pos": (4, 3), "dmg": 400},
        {"name": "Boss Beta",   "hp":  9000, "res": 0.50, "mp": 3, "pos": (6, 5), "dmg": 350},
        {"name": "Boss Gamma",  "hp":  7000, "res": 0.45, "mp": 3, "pos": (3, 6), "dmg": 300},
    ],
    "salle_variee": [
        {"name": "Melee A",      "hp": 3000, "res": 0.40, "mp": 4, "pos": (3, 3), "dmg": 200},
        {"name": "Melee B",      "hp": 3000, "res": 0.40, "mp": 4, "pos": (5, 3), "dmg": 200},
        {"name": "Rangeur",      "hp": 2200, "res": 0.30, "mp": 3, "pos": (7, 6), "dmg": 250},
        {"name": "Support",      "hp": 2500, "res": 0.35, "mp": 2, "pos": (2, 6), "dmg": 100},
        {"name": "Tank",         "hp": 4500, "res": 0.55, "mp": 2, "pos": (4, 5), "dmg": 150},
        {"name": "Glass Canon",  "hp": 1500, "res": 0.20, "mp": 5, "pos": (9, 4), "dmg": 400},
    ],
}

SRAM_START_POS = (1, 4)

# ═══════════════════════════════════════════════════════════════════
#  UTILITY
# ═══════════════════════════════════════════════════════════════════

def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def cap_wp(sram):
    sram["wp"] = min(WP_CAP, sram["wp"])

def cap_mp(sram):
    # V4.6 FIX-3: cap MP to a realistic maximum
    sram["mp"] = min(MP_CAP_MAX, sram["mp"])

def init_worker():
    """V4.6 FIX-2: Seed RNG per worker with high-entropy unique seed."""
    seed = int.from_bytes(os.urandom(8), 'big') ^ os.getpid() ^ int(time.time_ns())
    random.seed(seed)

# ═══════════════════════════════════════════════════════════════════
#  ARMOR BREAK & SUBLIMATION TRIGGERS
# ═══════════════════════════════════════════════════════════════════

def handle_armor_interaction(dmg, sram, target, bypasses_armor):
    """
    Apply damage vs armor. Returns (actual_hp_dmg, armor_broken, armor_absorbed).
    Attaque Perfide bypasses armor entirely.
    """
    armor = target.get("armor", 0)

    if bypasses_armor or armor <= 0:
        return dmg, False, 0

    if dmg >= armor:
        actual_dmg = dmg - armor
        target["armor"] = 0
        return actual_dmg, True, armor
    else:
        target["armor"] -= dmg
        return 0, False, dmg

def trigger_sublimations_on_armor_break(sram, target, full_break):
    """Trigger Rupture PA, Rupture Violente, Temerite on armor break."""
    triggers = []

    # Rupture PA
    if sram["rupture_pa_used"] < RUPTURE_PA_ACTIVATIONS:
        sram["ap"] += RUPTURE_PA_GAIN
        sram["rupture_pa_used"] += 1
        triggers.append(f"Rupture PA: +{RUPTURE_PA_GAIN}AP (#{sram['rupture_pa_used']}/{RUPTURE_PA_ACTIVATIONS})")

    # Rupture Violente
    if sram["rupture_violente_used"] < RUPTURE_VIOLENTE_ACTIVATIONS:
        rv_dmg = int(LVL * RUPTURE_VIOLENTE_DMG_PCT * (1 - target["res"]))
        target["hp"] -= rv_dmg
        sram["rupture_violente_used"] += 1
        triggers.append(f"Rupture Violente: {rv_dmg} dmg (#{sram['rupture_violente_used']}/{RUPTURE_VIOLENTE_ACTIVATIONS})")
        sram["turn_dmg_bonus"] += rv_dmg

    # Temerite: only on FULL armor break
    # V4.6 FIX-1: temerite_bonus is now on sram["combat_temerite"], persists across turns
    if full_break and sram["combat_temerite"] < TEMERITE_CAP:
        sram["combat_temerite"] = min(TEMERITE_CAP, sram["combat_temerite"] + TEMERITE_PER_BREAK)
        triggers.append(f"Temerite: +{TEMERITE_PER_BREAK*100:.0f}% dmg (total: {sram['combat_temerite']*100:.0f}%)")

    return triggers

# ═══════════════════════════════════════════════════════════════════
#  DAMAGE CALCULATION
# ═══════════════════════════════════════════════════════════════════

def calc_dmg(spell_key, sram, target, passives, pf_consumed_this_turn):
    sp = SPELLS[spell_key]
    if sp["base_dmg"] == 0:
        return 0, False, "no-dmg"

    elem = sp["element"]
    mastery = MAST.get(elem, 0)

    has_lq = "localisation_quantique" in passives
    effective_melee = MAST_MELEE + (MAST_REAR if has_lq else 0)

    is_melee = sp.get("melee", False) or manhattan(sram["pos"], target["pos"]) <= 1
    if is_melee:
        mastery += effective_melee
        if "inspiration" in passives:
            mastery = int(mastery * 0.60)

    dmg_mult = 1.0 + DMG_BONUS

    if "carnage" in passives:
        dmg_mult += 0.30
    if "motivation" in passives:
        dmg_mult -= 0.20

    # Isolated bonus
    alive_enemies = [e for e in sram["enemies"] if e["hp"] > 0]
    is_isolated = all(
        other is target or manhattan(other["pos"], target["pos"]) > 2
        for other in alive_enemies
    )
    if is_isolated:
        dmg_mult += INNATE_ISO_BONUS

    # Assaut Brutal
    if "assaut_brutal" in passives and sp["ap"] >= 4:
        dmg_mult += 0.05 * sp["ap"]

    # Hemorrhage
    hemo = target.get("hemo", 0)
    if hemo > 0:
        dmg_mult += hemo * 0.01

    # V4.6 FIX-1: use combat-level temerite (persists across turns)
    dmg_mult += sram.get("combat_temerite", 0)

    # PF consumer bonus
    pf_bonus = 0
    if sp["pf_consume"]:
        pf_bonus = sram["pf"] * 0.01

    # Chatiment/Effroi
    chatiment_bonus = 0
    if sp.get("special") in ("chatiment", "effroi") and pf_consumed_this_turn:
        chatiment_bonus = 0.30

    # Attaque Mortelle: extra if <50% HP
    low_hp_bonus = 0
    if sp.get("special") == "attaque_mortelle" and target["hp"] < target["max_hp"] * 0.5:
        low_hp_bonus = 0.40

    # Crit
    crit_chance = BASE_CRIT + sram.get("influence_lente_bonus", 0)
    crit = random.random() < min(1.0, crit_chance)
    crit_mult = 1.0
    if crit:
        crit_mult = 1.25
        mastery += MAST_CRIT
        if sp["ap"] >= 4 or sp.get("wp", 0) >= 1:
            crit_mult += IVORY_CRIT_DMG_BONUS

    # Surineur buff
    if sram.get("surineur_buff", False):
        if crit:
            crit_mult += 0.20
        dmg_mult += 0.20

    # Resistance
    res = target["res"]
    if target.get("assassinat_debuff", False):
        res = max(0, res - 0.15)
    effective_res = min(res, RES_CAP)

    base = sp["base_dmg"]
    # V4.6 FIX-2: apply damage noise HERE, per roll, not just in scoring
    noise = random.uniform(0.92, 1.08)
    dmg = base * (1 + mastery / 100) * dmg_mult * crit_mult * (1 + pf_bonus + chatiment_bonus + low_hp_bonus) * (1 - effective_res) * noise

    details = f"{elem.upper()} {'CRIT ' if crit else ''}mast:{mastery}"
    return max(0, int(dmg)), crit, details

# ═══════════════════════════════════════════════════════════════════
#  PF MANAGEMENT
# ═══════════════════════════════════════════════════════════════════

def apply_pf_generation(spell_key, sram, target, passives):
    sp = SPELLS[spell_key]
    if sp["pf_consume"] or sp["element"] == "neutral":
        return 0, "no PF gen"
    if "assaut_brutal" in passives and sp["ap"] >= 4:
        return 0, f"assaut_brutal blocks PF (+{sp['ap']*5}% dmg)"

    pf_gained = sp["ap"] * 5
    expl = f"+{pf_gained}({sp['ap']}APx5)"

    if spell_key == "kleptosram" and random.random() < 0.5:
        pf_gained += 5
        expl += "+5dos"

    if spell_key == "ouvrir_veines":
        h = target.get("hemo", 0)
        if h > 0:
            pf_gained += h
            expl += f"+{h}hemo"

    if spell_key == "coup_sournois":
        extras = sum(1 for e in sram["enemies"]
                     if e["hp"] > 0 and e is not target and manhattan(sram["pos"], e["pos"]) <= 1)
        if extras > 0:
            pf_gained += extras * 5
            expl += f"+{extras*5}aoe"

    old = sram["pf"]
    sram["pf"] = min(PF_CAP, sram["pf"] + pf_gained)
    return sram["pf"] - old, expl

def apply_pf_consumption(spell_key, sram, target):
    sp = SPELLS[spell_key]
    if not sp["pf_consume"] or sram["pf"] == 0:
        return 0, 0, 0, 0, 0, ""

    pf = sram["pf"]
    sram["pf"] = 0
    tiers = pf // 25
    ap_refund = tiers
    mp_refund = tiers
    wp_refund = tiers
    sram["ap"] += ap_refund
    sram["mp"] += mp_refund
    sram["wp"] += wp_refund
    cap_wp(sram)
    cap_mp(sram)

    hemo_add = tiers * 10
    old_h = target.get("hemo", 0)
    target["hemo"] = min(HEMO_CAP, old_h + hemo_add)

    expl = f"consumed {pf}PF ({tiers}x25): +{ap_refund}AP +{mp_refund}PM +{wp_refund}WP +{target['hemo']-old_h}hemo"
    return pf, ap_refund, mp_refund, wp_refund, target["hemo"] - old_h, expl

# ═══════════════════════════════════════════════════════════════════
#  KILL REWARDS
# ═══════════════════════════════════════════════════════════════════

def apply_kill_rewards(sram, target, passives):
    parts = []
    if "assassin" in passives:
        sram["ap"] += 1
        sram["mp"] += 1
        sram["wp"] += 1
        cap_wp(sram)
        cap_mp(sram)
        heal = int(BASE_HP * 0.20)
        sram["hp"] = min(sram["max_hp"], sram["hp"] + heal)
        parts.append(f"Assassin: +1AP +1PM +1WP heal+{heal}")
    else:
        old = sram["pf"]
        sram["pf"] = min(PF_CAP, sram["pf"] + 25)
        parts.append(f"+{sram['pf']-old}PF(kill)")

    sram["kills"] += 1
    sram["assassin_state"] = True
    return " | ".join(parts)

# ═══════════════════════════════════════════════════════════════════
#  SPELL CAST — V4.6 FIX-4: decomposed logging
# ═══════════════════════════════════════════════════════════════════

def can_cast(spell_key, sram, target, turn_uses, target_uses):
    sp = SPELLS[spell_key]
    if sram["ap"] < sp["ap"]:
        return False
    if sram["wp"] < sp.get("wp", 0):
        return False
    if target["hp"] <= 0:
        return False

    dist = manhattan(sram["pos"], target["pos"])
    if dist < sp["range_min"] or dist > sp["range_max"]:
        return False

    if turn_uses.get(spell_key, 0) >= sp["uses_per_turn"]:
        return False
    kt = f"{spell_key}_{id(target)}"
    if target_uses.get(kt, 0) >= sp["uses_per_target"]:
        return False

    cd = sp.get("cooldown", 0)
    if cd > 0 and sram.get("cooldowns", {}).get(spell_key, 0) > 0:
        return False

    if sp.get("line", False) and dist > 1:
        if sram["pos"][0] != target["pos"][0] and sram["pos"][1] != target["pos"][1]:
            return False

    return True

def apply_spell(spell_key, sram, target, passives, turn_uses, target_uses, pf_consumed_this_turn):
    sp = SPELLS[spell_key]

    # V4.6 FIX-4: capture state BEFORE paying cost
    snap_before = {
        "ap": sram["ap"], "mp": sram["mp"], "wp": sram["wp"], "pf": sram["pf"],
        "sram_hp": sram["hp"], "sram_pos": sram["pos"],
        "target_hp": target["hp"], "target_hemo": target.get("hemo", 0),
        "target_armor": target.get("armor", 0), "target_pos": target["pos"],
    }

    # ── Pay costs ──
    sram["ap"] -= sp["ap"]
    sram["wp"] -= sp.get("wp", 0)

    # V4.6 FIX-4: capture state AFTER paying cost (before any refunds)
    snap_after_cost = {"ap": sram["ap"], "mp": sram["mp"], "wp": sram["wp"], "pf": sram["pf"]}

    turn_uses[spell_key] = turn_uses.get(spell_key, 0) + 1
    target_uses[f"{spell_key}_{id(target)}"] = target_uses.get(f"{spell_key}_{id(target)}", 0) + 1

    if sp.get("cooldown", 0) > 0:
        sram.setdefault("cooldowns", {})[spell_key] = sp["cooldown"] + 1

    # ── PF generation ──
    pf_gained, pf_expl = apply_pf_generation(spell_key, sram, target, passives)

    # ── Damage ──
    dmg, crit, dmg_details = calc_dmg(spell_key, sram, target, passives, pf_consumed_this_turn[0])

    # ── PF consumption ──
    pf_consumed, ref_ap, ref_mp, ref_wp, ref_hemo, pf_expl = apply_pf_consumption(spell_key, sram, target)
    if pf_consumed > 0:
        pf_consumed_this_turn[0] = True

    # V4.6 FIX-4: capture state AFTER PF refund (before armor/kill)
    snap_after_pf = {"ap": sram["ap"], "mp": sram["mp"], "wp": sram["wp"], "pf": sram["pf"]}

    # ── Armor interaction ──
    bypasses_armor = (spell_key == "attaque_perfide")
    actual_dmg, armor_broken, armor_absorbed = handle_armor_interaction(dmg, sram, target, bypasses_armor)
    target["hp"] -= actual_dmg

    armor_given = 0
    if spell_key == "attaque_perfide":
        armor_given = int(dmg * 0.40)
        target["armor"] = target.get("armor", 0) + armor_given

    # Sublimation triggers
    sub_triggers = []
    if armor_absorbed > 0 or armor_broken:
        sub_triggers = trigger_sublimations_on_armor_break(sram, target, armor_broken)

    # V4.6 FIX-4: capture state AFTER armor/sublimation (before hemo/kill)
    snap_after_sub = {"ap": sram["ap"], "mp": sram["mp"], "wp": sram["wp"]}

    # ── Hemo application ──
    hemo_applied = 0
    if sp.get("hemo_apply", 0) > 0:
        to_add = sp["hemo_apply"]
        if spell_key == "premier_sang" and target.get("hemo", 0) > 0:
            to_add = sp.get("hemo_apply_if_already", to_add)
        old_h = target.get("hemo", 0)
        target["hemo"] = min(HEMO_CAP, old_h + to_add)
        hemo_applied = target["hemo"] - old_h

    if spell_key == "saignee_mortelle":
        old_h = target.get("hemo", 0)
        target["hemo"] = min(HEMO_CAP, old_h + 6)
        hemo_applied += target["hemo"] - old_h

    # Ouvrir les Veines: consume hemo, heal
    heal = 0
    if spell_key == "ouvrir_veines":
        h = target.get("hemo", 0)
        if h > 0:
            heal = int(sram["max_hp"] * h * 0.01)
            sram["hp"] = min(sram["max_hp"], sram["hp"] + heal)
            target["hemo"] = 0

    # Arnaque: heal
    if spell_key == "arnaque" and pf_consumed > 0:
        heal = int(sram["max_hp"] * pf_consumed * 0.005)
        sram["hp"] = min(sram["max_hp"], sram["hp"] + heal)

    # ── Kill check ──
    killed = target["hp"] <= 0
    kill_rewards_str = ""
    letale_refund = ""
    if killed:
        target["hp"] = 0
        if spell_key == "attaque_letale":
            sram["ap"] += 2
            sram["mp"] += 2
            cap_mp(sram)
            letale_refund = "+2AP +2PM (Letale kill)"
        kill_rewards_str = apply_kill_rewards(sram, target, passives)

    # V4.6 FIX-4: capture FINAL state
    snap_final = {
        "ap": sram["ap"], "mp": sram["mp"], "wp": sram["wp"], "pf": sram["pf"],
        "sram_hp": sram["hp"], "sram_pos": sram["pos"],
        "target_hp": target["hp"], "target_hemo": target.get("hemo", 0),
        "target_armor": target.get("armor", 0),
    }

    if spell_key == "assassinat":
        target["assassinat_debuff"] = True

    if spell_key == "fourberie" and target["hp"] > 0:
        tx, ty = target["pos"]
        sram["pos"] = (tx + 1, ty)

    if spell_key == "saignee_mortelle" and target["hp"] > 0:
        target["saignee_replica"] = True

    # V4.6 FIX-4: build decomposed log
    log = {
        "spell": sp["name"], "spell_key": spell_key, "target": target["name"],
        "element": sp["element"],
        "cost_ap": sp["ap"], "cost_wp": sp.get("wp", 0),
        "cost": f"-{sp['ap']}AP" + (f"-{sp['wp']}WP" if sp.get('wp',0)>0 else ""),
        "dmg": dmg, "actual_dmg": actual_dmg, "crit": crit,
        "snap_before": snap_before,
        "snap_after_cost": snap_after_cost,       # V4.6: after paying AP/WP
        "snap_after_pf": snap_after_pf,           # V4.6: after PF refund
        "snap_after_sub": snap_after_sub,          # V4.6: after sublimation triggers
        "snap_final": snap_final,                  # V4.6: after kill rewards
        "pf_gen": pf_expl,
        "pf_consume": pf_expl if pf_consumed > 0 else "",
        "pf_consumed_amount": pf_consumed,
        "pf_refund_ap": ref_ap, "pf_refund_mp": ref_mp, "pf_refund_wp": ref_wp,
        "sub_triggers": sub_triggers,
        "armor_given": armor_given,
        "armor_absorbed": armor_absorbed,
        "armor_broken": armor_broken,
        "hemo_applied": hemo_applied,
        "heal": heal,
        "kill": killed,
        "kill_rewards": kill_rewards_str,
        "letale_refund": letale_refund,
        "alive": sum(1 for e in sram["enemies"] if e["hp"] > 0),
        "total_kills": sram["kills"],
    }

    return log, pf_consumed_this_turn

# ═══════════════════════════════════════════════════════════════════
#  MOVEMENT
# ═══════════════════════════════════════════════════════════════════

def move_toward(sram, target_pos, max_steps=99):
    moved = 0
    while sram["mp"] > 0 and moved < max_steps:
        sx, sy = sram["pos"]
        tx, ty = target_pos
        if manhattan(sram["pos"], target_pos) <= 1:
            break
        dx = (1 if tx > sx else -1) if tx != sx else 0
        dy = (1 if ty > sy else -1) if ty != sy else 0
        if abs(tx - sx) >= abs(ty - sy) and dx != 0:
            sram["pos"] = (sx + dx, sy)
        elif dy != 0:
            sram["pos"] = (sx, sy + dy)
        else:
            break
        sram["mp"] -= 1
        moved += 1
    return moved

# ═══════════════════════════════════════════════════════════════════
#  GREEDY ACTION SELECTION — V4.6 FIX-5: Perfide end-of-turn penalty
# ═══════════════════════════════════════════════════════════════════

def find_best_action(sram, deck, passives, turn_uses, target_uses, pf_consumed_this_turn):
    alive = [e for e in sram["enemies"] if e["hp"] > 0]
    if not alive:
        return None, None

    best_spell = None
    best_target = None
    best_score = -1

    current_ap = sram["ap"]

    for spell_key in deck:
        sp = SPELLS[spell_key]
        for target in alive:
            if not can_cast(spell_key, sram, target, turn_uses, target_uses):
                continue

            dmg, _, _ = calc_dmg(spell_key, sram, target, passives, pf_consumed_this_turn[0])
            score = float(dmg)

            # Kill bonus
            if target["hp"] <= dmg * 1.1:
                score *= 1.5

            # PF consumer: prefer when PF high
            if sp["pf_consume"] and sram["pf"] >= 50:
                score *= (1 + sram["pf"] * 0.01)
            if sp["pf_consume"] and sram["pf"] < 25:
                score *= 0.3

            # V4.6 FIX-5: Attaque Perfide scoring with end-of-turn awareness
            if spell_key == "attaque_perfide":
                remaining_ruptures = RUPTURE_PA_ACTIVATIONS - sram["rupture_pa_used"]
                ap_after_perfide = current_ap - sp["ap"]  # AP left after casting Perfide
                if remaining_ruptures > 0 and ap_after_perfide >= 2:
                    # We have AP left to break the armor this turn → good
                    score *= 2.0
                elif remaining_ruptures > 0 and ap_after_perfide < 2:
                    # V4.6 FIX-5: Not enough AP to break armor → wasted Perfide
                    score *= 0.3
                else:
                    # No ruptures left, Perfide is just a damage spell
                    score *= 0.8

            # If target HAS armor and we're NOT perfide, big bonus for breaking it
            if target.get("armor", 0) > 0 and spell_key != "attaque_perfide":
                remaining_ruptures = RUPTURE_PA_ACTIVATIONS - sram["rupture_pa_used"]
                if remaining_ruptures > 0:
                    score += 8000 * remaining_ruptures  # Very high priority

            # Assassinat
            if spell_key == "assassinat" and sram["ap"] >= 7:
                score = max(score, 5000)

            # V4.6 FIX-2: stronger noise to differentiate runs
            score *= random.uniform(0.85, 1.15)

            if score > best_score:
                best_score = score
                best_spell = spell_key
                best_target = target

    return best_spell, best_target

# ═══════════════════════════════════════════════════════════════════
#  TURN SIMULATION — V4.6 FIX-1: Temerite persists
# ═══════════════════════════════════════════════════════════════════

def run_turn(sram, deck, passives, turn_num):
    turn_uses = {}
    target_uses = {}
    pf_consumed_this_turn = [False]
    turn_dmg = 0
    actions = []

    # Reset per-turn sublimation counters (activations reset each turn)
    sram["rupture_pa_used"] = 0
    sram["rupture_violente_used"] = 0
    sram["turn_dmg_bonus"] = 0
    # V4.6 FIX-1: temerite_bonus is NOT reset here — it's combat_temerite on the sram dict
    # (was: sram["temerite_bonus"] = 0.0 — REMOVED)

    # Cooldowns
    for k in list(sram.get("cooldowns", {}).keys()):
        sram["cooldowns"][k] -= 1
        if sram["cooldowns"][k] <= 0:
            del sram["cooldowns"][k]

    # Influence Lente: +2% crit per turn
    old_il = sram.get("influence_lente_bonus", 0)
    sram["influence_lente_bonus"] = min(INFLUENCE_LENTE_CAP, old_il + INFLUENCE_LENTE_PER_TURN)
    if sram["influence_lente_bonus"] > old_il:
        actions.append({"spell": f"[Influence Lente +{INFLUENCE_LENTE_PER_TURN*100:.0f}% CC -> {sram['influence_lente_bonus']*100:.0f}%]",
                       "dmg": 0})

    # End-of-prev-turn PF (isolated)
    if turn_num > 1 and not sram.get("assassin_state", False):
        alive = [e for e in sram["enemies"] if e["hp"] > 0]
        if all(manhattan(sram["pos"], e["pos"]) > 2 for e in alive):
            old_pf = sram["pf"]
            sram["pf"] = min(PF_CAP, sram["pf"] + 25)
            if sram["pf"] > old_pf:
                actions.append({"spell": f"[+25PF isolated]", "dmg": 0})

    sram["assassin_state"] = False

    # Assassinat debuff resolution
    for e in sram["enemies"]:
        if e.get("assassinat_end_of_turn_buff", False):
            e["assassinat_debuff"] = False
            e["assassinat_end_of_turn_buff"] = False
        if e.get("assassinat_debuff", False):
            e["assassinat_end_of_turn_buff"] = True

    # Saignee replica
    for e in sram["enemies"]:
        if e.get("saignee_replica", False) and e["hp"] > 0:
            replica_base = int(SPELLS["saignee_mortelle"]["base_dmg"] * 0.7 *
                              (1 + MAST["fire"] / 100) * (1 - e["res"]))
            old_h = e.get("hemo", 0)
            e["hemo"] = min(HEMO_CAP, old_h + 6)
            hemo_dmg_portion = int(replica_base * old_h * 0.01)
            sram["hp"] = min(sram["max_hp"], sram["hp"] + hemo_dmg_portion)

            e["hp"] -= replica_base
            turn_dmg += replica_base
            actions.append({"spell": "[Saignee Replica]", "target": e["name"],
                           "dmg": replica_base, "element": "fire",
                           "hemo_applied": e["hemo"] - old_h,
                           "heal": hemo_dmg_portion})
            if e["hp"] <= 0:
                e["hp"] = 0
                apply_kill_rewards(sram, e, passives)
            e["saignee_replica"] = False

    # Initial movement
    alive = [e for e in sram["enemies"] if e["hp"] > 0]
    if alive:
        nearest = min(alive, key=lambda e: manhattan(sram["pos"], e["pos"]))
        mp_before = sram["mp"]
        pos_before = sram["pos"]
        moved = move_toward(sram, nearest["pos"])
        if moved > 0:
            actions.append({"spell": f"[Move {moved}PM]", "dmg": 0,
                           "before": {"mp": mp_before, "pos": pos_before},
                           "after": {"mp": sram["mp"], "pos": sram["pos"]}})

    # Main loop
    for _ in range(25):
        alive = [e for e in sram["enemies"] if e["hp"] > 0]
        if not alive:
            break

        spell_key, target = find_best_action(sram, deck, passives, turn_uses, target_uses, pf_consumed_this_turn)

        if spell_key is None:
            nearest = min(alive, key=lambda e: manhattan(sram["pos"], e["pos"]))
            if sram["mp"] > 0 and manhattan(sram["pos"], nearest["pos"]) > 1:
                mp_before = sram["mp"]
                moved = move_toward(sram, nearest["pos"], max_steps=3)
                if moved > 0:
                    actions.append({"spell": f"[Move {moved}PM mid]", "dmg": 0,
                                   "before": {"mp": mp_before},
                                   "after": {"mp": sram["mp"], "pos": sram["pos"]}})
                    continue
            break

        alog, pf_consumed_this_turn = apply_spell(
            spell_key, sram, target, passives, turn_uses, target_uses, pf_consumed_this_turn
        )
        turn_dmg += alog["dmg"]
        actions.append(alog)

    # Enemy turn
    alive_enemies = [e for e in sram["enemies"] if e["hp"] > 0]
    enemy_dmg = sum(e["dmg"] for e in alive_enemies if manhattan(sram["pos"], e["pos"]) <= e["mp"] + 1)
    sram["hp"] -= enemy_dmg
    if sram["hp"] <= 0:
        sram["hp"] = 0
        sram["dead"] = True

    turn_dmg += sram["turn_dmg_bonus"]

    return turn_dmg, {
        "turn": turn_num, "actions": actions, "turn_dmg": turn_dmg,
        "enemy_dmg": enemy_dmg, "sram_hp": sram["hp"], "pf": sram["pf"],
        "ap_remaining": sram["ap"], "mp_remaining": sram["mp"],
        "wp_remaining": sram["wp"],
        "alive": len(alive_enemies),
        "temerite": sram.get("combat_temerite", 0),  # V4.6: combat-level
        "rupture_pa": sram["rupture_pa_used"],
        "influence_lente": sram.get("influence_lente_bonus", 0),
    }

# ═══════════════════════════════════════════════════════════════════
#  SIMULATION — V4.6 FIX-1: combat_temerite initialized here
# ═══════════════════════════════════════════════════════════════════

def simulate_one(args):
    deck, passive_list, combat_name = args
    passives = set(passive_list)

    hp = BASE_HP
    if "carnage" in passives:
        hp = int(BASE_HP * 0.80)

    ap = BASE_AP
    if "motivation" in passives:
        ap += 1

    sram = {
        "hp": hp, "max_hp": hp, "ap": ap, "base_ap": ap,
        "mp": BASE_MP, "base_mp": BASE_MP,
        "wp": BASE_WP, "base_wp": BASE_WP,
        "pf": START_PF, "pos": SRAM_START_POS,
        "kills": 0, "dead": False, "assassin_state": False,
        "cooldowns": {}, "surineur_buff": False,
        "influence_lente_bonus": 0.0,
        "rupture_pa_used": 0, "rupture_violente_used": 0,
        "combat_temerite": 0.0,      # V4.6 FIX-1: persists across turns
        "turn_dmg_bonus": 0,
        "enemies": [],
    }

    enemies = []
    for et in COMBATS[combat_name]:
        enemies.append({
            "name": et["name"], "hp": et["hp"], "max_hp": et["hp"],
            "res": et["res"], "mp": et["mp"], "pos": et["pos"], "dmg": et["dmg"],
            "hemo": 0, "armor": 0,
            "assassinat_debuff": False, "assassinat_end_of_turn_buff": False,
            "saignee_replica": False,
        })
    sram["enemies"] = enemies

    available = [s for s in deck if s in SPELLS]
    total_dmg = 0
    turn_logs = []

    for t in range(1, MAX_TURNS + 1):
        if not any(e["hp"] > 0 for e in sram["enemies"]) or sram["dead"]:
            break
        sram["ap"] = sram["base_ap"]
        sram["mp"] = sram["base_mp"]
        # WP does NOT reset — correct

        td, tl = run_turn(sram, available, passives, t)
        total_dmg += td
        turn_logs.append(tl)

    return {
        "total_dmg": total_dmg, "kills": sram["kills"],
        "survived": not sram["dead"], "turns": len(turn_logs),
        "turn_logs": turn_logs, "deck": deck,
        "passives": passive_list, "combat": combat_name,
    }

# ═══════════════════════════════════════════════════════════════════
#  LOADOUT GENERATION
# ═══════════════════════════════════════════════════════════════════

def gen_all_loadouts():
    fire = ["premier_sang", "ouvrir_veines", "saignee_mortelle", "chatiment", "mise_a_mort"]
    water = ["kleptosram", "arnaque", "attaque_letale", "attaque_perfide", "attaque_mortelle"]
    air = ["coup_penetrant", "fourberie", "coup_sournois", "effroi", "traumatisme"]
    neutral = ["assassinat", "peur", "surineur", "galopade"]

    deck_templates = [
        fire + water + ["assassinat", "peur"],
        fire + water + ["fourberie", "assassinat"],
        fire + water + ["fourberie", "coup_penetrant"],
        fire + water[:4] + ["fourberie", "coup_penetrant", "traumatisme"],
        fire + water[:4] + ["fourberie", "traumatisme", "assassinat"],
        fire + water[:3] + air[:3] + ["assassinat"],
        fire + water[:3] + ["fourberie", "coup_sournois", "assassinat", "peur"],
        fire + water + ["effroi", "traumatisme"],
        fire + water[:4] + ["coup_sournois", "effroi", "assassinat"],
        fire + air[:3] + water[:3] + ["assassinat"],
        fire + water + ["surineur", "assassinat"],
        fire + air[:4] + water[:2] + ["assassinat"],
        fire + water + ["fourberie", "effroi"],
        fire + water[:3] + air[:3] + ["peur"],
    ]

    passive_sets = [
        ["localisation_quantique", "assassin", "carnage", "evasion", "assaut_brutal"],
        ["localisation_quantique", "assassin", "carnage", "evasion", "inspiration"],
        ["localisation_quantique", "assassin", "carnage", "evasion", "interception"],
        ["localisation_quantique", "assassin", "carnage", "assaut_brutal", "interception"],
        ["localisation_quantique", "assassin", "carnage", "retenue", "evasion"],
        ["localisation_quantique", "assassin", "carnage", "embuscade", "evasion"],
        ["localisation_quantique", "assassin", "carnage", "leurre", "evasion"],
        ["localisation_quantique", "assassin", "carnage", "motivation", "evasion"],
        ["localisation_quantique", "assassin", "carnage", "hemophilie", "evasion"],
    ]

    loadouts = []
    for deck in deck_templates:
        for pset in passive_sets:
            loadouts.append((deck[:DECK_SLOTS], tuple(pset)))
    return loadouts

# ═══════════════════════════════════════════════════════════════════
#  DISPLAY — V4.6 FIX-4: decomposed action format
# ═══════════════════════════════════════════════════════════════════

def format_action(action, idx):
    lines = []
    sp_name = action.get("spell", "?")
    target = action.get("target", "-")
    dmg = action.get("dmg", 0)
    elem = action.get("element", "")
    cost = action.get("cost", "")

    if sp_name.startswith("["):
        lines.append(f"  |  {idx}. {sp_name}")
        if "before" in action and "after" in action:
            b, a = action["before"], action["after"]
            parts = []
            for k in ["mp", "pf"]:
                if k in b and k in a:
                    parts.append(f"{k.upper()}:{b[k]}->{a[k]}")
            if "pos" in a:
                parts.append(f"Pos:{a['pos']}")
            if parts:
                lines.append(f"  |     {' | '.join(parts)}")
        return "\n".join(lines)

    crit_str = " CRIT" if action.get("crit") else ""
    lines.append(f"  |  {idx}. {sp_name:25s} > {target:15s}  DMG:{dmg:>6,}{crit_str}  ({cost}) [{elem.upper()}]")

    # V4.6 FIX-4: decomposed resource lines
    sb = action.get("snap_before", {})
    sc = action.get("snap_after_cost", {})

    # Line 1: Cost
    lines.append(f"  |     Cout:  AP:{sb.get('ap','?')}->{sc.get('ap','?')}  "
                 f"WP:{sb.get('wp','?')}->{sc.get('wp','?')}")

    # Line 2: PF refund (if any)
    pf_consumed = action.get("pf_consumed_amount", 0)
    if pf_consumed > 0:
        sp_pf = action.get("snap_after_pf", {})
        ref_ap = action.get("pf_refund_ap", 0)
        ref_mp = action.get("pf_refund_mp", 0)
        ref_wp = action.get("pf_refund_wp", 0)
        lines.append(f"  |     PF Refund: {pf_consumed}PF consumed -> +{ref_ap}AP +{ref_mp}PM +{ref_wp}WP  "
                     f"AP:{sc.get('ap','?')}->{sp_pf.get('ap','?')}  "
                     f"MP:{sc.get('mp','?')}->{sp_pf.get('mp','?')}  "
                     f"PF:{sb.get('pf','?')}->0")

    # Line 3: Sublimation triggers (if any)
    for st in action.get("sub_triggers", []):
        ss = action.get("snap_after_sub", {})
        lines.append(f"  |     >> {st}  AP->{ss.get('ap','?')}")

    # Line 4: Kill rewards (if any)
    if action.get("kill"):
        sf = action.get("snap_final", {})
        sp_sub = action.get("snap_after_sub", action.get("snap_after_pf", sc))
        lines.append(f"  |     >>> KILL! {action.get('kill_rewards', '')}")
        lines.append(f"  |         AP:{sp_sub.get('ap','?')}->{sf.get('ap','?')}  "
                     f"MP:{sp_sub.get('mp','?')}->{sf.get('mp','?')}  "
                     f"WP:{sp_sub.get('wp','?')}->{sf.get('wp','?')}")

    if action.get("letale_refund"):
        lines.append(f"  |     {action['letale_refund']}")

    # Line 5: PF generation (if not consumed)
    pf_gen = action.get("pf_gen", "")
    if pf_gen and "no" not in pf_gen and pf_consumed == 0:
        lines.append(f"  |     PF Gen: {pf_gen}")

    # Line 6: Armor given
    if action.get("armor_given"):
        lines.append(f"  |     Armor given: {action['armor_given']}")

    # Line 7: Armor broken
    if action.get("armor_broken"):
        lines.append(f"  |     Armor BROKEN (absorbed: {action.get('armor_absorbed', 0)})")

    # Line 8: Hemo
    if action.get("hemo_applied"):
        lines.append(f"  |     Hemo: +{action['hemo_applied']}")

    # Line 9: Heal
    if action.get("heal"):
        lines.append(f"  |     Heal: +{action['heal']}")

    # Line 10: Target status
    sf = action.get("snap_final", action.get("snap_after_pf", {}))
    lines.append(f"  |     Cible: HP:{sb.get('target_hp','?'):>5}->{sf.get('target_hp','?'):>5}  "
                 f"Hemo:{sb.get('target_hemo','?')}->{sf.get('target_hemo','?')}  "
                 f"Arm:{sb.get('target_armor',0):>4}->{sf.get('target_armor',0):>4}")

    return "\n".join(lines)

def print_detailed_run(result):
    print(f"\n  Deck: {', '.join(result['deck'])}")
    print(f"  Passifs: {', '.join(result['passives'])}")
    print(f"  DPT Total: {result['total_dmg']:,}  Kills: {result['kills']}  "
          f"{'SURVECU' if result['survived'] else 'MORT'}")

    for tl in result["turn_logs"]:
        t = tl["turn"]
        print(f"\n  +== TOUR {t} {'='*60}")
        print(f"  |  Degats: {tl['turn_dmg']:>6,}  |  HP:{tl['sram_hp']:>5}  "
              f"|  Mobs:{tl['alive']}  |  Dmg recu:{tl['enemy_dmg']}")
        tem_val = tl.get('temerite', 0)
        print(f"  |  Temerite: +{tem_val*100:.0f}% (cumul)  "
              f"Rupture PA: {tl.get('rupture_pa',0)}/{RUPTURE_PA_ACTIVATIONS}  "
              f"Influence Lente: +{tl.get('influence_lente',0)*100:.0f}% CC")
        print(f"  +{'─'*72}")

        for i, action in enumerate(tl["actions"], 1):
            print(format_action(action, i))

        ap_left = tl["ap_remaining"]
        alive = tl["alive"]
        if ap_left > 1 and alive > 0:
            print(f"  |  >>> PA RESTANT: {ap_left}")
        print(f"  |  Fin: AP={ap_left} MP={tl['mp_remaining']} WP={tl.get('wp_remaining','?')} PF={tl['pf']}")
        print(f"  +{'='*72}")

# ═══════════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════════

def main():
    sep = "=" * 90
    print(f"\n{sep}")
    print(f"  WAKFU SRAM OPTIMIZER V{VERSION} -- Sublimation & Armor Engine")
    print(f"  Sram \"L'Immortel\" -- Niveau {LVL} -- Patch 1.91")
    print(f"  Sublimations: Rupture PA (Niv.4, +2PA, 2 act/tour), Rupture Violente (Niv.4, 40%, 2 act/tour), Temerite (+12%/break, cap 30%), Influence Lente (+2%CC/tour)")
    print(f"  Relique: Ivory Dofus (+15% crit dmg on >=4AP/>=1WP)")
    print(f"  V4.6 FIXES: Temerite persiste, RNG diversifie, MP cap={MP_CAP_MAX}, log decompose, Perfide fin-de-tour penalise")
    print(f"{sep}\n")

    loadouts = gen_all_loadouts()
    combats = list(COMBATS.keys())
    n_cores = max(1, cpu_count() - 1)

    tasks = []
    for deck, passives in loadouts:
        for combat in combats:
            for _ in range(SIMS_PER_LOADOUT):
                tasks.append((deck, passives, combat))

    total = len(tasks)
    print(f"  {len(loadouts)} loadouts x {len(combats)} combats x {SIMS_PER_LOADOUT} simus")
    print(f"  = {total:,} simulations totales")
    print(f"  {n_cores} processus paralleles\n")

    t0 = time.time()
    results = []

    with Pool(n_cores, initializer=init_worker) as pool:
        for i, res in enumerate(pool.imap_unordered(simulate_one, tasks, chunksize=50), 1):
            results.append(res)
            if i % 5000 == 0 or i == total:
                elapsed = time.time() - t0
                rate = i / elapsed if elapsed > 0 else 0
                eta = (total - i) / rate if rate > 0 else 0
                print(f"  {i:>10,}/{total:,}  ({100*i/total:.1f}%)  "
                      f"{rate:.0f} sims/s  ETA {eta:.0f}s")

    elapsed = time.time() - t0
    print(f"\n  {total:,} simulations en {elapsed:.1f}s ({total/elapsed:.0f} sims/s)")

    # Aggregate
    loadout_stats = defaultdict(lambda: defaultdict(list))
    for r in results:
        key = (tuple(r["deck"]), tuple(r["passives"]))
        loadout_stats[r["combat"]][key].append(r)

    print(f"\n{sep}")
    print(f"  RESULTATS PAR COMBAT")
    print(f"{sep}")

    global_best = None
    global_best_avg = 0

    for combat in combats:
        print(f"\n{'─'*90}")
        print(f"  COMBAT: {combat}")
        print(f"{'─'*90}\n")

        rankings = []
        for key, runs in loadout_stats[combat].items():
            avg = sum(r["total_dmg"] for r in runs) / len(runs)
            mn = min(r["total_dmg"] for r in runs)
            mx = max(r["total_dmg"] for r in runs)
            surv = sum(1 for r in runs if r["survived"]) / len(runs)
            best_run = max(runs, key=lambda r: r["total_dmg"])
            rankings.append((avg, mn, mx, surv, key, best_run))
        rankings.sort(key=lambda x: -x[0])

        for i, (avg, mn, mx, surv, key, best_run) in enumerate(rankings[:5], 1):
            deck, passives = key
            n_elem = sum(1 for s in deck if SPELLS.get(s, {}).get("element", "neutral") != "neutral")
            print(f"  #{i}  DPT moy: {avg:>10,.0f}  (min:{mn:,} max:{mx:,})  Survie: {surv*100:.0f}%")
            print(f"      Passifs: {', '.join(passives)}")
            print(f"      Deck ({len(deck)}): {n_elem} elem + {len(deck)-n_elem} neutres")
            print(f"      Sorts: {', '.join(deck)}\n")

        best = rankings[0][5]
        print(f"  * Meilleur run: {best['total_dmg']:,} dmg ({best['kills']} kills)")
        for tl in best["turn_logs"]:
            spells = [a.get("spell", "?") for a in tl["actions"] if a.get("dmg", 0) > 0 or a.get("spell","").startswith("[")]
            tmrt = f" Tem:+{tl.get('temerite',0)*100:.0f}%" if tl.get('temerite',0) > 0 else ""
            rpa = f" RupPA:{tl.get('rupture_pa',0)}" if tl.get('rupture_pa',0) > 0 else ""
            print(f"    T{tl['turn']}: {tl['turn_dmg']:>6,} dmg  HP:{tl['sram_hp']}  PF:{tl['pf']:>3}  "
                  f"WP:{tl.get('wp_remaining','?')}{tmrt}{rpa}  [{' > '.join(spells[:8])}]")

        if rankings[0][0] > global_best_avg:
            global_best_avg = rankings[0][0]
            global_best = rankings[0]

    # Global best
    print(f"\n{sep}")
    print(f"  MEILLEUR BUILD GLOBAL")
    print(f"{sep}")
    if global_best:
        avg, mn, mx, surv, key, best_run = global_best
        deck, passives = key
        print(f"  DPT moyen: {avg:,.0f}")
        print(f"  Passifs: {', '.join(passives)}")
        print(f"  Deck: {', '.join(deck)}")

    # Synergies
    print(f"\n{sep}")
    print(f"  SYNERGIES EMERGENTES (top 10%)")
    print(f"{sep}")

    top_pct = sorted(results, key=lambda r: -r["total_dmg"])[:len(results)//10]

    spell_freq = Counter()
    combo_freq = Counter()
    passive_freq = Counter()
    elem_dmg = defaultdict(float)
    perfide_rupture_count = 0
    wasted_perfide_count = 0  # V4.6: track wasted Perfide (armor not broken same turn)

    for r in top_pct:
        for p in r["passives"]:
            passive_freq[p] += 1
        for tl in r["turn_logs"]:
            if tl.get("rupture_pa", 0) > 0:
                perfide_rupture_count += tl["rupture_pa"]

            # V4.6: count wasted Perfides (armor given but not broken in same turn)
            perfide_cast_this_turn = False
            armor_broken_this_turn = False
            prev = None
            for a in tl["actions"]:
                sp = a.get("spell_key") or a.get("spell", "")
                dmg = a.get("dmg", 0)
                el = a.get("element", "")

                if sp == "attaque_perfide" and dmg > 0:
                    perfide_cast_this_turn = True
                if a.get("armor_broken", False):
                    armor_broken_this_turn = True

                if dmg > 0:
                    spell_freq[a.get("spell", sp)] += 1
                    if el:
                        elem_dmg[el] += dmg
                if prev and dmg > 0:
                    combo_freq[f"{prev} > {a.get('spell', sp)}"] += 1
                if dmg > 0 or sp.startswith("["):
                    prev = a.get("spell", sp)

            if perfide_cast_this_turn and not armor_broken_this_turn:
                wasted_perfide_count += 1

    total_top = len(top_pct)
    print(f"\n  Sorts les + frequents:")
    for name, count in spell_freq.most_common(15):
        print(f"    {name:30s} {count:>6}")

    print(f"\n  Enchainements les + frequents:")
    for combo, count in combo_freq.most_common(12):
        print(f"    {combo:50s} {count:>6}")

    print(f"\n  Passifs:")
    for name, count in passive_freq.most_common():
        print(f"    {name:30s} {count:>6} ({count*100//total_top}%)")

    total_elem = sum(elem_dmg.values()) or 1
    print(f"\n  Degats par element:")
    for el in ["fire", "water", "air"]:
        avg_d = elem_dmg.get(el, 0) / max(1, total_top)
        pct = elem_dmg.get(el, 0) / total_elem * 100
        print(f"    {el.upper():15s} {avg_d:>10,.0f} moy  ({pct:.1f}%)")

    print(f"\n  Rupture PA activations (top 10%): {perfide_rupture_count:,} total "
          f"({perfide_rupture_count/max(1,total_top):.1f} moy/combat)")
    print(f"  Perfide gaspillees (armure non cassee): {wasted_perfide_count:,} "
          f"({wasted_perfide_count/max(1,total_top):.1f} moy/combat)")

    # Detailed best run
    print(f"\n{sep}")
    print(f"  LOG DETAILLE -- MEILLEUR RUN")
    print(f"{sep}")
    best_overall = max(results, key=lambda r: r["total_dmg"])
    print_detailed_run(best_overall)

    # Top 5
    print(f"\n{sep}")
    print(f"  TOP 5 RUNS")
    print(f"{sep}")
    top5 = sorted(results, key=lambda r: -r["total_dmg"])[:5]
    for i, r in enumerate(top5, 1):
        print(f"\n  #{i}  DPT: {r['total_dmg']:>10,}  Kills:{r['kills']}  "
              f"{'OK' if r['survived'] else 'MORT'}")
        print(f"      Deck: {', '.join(r['deck'][:6])}...")
        print(f"      Passifs: {', '.join(r['passives'])}")
        for tl in r["turn_logs"]:
            spells = [a.get("spell", "?") for a in tl["actions"] if a.get("dmg", 0) > 0 or a.get("spell","").startswith("[")]
            print(f"      T{tl['turn']}: {tl['turn_dmg']:>6,}  AP:{tl['ap_remaining']} WP:{tl.get('wp_remaining','?')} PF:{tl['pf']}  "
                  f"Rup:{tl.get('rupture_pa',0)} Tem:{tl.get('temerite',0)*100:.0f}%  "
                  f"[{' > '.join(spells[:8])}]")

    print(f"\n{sep}")
    print(f"  Termine en {time.time()-t0:.1f}s")
    print(f"{sep}\n")

if __name__ == "__main__":
    main()
