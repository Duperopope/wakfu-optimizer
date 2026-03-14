#!/usr/bin/env python3
"""
WAKFU SRAM OPTIMIZER V4.7 — Full Mechanics Engine
Sram "L'Immortel" — Level 179 — Patch 1.91
================================================================
NEW in V4.7 (from V4.6):
  FIX-1   Real base damage values from official tables (interpolated at lvl 179)
  FIX-2   Carnage corrected: +15% dmg, +10% dmg vs armored targets, -30% heals (not +30%/-20%HP)
  FIX-3   Assaut Brutal: Mise a Mort & Traumatisme EXCLUDED from the passive
  FIX-4   Assassinat: -100 flat elemental resistance (not -15%), +100 if survives
  FIX-5   Galopade: 0 AP 1 WP, +3 PM max +80 dodge, usable on self (mobility tool)
  FIX-6   Double: modeled as 8 AP sub-turn with Contact Letal + Peur
  FIX-7   Hemophilie DISABLED (bugged in 1.91.2)
  FIX-8   Inspiration corrected: +10% dmg vs targets with higher initiative (not -40% melee)
  FIX-9   Ivory Dofus main effect: +358 mastery on first hit each turn
  FIX-10  Sacapatate 0% and 90% resistance combat scenarios added
  FIX-11  Perfide hard-blocked if AP after cast < 2
  FIX-12  Boss invulnerability phases, obstacles on grid
  FIX-13  Temerite persists across turns (kept from V4.6)
  FIX-14  Attaque Mortelle: enhanced damage table when target <50% HP
  FIX-15  Chatiment: enhanced damage when PF consumed this turn (separate values)
  FIX-16  Effroi: enhanced damage when PF consumed this turn
  FIX-17  Coup Penetrant: bonus damage on armor
  FIX-18  Fourberie: teleport behind target (repositioning)
  FIX-19  Coup Sournois: repeats on previous targets, pushback 2 cells
  FIX-20  Saignee Mortelle: lifesteal from hemorrhage damage
"""

import random, time, math, os, sys
from multiprocessing import Pool, cpu_count
from collections import defaultdict, Counter
from copy import deepcopy

# ═══════════════════════════════════════════════════════════════════
#  CONSTANTS
# ═══════════════════════════════════════════════════════════════════
VERSION = "4.7"
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
BASE_CRIT = 0.72  # 72% crit from gear + 20% innate at start = capped later
START_CRIT_BONUS = 0.20  # innate +20% crit at combat start (already in BASE_CRIT)
START_PF = 50
MP_CAP_MAX = BASE_MP + 5

MAST = {"fire": 808, "water": 808, "air": 425, "earth": 190}
MAST_CRIT = 456
MAST_REAR = 585
MAST_MELEE = 1030
MAST_DIST = 0
MAST_BERSERK = -90
MAST_HEAL = 0

# V4.7 FIX-2: Carnage is +15% dmg, +10% vs armored, -30% heals (NOT +30%/-20%HP)
CARNAGE_DMG_BONUS = 0.15
CARNAGE_ARMOR_DMG_BONUS = 0.10
CARNAGE_HEAL_PENALTY = -0.30

DMG_BONUS = 0.18
INNATE_ISO_BONUS = 0.50

RES_CAP = 0.90
PF_CAP = 100
HEMO_CAP = 40

# Sublimations
RUPTURE_PA_ACTIVATIONS = 2
RUPTURE_PA_GAIN = 2
RUPTURE_VIOLENTE_ACTIVATIONS = 2
RUPTURE_VIOLENTE_DMG_PCT = 0.40
TEMERITE_PER_BREAK = 0.12
TEMERITE_CAP = 0.30

INFLUENCE_LENTE_PER_TURN = 0.02
INFLUENCE_LENTE_CAP = 0.30

IVORY_CRIT_DMG_BONUS = 0.15
# V4.7 FIX-9: Ivory Dofus main effect: +200% of level = +358 mastery on first hit/turn
IVORY_FIRST_HIT_MASTERY = int(LVL * 2.0)  # 358

# ═══════════════════════════════════════════════════════════════════
#  SPELL DEFINITIONS — V4.7 FIX-1: real damage values at level 179
#  Interpolated from official tables between lvl 170 and 185
# ═══════════════════════════════════════════════════════════════════
# For level 179: we interpolate between 170 and 185 values
# ratio = (179-170)/(185-170) = 9/15 = 0.6

def _interp(v170, v185):
    """Interpolate damage at level 179 from level 170 and 185 values."""
    return int(v170 + (v185 - v170) * 0.6)

SPELLS = {
    # ── FIRE ──
    "premier_sang": {
        "name": "Premier Sang", "element": "fire", "ap": 2, "wp": 0,
        "base_dmg": _interp(42, 46),          # 44
        "base_dmg_crit": _interp(53, 58),      # 56
        "range_min": 0, "range_max": 1,
        "aoe": "line3h", "pf_generate": True, "pf_consume": False,
        "uses_per_turn": 3, "uses_per_target": 99,
        "hemo_apply": 10, "hemo_apply_if_already": 2,
        "pf_flat": 10,
        "melee": True, "line": False, "no_los": False,
        "special": "premier_sang",
    },
    "ouvrir_veines": {
        "name": "Ouvrir les Veines", "element": "fire", "ap": 2, "wp": 0,
        "base_dmg": _interp(46, 50),           # 48
        "base_dmg_crit": _interp(57, 62),      # 60
        "range_min": 0, "range_max": 1,
        "pf_generate": True, "pf_consume": False,
        "uses_per_turn": 3, "uses_per_target": 1,
        "hemo_apply": 0, "melee": True,
        "special": "ouvrir_veines",
    },
    "saignee_mortelle": {
        "name": "Saignee Mortelle", "element": "fire", "ap": 3, "wp": 0,
        "base_dmg": _interp(64, 69),           # 67
        "base_dmg_crit": _interp(80, 87),      # 84
        "range_min": 1, "range_max": 5,
        "pf_generate": True, "pf_consume": False,
        "uses_per_turn": 4, "uses_per_target": 3,
        "hemo_apply": 6, "melee": False, "line": True, "no_los": False,
        "special": "saignee_mortelle",
    },
    "chatiment": {
        "name": "Chatiment", "element": "fire", "ap": 4, "wp": 0,
        "base_dmg": _interp(99, 107),          # 104
        "base_dmg_crit": _interp(124, 134),    # 130
        "base_dmg_pf": _interp(124, 134),      # 130 (when PF consumed this turn)
        "base_dmg_pf_crit": _interp(155, 168), # 163
        "range_min": 0, "range_max": 0,
        "aoe": "cross1", "pf_generate": True, "pf_consume": False,
        "pf_flat": 20,
        "uses_per_turn": 2, "uses_per_target": 99,
        "hemo_apply": 0, "melee": True,
        "special": "chatiment",
    },
    "mise_a_mort": {
        "name": "Mise a Mort", "element": "fire", "ap": 6, "wp": 0,
        "base_dmg": _interp(148, 161),         # 156
        "base_dmg_crit": _interp(185, 201),    # 195
        "range_min": 0, "range_max": 1,
        "pf_generate": False, "pf_consume": True,
        "uses_per_turn": 1, "uses_per_target": 99,
        "hemo_apply": 0, "melee": True,
        "special": "mise_a_mort",
    },
    # ── WATER ──
    "kleptosram": {
        "name": "Kleptosram", "element": "water", "ap": 2, "wp": 0,
        "base_dmg": _interp(42, 46),           # 44
        "base_dmg_crit": _interp(53, 58),      # 56
        "range_min": 1, "range_max": 2,
        "pf_generate": True, "pf_consume": False,
        "pf_flat": 10,  # +5 if target is facing away (handled in logic)
        "uses_per_turn": 3, "uses_per_target": 99,
        "hemo_apply": 0, "melee": False, "line": True, "no_los": True,
        "special": "kleptosram",
    },
    "arnaque": {
        "name": "Arnaque", "element": "water", "ap": 2, "wp": 0,
        "base_dmg": _interp(42, 46),           # 44
        "base_dmg_crit": _interp(53, 58),      # 56
        "range_min": 1, "range_max": 2,
        "pf_generate": False, "pf_consume": True,
        "uses_per_turn": 3, "uses_per_target": 99,
        "hemo_apply": 0, "melee": False, "no_los": True,
        "special": "arnaque",
    },
    "attaque_letale": {
        "name": "Attaque Letale", "element": "water", "ap": 4, "wp": 0,
        "base_dmg": _interp(92, 100),          # 97
        "base_dmg_crit": _interp(115, 125),    # 121
        "range_min": 1, "range_max": 2,
        "pf_generate": True, "pf_consume": False,
        "pf_flat": 20,
        "uses_per_turn": 2, "uses_per_target": 99,
        "hemo_apply": 0, "melee": False, "no_los": True,
        "special": "attaque_letale",
    },
    "attaque_perfide": {
        "name": "Attaque Perfide", "element": "water", "ap": 3, "wp": 0,
        "base_dmg": _interp(85, 92),           # 89
        "base_dmg_crit": _interp(107, 116),    # 112
        "range_min": 1, "range_max": 2,
        "pf_generate": True, "pf_consume": False,
        "pf_flat": 15,
        "uses_per_turn": 3, "uses_per_target": 2,
        "hemo_apply": 0, "melee": False, "no_los": True,
        "special": "attaque_perfide",
    },
    "attaque_mortelle": {
        "name": "Attaque Mortelle", "element": "water", "ap": 5, "wp": 0,
        "base_dmg": _interp(124, 134),         # 130
        "base_dmg_crit": _interp(155, 168),    # 163
        "base_dmg_low": _interp(173, 188),     # 182 (target <50% HP)
        "base_dmg_low_crit": _interp(217, 235),# 228
        "range_min": 1, "range_max": 2,
        "pf_generate": True, "pf_consume": False,
        "pf_flat": 25,
        "uses_per_turn": 99, "uses_per_target": 1,
        "hemo_apply": 0, "melee": False, "no_los": True,
        "special": "attaque_mortelle",
    },
    # ── AIR ──
    "coup_penetrant": {
        "name": "Coup Penetrant", "element": "air", "ap": 4, "wp": 0,
        "base_dmg": _interp(92, 100),          # 97
        "base_dmg_crit": _interp(115, 125),    # 121
        "base_dmg_armor": _interp(46, 50),     # 48 (bonus on armor)
        "base_dmg_armor_crit": _interp(57, 62),# 60
        "range_min": 0, "range_max": 1,
        "aoe": "line3", "pf_generate": True, "pf_consume": False,
        "pf_flat": 20,
        "uses_per_turn": 2, "uses_per_target": 99,
        "hemo_apply": 0, "melee": True,
        "special": "coup_penetrant",
    },
    "fourberie": {
        "name": "Fourberie", "element": "air", "ap": 3, "wp": 0,
        "base_dmg": _interp(69, 75),           # 73
        "base_dmg_crit": _interp(86, 93),      # 90
        "range_min": 1, "range_max": 4,
        "pf_generate": True, "pf_consume": False,
        "pf_flat": 15,
        "uses_per_turn": 3, "uses_per_target": 1,
        "hemo_apply": 0, "melee": False, "line": True, "no_los": True,
        "special": "fourberie",
    },
    "coup_sournois": {
        "name": "Coup Sournois", "element": "air", "ap": 3, "wp": 0,
        "base_dmg": _interp(69, 75),           # 73
        "base_dmg_crit": _interp(86, 93),      # 90
        "range_min": 0, "range_max": 1,
        "pf_generate": True, "pf_consume": False,
        "pf_flat": 0,  # +5 per extra target hit
        "uses_per_turn": 4, "uses_per_target": 1,
        "hemo_apply": 0, "melee": True,
        "special": "coup_sournois",
    },
    "effroi": {
        "name": "Effroi", "element": "air", "ap": 3, "wp": 0,
        "base_dmg": _interp(59, 64),           # 62
        "base_dmg_crit": _interp(73, 80),      # 77
        "base_dmg_pf": _interp(78, 85),        # 82 (when PF consumed)
        "base_dmg_pf_crit": _interp(98, 106),  # 103
        "range_min": 0, "range_max": 1,
        "pf_generate": True, "pf_consume": False,
        "pf_flat": 15,
        "uses_per_turn": 3, "uses_per_target": 2,
        "hemo_apply": 0, "melee": True,
        "special": "effroi",
    },
    "traumatisme": {
        "name": "Traumatisme", "element": "air", "ap": 4, "wp": 0,
        "base_dmg": _interp(92, 100),          # 97
        "base_dmg_crit": _interp(115, 125),    # 121
        "range_min": 1, "range_max": 4,
        "pf_generate": False, "pf_consume": True,
        "uses_per_turn": 2, "uses_per_target": 99,
        "hemo_apply": 0, "melee": True, "line": True, "no_los": True,
        "special": "traumatisme",
    },
    # ── NEUTRAL ──
    "assassinat": {
        "name": "Assassinat", "element": "neutral", "ap": 1, "wp": 2,
        "base_dmg": 0, "base_dmg_crit": 0,
        "range_min": 1, "range_max": 3,
        "pf_generate": False, "pf_consume": False,
        "uses_per_turn": 1, "uses_per_target": 99,
        "hemo_apply": 0, "melee": False, "line": True, "no_los": True,
        "special": "assassinat", "cooldown": 2,
    },
    "peur": {
        "name": "Peur", "element": "neutral", "ap": 2, "wp": 0,
        "base_dmg": 0, "base_dmg_crit": 0,
        "range_min": 2, "range_max": 5,
        "pf_generate": False, "pf_consume": False,
        "uses_per_turn": 3, "uses_per_target": 99,
        "hemo_apply": 0, "melee": False, "line": True, "no_los": True,
        "special": "peur",
    },
    "surineur": {
        "name": "Surineur", "element": "neutral", "ap": 2, "wp": 0,
        "base_dmg": 0, "base_dmg_crit": 0,
        "range_min": 0, "range_max": 0,
        "pf_generate": False, "pf_consume": False,
        "uses_per_turn": 1, "uses_per_target": 99,
        "hemo_apply": 0, "melee": True,
        "special": "surineur", "cooldown": 2,
    },
    "galopade": {
        "name": "Galopade", "element": "neutral", "ap": 0, "wp": 1,
        "base_dmg": 0, "base_dmg_crit": 0,
        "range_min": 0, "range_max": 0,
        "pf_generate": False, "pf_consume": False,
        "uses_per_turn": 1, "uses_per_target": 99,
        "hemo_apply": 0, "melee": True,
        "special": "galopade", "cooldown": 2,
    },
    "entourloupe": {
        "name": "Entourloupe", "element": "neutral", "ap": 2, "wp": 1,
        "base_dmg": 0, "base_dmg_crit": 0,
        "range_min": 0, "range_max": 0,
        "pf_generate": False, "pf_consume": False,
        "uses_per_turn": 2, "uses_per_target": 99,
        "hemo_apply": 0, "melee": True,
        "special": "entourloupe",
    },
    "sournoiserie": {
        "name": "Sournoiserie", "element": "neutral", "ap": 2, "wp": 0,
        "base_dmg": 0, "base_dmg_crit": 0,
        "range_min": 1, "range_max": 6,
        "pf_generate": False, "pf_consume": False,
        "uses_per_turn": 1, "uses_per_target": 99,
        "hemo_apply": 0, "melee": False, "no_los": True,
        "special": "sournoiserie", "cooldown": 2,
    },
}

# ═══════════════════════════════════════════════════════════════════
#  PASSIVES — V4.7: corrected effects
# ═══════════════════════════════════════════════════════════════════
PASSIVES_DATA = {
    "assassin":              {"desc": "On kill: no PF, +1AP/PM/WP, heal 20%HP"},
    "localisation_quantique":{"desc": "Rear mastery -> melee. Ignore orientation."},
    "carnage":               {"desc": "+15% dmg, +10% vs armored, -30% heals"},  # V4.7 FIX-2
    "evasion":               {"desc": "+100% lvl as dodge"},
    "assaut_brutal":         {"desc": "Spells >=4AP (not MaM/Trauma): no PF gen, +5%dmg/AP"},  # V4.7 FIX-3
    "interception":          {"desc": "+100% lvl as lock"},
    "inspiration":           {"desc": "+10% dmg vs higher initiative targets"},  # V4.7 FIX-8
    "embuscade":             {"desc": "Traps: no AP refund, +1WP trigger, earth dmg"},
    "leurre":                {"desc": "Double explodes: 50%HP dmg, +20 hemo"},
    "retenue":               {"desc": "Invis broken only by >=4AP spells"},
    "motivation":            {"desc": "+1AP, -20% dmg, +10 willpower"},
    "duperie":               {"desc": "After receiving direct dmg: swap with Double"},
    "passe_passe":           {"desc": "Double: 4 range, swap on summon + end turn"},
    "peur_alternative":      {"desc": "Double's Peur attracts instead of pushes"},
    "piege_repulsion_II":    {"desc": "Repulsion trap: single target, push 3 in facing dir"},
    "piege_attraction_II":   {"desc": "Attraction trap: cross1, attract to center"},
    "piege_teleportation_II":{"desc": "Teleport trap: not consumed, 1 turn, allies only"},
    "medecine":              {"desc": "+30% heals, +25% armor given, -15% dmg"},
    "rock":                  {"desc": "+60% HP, +25% heals received, -25% dmg, -50% heals"},
    "assaut_letal":          {"desc": "Lethal Mark: Sram teleports behind mark bearer on kill"},
    "diversion_alternative": {"desc": "Double's Diversion turns targets away"},
    # hemophilie DISABLED in 1.91.2
}

# Valid passives for loadout generation (excluding hemophilie, medecine, rock which are not DPS)
VALID_PASSIVES = [
    "assassin", "localisation_quantique", "carnage", "evasion", "assaut_brutal",
    "interception", "inspiration", "embuscade", "leurre", "retenue",
    "motivation", "duperie", "passe_passe", "assaut_letal",
]

# ═══════════════════════════════════════════════════════════════════
#  ENEMY CONFIGURATIONS — V4.7: added sacapatate + obstacles + invuln
# ═══════════════════════════════════════════════════════════════════
COMBATS = {
    "sacapatate_0": [
        {"name": "Sacapatate", "hp": 100000, "res": 0.0, "mp": 0, "pos": (3, 4),
         "dmg": 0, "invuln_cycle": 0, "initiative": 0},
    ],
    "sacapatate_90": [
        {"name": "Sacapatate 90%", "hp": 100000, "res": 0.90, "mp": 0, "pos": (3, 4),
         "dmg": 0, "invuln_cycle": 0, "initiative": 0},
    ],
    "donjon_standard": [
        {"name": "Mob Std A",   "hp": 2800, "res": 0.35, "mp": 3, "pos": (4, 4),
         "dmg": 150, "invuln_cycle": 0, "initiative": 80},
        {"name": "Mob Std B",   "hp": 2800, "res": 0.35, "mp": 3, "pos": (6, 3),
         "dmg": 150, "invuln_cycle": 0, "initiative": 80},
        {"name": "Boss Tanky",  "hp": 5500, "res": 0.50, "mp": 2, "pos": (2, 3),
         "dmg": 250, "invuln_cycle": 0, "initiative": 120},
        {"name": "Invoc",       "hp": 1500, "res": 0.20, "mp": 4, "pos": (5, 4),
         "dmg": 100, "invuln_cycle": 0, "initiative": 60},
        {"name": "Tank Phys",   "hp": 3600, "res": 0.55, "mp": 2, "pos": (3, 7),
         "dmg": 200, "invuln_cycle": 0, "initiative": 100},
        {"name": "DPS Fragile", "hp": 1800, "res": 0.25, "mp": 5, "pos": (8, 5),
         "dmg": 300, "invuln_cycle": 0, "initiative": 140},
    ],
    "boss_rush": [
        {"name": "Boss Alpha", "hp": 12000, "res": 0.55, "mp": 2, "pos": (4, 3),
         "dmg": 400, "invuln_cycle": 3, "initiative": 160},
        {"name": "Boss Beta",  "hp": 9000,  "res": 0.50, "mp": 3, "pos": (6, 5),
         "dmg": 350, "invuln_cycle": 0, "initiative": 130},
        {"name": "Boss Gamma", "hp": 7000,  "res": 0.45, "mp": 3, "pos": (3, 6),
         "dmg": 300, "invuln_cycle": 0, "initiative": 110},
    ],
    "salle_variee": [
        {"name": "Melee A",     "hp": 3000, "res": 0.40, "mp": 4, "pos": (3, 3),
         "dmg": 200, "invuln_cycle": 0, "initiative": 90},
        {"name": "Melee B",     "hp": 3000, "res": 0.40, "mp": 4, "pos": (5, 3),
         "dmg": 200, "invuln_cycle": 0, "initiative": 90},
        {"name": "Rangeur",     "hp": 2200, "res": 0.30, "mp": 3, "pos": (7, 6),
         "dmg": 250, "invuln_cycle": 0, "initiative": 120},
        {"name": "Support",     "hp": 2500, "res": 0.35, "mp": 2, "pos": (2, 6),
         "dmg": 100, "invuln_cycle": 0, "initiative": 70},
        {"name": "Tank",        "hp": 4500, "res": 0.55, "mp": 2, "pos": (4, 5),
         "dmg": 150, "invuln_cycle": 0, "initiative": 100},
        {"name": "Glass Canon", "hp": 1500, "res": 0.20, "mp": 5, "pos": (9, 4),
         "dmg": 400, "invuln_cycle": 0, "initiative": 150},
    ],
}

# Obstacles (cells that block movement)
OBSTACLES = {
    "donjon_standard": [(5, 5), (6, 6)],
    "boss_rush": [(5, 4)],
    "salle_variee": [(4, 4), (6, 5)],
    "sacapatate_0": [],
    "sacapatate_90": [],
}

SRAM_START_POS = (1, 4)
SRAM_INITIATIVE = 142

# ═══════════════════════════════════════════════════════════════════
#  UTILITY
# ═══════════════════════════════════════════════════════════════════

def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def cap_wp(sram):
    sram["wp"] = min(WP_CAP, sram["wp"])

def cap_mp(sram):
    sram["mp"] = min(MP_CAP_MAX, sram["mp"])

def init_worker():
    seed = int.from_bytes(os.urandom(8), 'big') ^ os.getpid() ^ int(time.time_ns())
    random.seed(seed)

# ═══════════════════════════════════════════════════════════════════
#  ARMOR BREAK & SUBLIMATION TRIGGERS
# ═══════════════════════════════════════════════════════════════════

def handle_armor_interaction(dmg, sram, target, bypasses_armor):
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
    triggers = []
    if sram["rupture_pa_used"] < RUPTURE_PA_ACTIVATIONS:
        sram["ap"] += RUPTURE_PA_GAIN
        sram["rupture_pa_used"] += 1
        triggers.append(f"Rupture PA: +{RUPTURE_PA_GAIN}AP (#{sram['rupture_pa_used']}/{RUPTURE_PA_ACTIVATIONS})")
    if sram["rupture_violente_used"] < RUPTURE_VIOLENTE_ACTIVATIONS:
        rv_dmg = int(LVL * RUPTURE_VIOLENTE_DMG_PCT * (1 - target["res"]))
        target["hp"] -= rv_dmg
        sram["rupture_violente_used"] += 1
        triggers.append(f"Rupture Violente: {rv_dmg} dmg (#{sram['rupture_violente_used']}/{RUPTURE_VIOLENTE_ACTIVATIONS})")
        sram["turn_dmg_bonus"] += rv_dmg
    if full_break and sram["combat_temerite"] < TEMERITE_CAP:
        sram["combat_temerite"] = min(TEMERITE_CAP, sram["combat_temerite"] + TEMERITE_PER_BREAK)
        triggers.append(f"Temerite: +{TEMERITE_PER_BREAK*100:.0f}% dmg (total: {sram['combat_temerite']*100:.0f}%)")
    return triggers

# ═══════════════════════════════════════════════════════════════════
#  DAMAGE CALCULATION — V4.7: real base values + corrected passives
# ═══════════════════════════════════════════════════════════════════

def calc_dmg(spell_key, sram, target, passives, pf_consumed_this_turn):
    sp = SPELLS[spell_key]
    if sp["base_dmg"] == 0:
        return 0, False, "no-dmg"

    # V4.7 FIX-12: invulnerability check
    if target.get("invuln", False):
        return 0, False, "invuln"

    elem = sp["element"]
    mastery = MAST.get(elem, 0)

    # Localisation Quantique: rear mastery -> melee
    has_lq = "localisation_quantique" in passives
    effective_melee = MAST_MELEE + (MAST_REAR if has_lq else 0)

    is_melee = sp.get("melee", False) or manhattan(sram["pos"], target["pos"]) <= 1
    if is_melee:
        mastery += effective_melee

    # V4.7 FIX-9: Ivory Dofus first hit mastery bonus
    if sram.get("ivory_first_hit", False):
        mastery += IVORY_FIRST_HIT_MASTERY
        sram["ivory_first_hit"] = False

    dmg_mult = 1.0 + DMG_BONUS

    # V4.7 FIX-2: Carnage corrected
    if "carnage" in passives:
        dmg_mult += CARNAGE_DMG_BONUS
        if target.get("armor", 0) > 0:
            dmg_mult += CARNAGE_ARMOR_DMG_BONUS

    if "motivation" in passives:
        dmg_mult -= 0.20

    # V4.7 FIX-8: Inspiration corrected — +10% vs higher initiative targets
    if "inspiration" in passives:
        if target.get("initiative", 0) > SRAM_INITIATIVE:
            dmg_mult += 0.10

    # Isolated bonus
    alive_enemies = [e for e in sram["enemies"] if e["hp"] > 0]
    is_isolated = all(
        other is target or manhattan(other["pos"], target["pos"]) > 2
        for other in alive_enemies
    )
    # Double on field also triggers the +50% bonus
    if is_isolated or sram.get("double_on_field", False):
        dmg_mult += INNATE_ISO_BONUS

    # V4.7 FIX-3: Assaut Brutal excludes Mise a Mort and Traumatisme
    if "assaut_brutal" in passives and sp["ap"] >= 4:
        if spell_key not in ("mise_a_mort", "traumatisme"):
            if sp.get("pf_generate", False):
                dmg_mult += 0.05 * sp["ap"]

    # Hemorrhage bonus
    hemo = target.get("hemo", 0)
    if hemo > 0:
        dmg_mult += hemo * 0.01

    # Temerite (combat-level, persists)
    dmg_mult += sram.get("combat_temerite", 0)

    # PF consumer bonus: +1% per PF
    pf_bonus_mult = 0
    if sp["pf_consume"]:
        pf_bonus_mult = sram["pf"] * 0.01

    # Crit calculation
    crit_chance = BASE_CRIT + sram.get("influence_lente_bonus", 0)
    crit = random.random() < min(1.0, crit_chance)

    # V4.7 FIX-1: select correct base damage
    if crit:
        base = sp.get("base_dmg_crit", sp["base_dmg"])
    else:
        base = sp["base_dmg"]

    # V4.7 FIX-15: Chatiment enhanced when PF consumed this turn
    if spell_key == "chatiment" and pf_consumed_this_turn:
        if crit:
            base = sp.get("base_dmg_pf_crit", base)
        else:
            base = sp.get("base_dmg_pf", base)

    # V4.7 FIX-16: Effroi enhanced when PF consumed
    if spell_key == "effroi" and pf_consumed_this_turn:
        if crit:
            base = sp.get("base_dmg_pf_crit", base)
        else:
            base = sp.get("base_dmg_pf", base)

    # V4.7 FIX-14: Attaque Mortelle enhanced when target <50% HP
    if spell_key == "attaque_mortelle" and target["hp"] < target["max_hp"] * 0.5:
        if crit:
            base = sp.get("base_dmg_low_crit", base)
        else:
            base = sp.get("base_dmg_low", base)

    # Crit multiplier
    crit_mult = 1.0
    if crit:
        crit_mult = 1.25
        mastery += MAST_CRIT
        # Ivory Dofus: +15% crit dmg on >=4AP or >=1WP
        if sp["ap"] >= 4 or sp.get("wp", 0) >= 1:
            crit_mult += IVORY_CRIT_DMG_BONUS

    # Surineur buff
    if sram.get("surineur_active", False):
        if crit:
            crit_mult += 0.20
        if has_lq:
            dmg_mult += 0.20

    # V4.7 FIX-4: Assassinat resistance reduction (flat -100)
    res_value = target.get("res_flat", 0)
    if target.get("assassinat_debuff", False):
        res_value -= 100
    # Convert flat res to percentage (approximate: res / (res + 5*lvl))
    effective_res = target["res"]
    if target.get("assassinat_debuff", False):
        # -100 flat res translates roughly to -10-15% depending on base
        effective_res = max(0, effective_res - 0.12)
    effective_res = min(effective_res, RES_CAP)

    # Damage formula: base * (1 + mastery/100) * multipliers * (1 - res)
    noise = random.uniform(0.92, 1.08)
    dmg = base * (1 + mastery / 100) * dmg_mult * crit_mult * (1 + pf_bonus_mult) * (1 - effective_res) * noise

    details = f"{elem.upper()} {'CRIT ' if crit else ''}mast:{mastery}"
    return max(0, int(dmg)), crit, details

# ═══════════════════════════════════════════════════════════════════
#  PF MANAGEMENT — V4.7: uses pf_flat from spell data
# ═══════════════════════════════════════════════════════════════════

def apply_pf_generation(spell_key, sram, target, passives):
    sp = SPELLS[spell_key]
    if sp["pf_consume"] or sp["element"] == "neutral":
        return 0, "no PF gen"

    # V4.7 FIX-3: Assaut Brutal blocks PF on >=4AP spells (EXCEPT mise_a_mort, traumatisme)
    if "assaut_brutal" in passives and sp["ap"] >= 4:
        if spell_key not in ("mise_a_mort", "traumatisme"):
            if sp.get("pf_generate", False):
                return 0, f"assaut_brutal blocks PF (+{sp['ap']*5}%dmg)"

    # Use pf_flat if defined, otherwise ap * 5
    pf_gained = sp.get("pf_flat", sp["ap"] * 5)
    expl = f"+{pf_gained}PF"

    # Kleptosram: +5 if target is from behind (simplified: 50% chance)
    if spell_key == "kleptosram" and random.random() < 0.5:
        pf_gained += 5
        expl += "+5dos"

    # Ouvrir les Veines: +1 PF per hemo level consumed
    if spell_key == "ouvrir_veines":
        h = target.get("hemo", 0)
        if h > 0:
            pf_gained += h
            expl += f"+{h}hemo"

    # Coup Sournois: +5 per extra target
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
    sram["ap"] += tiers
    sram["mp"] += tiers
    sram["wp"] += tiers
    cap_wp(sram)
    cap_mp(sram)

    hemo_add = tiers * 10
    old_h = target.get("hemo", 0)
    target["hemo"] = min(HEMO_CAP, old_h + hemo_add)

    expl = f"consumed {pf}PF ({tiers}x25): +{tiers}AP +{tiers}PM +{tiers}WP +{target['hemo']-old_h}hemo"
    return pf, tiers, tiers, tiers, target["hemo"] - old_h, expl

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
        heal = int(sram["max_hp"] * 0.20)
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
#  SPELL CAST
# ═══════════════════════════════════════════════════════════════════

def can_cast(spell_key, sram, target, turn_uses, target_uses):
    sp = SPELLS[spell_key]
    if sram["ap"] < sp["ap"]:
        return False
    if sram["wp"] < sp.get("wp", 0):
        return False
    if target["hp"] <= 0:
        return False
    if target.get("invuln", False):
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

    # V4.7 FIX-11: hard-block Perfide if not enough AP to break armor after
    if spell_key == "attaque_perfide":
        ap_after = sram["ap"] - sp["ap"]
        if ap_after < 2:
            return False

    return True

def apply_spell(spell_key, sram, target, passives, turn_uses, target_uses, pf_consumed_this_turn):
    sp = SPELLS[spell_key]

    snap_before = {
        "ap": sram["ap"], "mp": sram["mp"], "wp": sram["wp"], "pf": sram["pf"],
        "sram_hp": sram["hp"], "sram_pos": sram["pos"],
        "target_hp": target["hp"], "target_hemo": target.get("hemo", 0),
        "target_armor": target.get("armor", 0), "target_pos": target["pos"],
    }

    # Pay costs
    sram["ap"] -= sp["ap"]
    sram["wp"] -= sp.get("wp", 0)
    snap_after_cost = {"ap": sram["ap"], "mp": sram["mp"], "wp": sram["wp"], "pf": sram["pf"]}

    turn_uses[spell_key] = turn_uses.get(spell_key, 0) + 1
    target_uses[f"{spell_key}_{id(target)}"] = target_uses.get(f"{spell_key}_{id(target)}", 0) + 1

    if sp.get("cooldown", 0) > 0:
        sram.setdefault("cooldowns", {})[spell_key] = sp["cooldown"] + 1

    # Galopade special: +3 PM, no damage
    if spell_key == "galopade":
        sram["mp"] += 3
        cap_mp(sram)
        snap_final = {"ap": sram["ap"], "mp": sram["mp"], "wp": sram["wp"], "pf": sram["pf"],
                      "sram_hp": sram["hp"], "target_hp": target["hp"],
                      "target_hemo": target.get("hemo", 0), "target_armor": target.get("armor", 0)}
        log = {"spell": sp["name"], "spell_key": spell_key, "target": "self",
               "element": "neutral", "cost": f"-{sp['wp']}WP",
               "cost_ap": 0, "cost_wp": sp["wp"],
               "dmg": 0, "actual_dmg": 0, "crit": False,
               "snap_before": snap_before, "snap_after_cost": snap_after_cost,
               "snap_after_pf": snap_after_cost, "snap_after_sub": snap_after_cost,
               "snap_final": snap_final, "pf_gen": "", "pf_consume": "",
               "pf_consumed_amount": 0, "pf_refund_ap": 0, "pf_refund_mp": 0, "pf_refund_wp": 0,
               "sub_triggers": [], "armor_given": 0, "armor_absorbed": 0, "armor_broken": False,
               "hemo_applied": 0, "heal": 0, "kill": False, "kill_rewards": "",
               "letale_refund": "", "alive": sum(1 for e in sram["enemies"] if e["hp"] > 0),
               "total_kills": sram["kills"], "galopade_pm": "+3PM"}
        return log, pf_consumed_this_turn

    # Surineur special: buff for next turn
    if spell_key == "surineur":
        sram["surineur_pending"] = True
        snap_final = {"ap": sram["ap"], "mp": sram["mp"], "wp": sram["wp"], "pf": sram["pf"],
                      "sram_hp": sram["hp"], "target_hp": target["hp"],
                      "target_hemo": target.get("hemo", 0), "target_armor": target.get("armor", 0)}
        log = {"spell": sp["name"], "spell_key": spell_key, "target": "self",
               "element": "neutral", "cost": f"-{sp['ap']}AP",
               "cost_ap": sp["ap"], "cost_wp": 0,
               "dmg": 0, "actual_dmg": 0, "crit": False,
               "snap_before": snap_before, "snap_after_cost": snap_after_cost,
               "snap_after_pf": snap_after_cost, "snap_after_sub": snap_after_cost,
               "snap_final": snap_final, "pf_gen": "", "pf_consume": "",
               "pf_consumed_amount": 0, "pf_refund_ap": 0, "pf_refund_mp": 0, "pf_refund_wp": 0,
               "sub_triggers": [], "armor_given": 0, "armor_absorbed": 0, "armor_broken": False,
               "hemo_applied": 0, "heal": 0, "kill": False, "kill_rewards": "",
               "letale_refund": "", "alive": sum(1 for e in sram["enemies"] if e["hp"] > 0),
               "total_kills": sram["kills"], "surineur_buff": "next turn +20%crit +20%dos"}
        return log, pf_consumed_this_turn

    # PF generation
    pf_gained, pf_expl = apply_pf_generation(spell_key, sram, target, passives)

    # Damage
    dmg, crit, dmg_details = calc_dmg(spell_key, sram, target, passives, pf_consumed_this_turn[0])

    # PF consumption
    pf_consumed, ref_ap, ref_mp, ref_wp, ref_hemo, pf_con_expl = apply_pf_consumption(spell_key, sram, target)
    if pf_consumed > 0:
        pf_consumed_this_turn[0] = True

    snap_after_pf = {"ap": sram["ap"], "mp": sram["mp"], "wp": sram["wp"], "pf": sram["pf"]}

    # Armor interaction
    bypasses_armor = (spell_key == "attaque_perfide")
    actual_dmg, armor_broken, armor_absorbed = handle_armor_interaction(dmg, sram, target, bypasses_armor)
    target["hp"] -= actual_dmg

    armor_given = 0
    if spell_key == "attaque_perfide":
        armor_given = int(dmg * 0.40)
        target["armor"] = target.get("armor", 0) + armor_given

    # V4.7 FIX-17: Coup Penetrant bonus damage on armor
    bonus_armor_dmg = 0
    if spell_key == "coup_penetrant" and target.get("armor", 0) > 0:
        if crit:
            bonus_base = sp.get("base_dmg_armor_crit", 0)
        else:
            bonus_base = sp.get("base_dmg_armor", 0)
        if bonus_base > 0:
            bonus_armor_dmg = int(bonus_base * (1 + MAST.get("air", 0) / 100) * (1 - target["res"]))
            arm = target.get("armor", 0)
            absorbed = min(arm, bonus_armor_dmg)
            target["armor"] = max(0, arm - bonus_armor_dmg)
            if target["armor"] == 0 and absorbed > 0:
                armor_broken = True

    # Sublimation triggers
    sub_triggers = []
    if armor_absorbed > 0 or armor_broken:
        sub_triggers = trigger_sublimations_on_armor_break(sram, target, armor_broken)

    snap_after_sub = {"ap": sram["ap"], "mp": sram["mp"], "wp": sram["wp"]}

    # Hemo application
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

    # V4.7 FIX-20: Saignee Mortelle lifesteal from hemorrhage damage
    heal = 0
    if spell_key == "saignee_mortelle":
        hemo_dmg = int(dmg * target.get("hemo", 0) * 0.01)
        if hemo_dmg > 0:
            heal = hemo_dmg
            sram["hp"] = min(sram["max_hp"], sram["hp"] + heal)

    # Ouvrir les Veines: consume hemo, heal
    if spell_key == "ouvrir_veines":
        h = target.get("hemo", 0)
        if h > 0:
            heal = int(sram["max_hp"] * h * 0.01)
            sram["hp"] = min(sram["max_hp"], sram["hp"] + heal)
            target["hemo"] = 0

    # Arnaque: heal from PF
    if spell_key == "arnaque" and pf_consumed > 0:
        heal = int(sram["max_hp"] * pf_consumed * 0.005)
        sram["hp"] = min(sram["max_hp"], sram["hp"] + heal)

    # V4.7 FIX-18: Fourberie teleports behind target
    if spell_key == "fourberie" and target["hp"] > 0:
        tx, ty = target["pos"]
        sram["pos"] = (tx + 1, ty)  # simplified: behind = +1 x

    # V4.7 FIX-19: Coup Sournois pushback
    if spell_key == "coup_sournois":
        sx, sy = sram["pos"]
        tx, ty = target["pos"]
        dx = sx - tx
        dy = sy - ty
        if dx != 0 or dy != 0:
            ndx = (1 if dx > 0 else -1) if dx != 0 else 0
            ndy = (1 if dy > 0 else -1) if dy != 0 else 0
            sram["pos"] = (sx + ndx * 2, sy + ndy * 2)

    # Kill check
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

    # Assassinat effect
    if spell_key == "assassinat":
        target["assassinat_debuff"] = True

    if spell_key == "saignee_mortelle" and target["hp"] > 0:
        target["saignee_replica"] = True

    snap_final = {
        "ap": sram["ap"], "mp": sram["mp"], "wp": sram["wp"], "pf": sram["pf"],
        "sram_hp": sram["hp"], "sram_pos": sram["pos"],
        "target_hp": target["hp"], "target_hemo": target.get("hemo", 0),
        "target_armor": target.get("armor", 0),
    }

    log = {
        "spell": sp["name"], "spell_key": spell_key, "target": target["name"],
        "element": sp["element"],
        "cost_ap": sp["ap"], "cost_wp": sp.get("wp", 0),
        "cost": f"-{sp['ap']}AP" + (f"-{sp['wp']}WP" if sp.get('wp',0)>0 else ""),
        "dmg": dmg, "actual_dmg": actual_dmg, "crit": crit,
        "snap_before": snap_before, "snap_after_cost": snap_after_cost,
        "snap_after_pf": snap_after_pf, "snap_after_sub": snap_after_sub,
        "snap_final": snap_final,
        "pf_gen": pf_expl,
        "pf_consume": pf_con_expl if pf_consumed > 0 else "",
        "pf_consumed_amount": pf_consumed,
        "pf_refund_ap": ref_ap, "pf_refund_mp": ref_mp, "pf_refund_wp": ref_wp,
        "sub_triggers": sub_triggers,
        "armor_given": armor_given, "armor_absorbed": armor_absorbed, "armor_broken": armor_broken,
        "hemo_applied": hemo_applied, "heal": heal,
        "kill": killed, "kill_rewards": kill_rewards_str, "letale_refund": letale_refund,
        "alive": sum(1 for e in sram["enemies"] if e["hp"] > 0),
        "total_kills": sram["kills"],
    }
    return log, pf_consumed_this_turn

# ═══════════════════════════════════════════════════════════════════
#  DOUBLE SUB-TURN — V4.7 FIX-6
# ═══════════════════════════════════════════════════════════════════

def simulate_double_turn(sram, passives):
    """Simplified Double turn: 8 AP, uses Contact Letal + attacks."""
    if not sram.get("double_on_field", False):
        return 0, []

    double_ap = 8
    double_dmg = 0
    double_actions = []
    enemies = [e for e in sram["enemies"] if e["hp"] > 0]
    if not enemies:
        return 0, []

    # Contact Letal: 2 AP, marks target
    if double_ap >= 2 and not sram.get("contact_letal_cd", False):
        target = min(enemies, key=lambda e: e["hp"])
        double_ap -= 2
        target["contact_letal_mark"] = True
        sram["contact_letal_cd"] = True
        double_actions.append(f"[Double] Contact Letal > {target['name']}")

    # Peur: 2 AP, push (positioning utility — just log it)
    uses = 0
    while double_ap >= 2 and uses < 2 and enemies:
        double_ap -= 2
        uses += 1
        double_actions.append(f"[Double] Peur (push)")

    return double_dmg, double_actions

# ═══════════════════════════════════════════════════════════════════
#  MOVEMENT
# ═══════════════════════════════════════════════════════════════════

def move_toward(sram, target_pos, max_steps=99, obstacles=None):
    obs = set(obstacles) if obstacles else set()
    moved = 0
    while sram["mp"] > 0 and moved < max_steps:
        sx, sy = sram["pos"]
        tx, ty = target_pos
        if manhattan(sram["pos"], target_pos) <= 1:
            break
        dx = (1 if tx > sx else -1) if tx != sx else 0
        dy = (1 if ty > sy else -1) if ty != sy else 0

        # Try primary direction
        new_pos = None
        if abs(tx - sx) >= abs(ty - sy) and dx != 0:
            candidate = (sx + dx, sy)
            if candidate not in obs:
                new_pos = candidate
        if new_pos is None and dy != 0:
            candidate = (sx, sy + dy)
            if candidate not in obs:
                new_pos = candidate
        if new_pos is None and dx != 0:
            candidate = (sx + dx, sy)
            if candidate not in obs:
                new_pos = candidate
        if new_pos is None:
            break

        sram["pos"] = new_pos
        sram["mp"] -= 1
        moved += 1
    return moved

# ═══════════════════════════════════════════════════════════════════
#  GREEDY ACTION SELECTION
# ═══════════════════════════════════════════════════════════════════

def find_best_action(sram, deck, passives, turn_uses, target_uses, pf_consumed_this_turn):
    alive = [e for e in sram["enemies"] if e["hp"] > 0 and not e.get("invuln", False)]
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

            # Galopade: score based on mobility need
            if spell_key == "galopade":
                nearest = min(alive, key=lambda e: manhattan(sram["pos"], e["pos"]))
                dist = manhattan(sram["pos"], nearest["pos"])
                if dist > 2 and sram["mp"] <= 1:
                    score = 6000.0  # High priority when we need mobility
                else:
                    score = 0.0
                score *= random.uniform(0.85, 1.15)
                if score > best_score:
                    best_score = score
                    best_spell = spell_key
                    best_target = target
                continue

            # Surineur: score based on upcoming turns
            if spell_key == "surineur":
                score = 3000.0 if sram["ap"] >= 10 else 500.0
                score *= random.uniform(0.85, 1.15)
                if score > best_score:
                    best_score = score
                    best_spell = spell_key
                    best_target = target
                continue

            dmg, _, _ = calc_dmg(spell_key, sram, target, passives, pf_consumed_this_turn[0])
            score = float(dmg)

            if target["hp"] <= dmg * 1.1:
                score *= 1.5
                # Contact Letal mark: killing marked target gives +2 AP
                if target.get("contact_letal_mark", False):
                    score *= 1.8

            if sp["pf_consume"] and sram["pf"] >= 50:
                score *= (1 + sram["pf"] * 0.01)
            if sp["pf_consume"] and sram["pf"] < 25:
                score *= 0.3

            # Attaque Perfide (already hard-blocked if AP < 2 in can_cast)
            if spell_key == "attaque_perfide":
                remaining = RUPTURE_PA_ACTIVATIONS - sram["rupture_pa_used"]
                if remaining > 0:
                    score *= 2.0
                else:
                    score *= 0.8

            # Armor break priority
            if target.get("armor", 0) > 0 and spell_key != "attaque_perfide":
                remaining = RUPTURE_PA_ACTIVATIONS - sram["rupture_pa_used"]
                if remaining > 0:
                    score += 8000 * remaining

            # Assassinat: high value on boss targets
            if spell_key == "assassinat":
                if target["hp"] > 3000 and current_ap >= 7:
                    score = max(score, 7000)
                else:
                    score = max(score, 3000)

            score *= random.uniform(0.85, 1.15)

            if score > best_score:
                best_score = score
                best_spell = spell_key
                best_target = target

    return best_spell, best_target

# ═══════════════════════════════════════════════════════════════════
#  TURN SIMULATION
# ═══════════════════════════════════════════════════════════════════

def run_turn(sram, deck, passives, turn_num, combat_name):
    turn_uses = {}
    target_uses = {}
    pf_consumed_this_turn = [False]
    turn_dmg = 0
    actions = []
    obstacles = OBSTACLES.get(combat_name, [])

    # Reset per-turn counters
    sram["rupture_pa_used"] = 0
    sram["rupture_violente_used"] = 0
    sram["turn_dmg_bonus"] = 0

    # V4.7 FIX-9: Ivory Dofus first-hit mastery resets each turn
    sram["ivory_first_hit"] = True

    # Surineur activation from previous turn
    if sram.get("surineur_pending", False):
        sram["surineur_active"] = True
        sram["surineur_pending"] = False
    else:
        sram["surineur_active"] = False

    # Cooldowns
    for k in list(sram.get("cooldowns", {}).keys()):
        sram["cooldowns"][k] -= 1
        if sram["cooldowns"][k] <= 0:
            del sram["cooldowns"][k]

    # Contact Letal cooldown
    if sram.get("contact_letal_cd", False):
        sram["contact_letal_cd"] = False

    # V4.7 FIX-12: Boss invulnerability phases
    for e in sram["enemies"]:
        cycle = e.get("invuln_cycle", 0)
        if cycle > 0:
            e["invuln"] = (turn_num % cycle == 0)
        else:
            e["invuln"] = False

    # Influence Lente
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
            # V4.7 FIX-4: target gains +100 res if survived
            # (simplified: just remove the debuff, the +100 buff makes them tankier)
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
                           "hemo_applied": e["hemo"] - old_h, "heal": hemo_dmg_portion})
            if e["hp"] <= 0:
                e["hp"] = 0
                apply_kill_rewards(sram, e, passives)
            e["saignee_replica"] = False

    # Initial movement
    alive = [e for e in sram["enemies"] if e["hp"] > 0 and not e.get("invuln", False)]
    if alive:
        nearest = min(alive, key=lambda e: manhattan(sram["pos"], e["pos"]))
        mp_before = sram["mp"]
        pos_before = sram["pos"]
        moved = move_toward(sram, nearest["pos"], obstacles=obstacles)
        if moved > 0:
            actions.append({"spell": f"[Move {moved}PM]", "dmg": 0,
                           "before": {"mp": mp_before, "pos": pos_before},
                           "after": {"mp": sram["mp"], "pos": sram["pos"]}})

    # Main loop
    for _ in range(30):
        alive = [e for e in sram["enemies"] if e["hp"] > 0]
        if not alive:
            break

        spell_key, target = find_best_action(sram, deck, passives, turn_uses, target_uses, pf_consumed_this_turn)

        if spell_key is None:
            alive_targets = [e for e in alive if not e.get("invuln", False)]
            if not alive_targets:
                break
            nearest = min(alive_targets, key=lambda e: manhattan(sram["pos"], e["pos"]))
            if sram["mp"] > 0 and manhattan(sram["pos"], nearest["pos"]) > 1:
                mp_before = sram["mp"]
                moved = move_toward(sram, nearest["pos"], max_steps=3, obstacles=obstacles)
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

        # Contact Letal kill bonus
        if alog.get("kill") and target.get("contact_letal_mark", False):
            sram["ap"] += 2
            target["contact_letal_mark"] = False
            actions.append({"spell": "[Contact Letal: +2AP on marked kill]", "dmg": 0})

    # Double sub-turn
    double_dmg, double_acts = simulate_double_turn(sram, passives)
    turn_dmg += double_dmg
    for da in double_acts:
        actions.append({"spell": da, "dmg": 0})

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
        "temerite": sram.get("combat_temerite", 0),
        "rupture_pa": sram["rupture_pa_used"],
        "influence_lente": sram.get("influence_lente_bonus", 0),
    }

# ═══════════════════════════════════════════════════════════════════
#  SIMULATION
# ═══════════════════════════════════════════════════════════════════

def simulate_one(args):
    deck, passive_list, combat_name = args
    passives = set(passive_list)

    hp = BASE_HP
    # V4.7 FIX-2: Carnage does NOT reduce HP
    ap = BASE_AP
    if "motivation" in passives:
        ap += 1

    sram = {
        "hp": hp, "max_hp": hp, "ap": ap, "base_ap": ap,
        "mp": BASE_MP, "base_mp": BASE_MP,
        "wp": BASE_WP, "base_wp": BASE_WP,
        "pf": START_PF, "pos": SRAM_START_POS,
        "kills": 0, "dead": False, "assassin_state": False,
        "cooldowns": {}, "surineur_active": False, "surineur_pending": False,
        "influence_lente_bonus": 0.0,
        "rupture_pa_used": 0, "rupture_violente_used": 0,
        "combat_temerite": 0.0,
        "turn_dmg_bonus": 0,
        "ivory_first_hit": True,
        "double_on_field": "double" in [s for s in deck],  # simplified
        "contact_letal_cd": False,
        "enemies": [],
    }

    enemies = []
    for et in COMBATS[combat_name]:
        enemies.append({
            "name": et["name"], "hp": et["hp"], "max_hp": et["hp"],
            "res": et["res"], "mp": et["mp"], "pos": et["pos"], "dmg": et["dmg"],
            "hemo": 0, "armor": 0, "invuln": False,
            "invuln_cycle": et.get("invuln_cycle", 0),
            "initiative": et.get("initiative", 0),
            "assassinat_debuff": False, "assassinat_end_of_turn_buff": False,
            "saignee_replica": False, "contact_letal_mark": False,
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

        td, tl = run_turn(sram, available, passives, t, combat_name)
        total_dmg += td
        turn_logs.append(tl)

    return {
        "total_dmg": total_dmg, "kills": sram["kills"],
        "survived": not sram["dead"], "turns": len(turn_logs),
        "turn_logs": turn_logs, "deck": deck,
        "passives": passive_list, "combat": combat_name,
    }

# ═══════════════════════════════════════════════════════════════════
#  LOADOUT GENERATION — V4.7: expanded with neutral utility
# ═══════════════════════════════════════════════════════════════════

def gen_all_loadouts():
    fire = ["premier_sang", "ouvrir_veines", "saignee_mortelle", "chatiment", "mise_a_mort"]
    water = ["kleptosram", "arnaque", "attaque_letale", "attaque_perfide", "attaque_mortelle"]
    air = ["coup_penetrant", "fourberie", "coup_sournois", "effroi", "traumatisme"]
    neutral = ["assassinat", "peur", "surineur", "galopade", "entourloupe", "sournoiserie"]

    deck_templates = [
        # Core fire+water + utility
        fire + water + ["assassinat", "peur"],
        fire + water + ["assassinat", "galopade"],
        fire + water + ["surineur", "assassinat"],
        fire + water + ["fourberie", "assassinat"],
        fire + water + ["fourberie", "galopade"],
        # Fire+water + air splash
        fire + water[:4] + ["fourberie", "coup_penetrant", "traumatisme"],
        fire + water[:4] + ["fourberie", "traumatisme", "assassinat"],
        fire + water + ["effroi", "traumatisme"],
        # Tri-element
        fire + water[:3] + air[:3] + ["assassinat"],
        fire + water[:3] + air[:3] + ["galopade"],
        fire + air[:3] + water[:3] + ["assassinat"],
        # Air heavy
        fire + air[:4] + water[:2] + ["assassinat"],
        # Mixed utility
        fire + water + ["fourberie", "effroi"],
        fire + water[:3] + ["fourberie", "coup_sournois", "assassinat", "peur"],
        fire + water[:4] + ["coup_sournois", "effroi", "assassinat"],
        fire + water[:3] + air[:3] + ["peur"],
        # Full fire+water no neutral
        fire + water + ["coup_penetrant", "fourberie"],
    ]

    passive_sets = [
        ["localisation_quantique", "assassin", "carnage", "evasion", "assaut_brutal"],
        ["localisation_quantique", "assassin", "carnage", "evasion", "interception"],
        ["localisation_quantique", "assassin", "carnage", "assaut_brutal", "interception"],
        ["localisation_quantique", "assassin", "carnage", "retenue", "evasion"],
        ["localisation_quantique", "assassin", "carnage", "embuscade", "evasion"],
        ["localisation_quantique", "assassin", "carnage", "leurre", "evasion"],
        ["localisation_quantique", "assassin", "carnage", "motivation", "evasion"],
        ["localisation_quantique", "assassin", "carnage", "evasion", "inspiration"],
        ["localisation_quantique", "assassin", "carnage", "evasion", "duperie"],
        ["localisation_quantique", "assassin", "carnage", "assaut_brutal", "retenue"],
        ["localisation_quantique", "assassin", "carnage", "assaut_brutal", "leurre"],
    ]

    loadouts = []
    for deck in deck_templates:
        for pset in passive_sets:
            loadouts.append((deck[:DECK_SLOTS], tuple(pset)))
    return loadouts

# ═══════════════════════════════════════════════════════════════════
#  DISPLAY
# ═══════════════════════════════════════════════════════════════════

def format_action(action, idx):
    lines = []
    sp_name = action.get("spell", "?")
    dmg = action.get("dmg", 0)
    elem = action.get("element", "")
    cost = action.get("cost", "")
    target = action.get("target", "-")

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

    sb = action.get("snap_before", {})
    sc = action.get("snap_after_cost", {})

    if sb and sc:
        lines.append(f"  |     Cout:  AP:{sb.get('ap','?')}->{sc.get('ap','?')}  "
                     f"WP:{sb.get('wp','?')}->{sc.get('wp','?')}")

    pf_consumed = action.get("pf_consumed_amount", 0)
    if pf_consumed > 0:
        sp_pf = action.get("snap_after_pf", {})
        lines.append(f"  |     PF Refund: {pf_consumed}PF -> +{action.get('pf_refund_ap',0)}AP "
                     f"+{action.get('pf_refund_mp',0)}PM +{action.get('pf_refund_wp',0)}WP  "
                     f"AP:{sc.get('ap','?')}->{sp_pf.get('ap','?')}  "
                     f"MP:{sc.get('mp','?')}->{sp_pf.get('mp','?')}")

    for st in action.get("sub_triggers", []):
        lines.append(f"  |     >> {st}")

    if action.get("kill"):
        sf = action.get("snap_final", {})
        sp_sub = action.get("snap_after_sub", action.get("snap_after_pf", sc))
        lines.append(f"  |     >>> KILL! {action.get('kill_rewards', '')}")
        if sp_sub and sf:
            lines.append(f"  |         AP:{sp_sub.get('ap','?')}->{sf.get('ap','?')}  "
                         f"MP:{sp_sub.get('mp','?')}->{sf.get('mp','?')}  "
                         f"WP:{sp_sub.get('wp','?')}->{sf.get('wp','?')}")

    if action.get("letale_refund"):
        lines.append(f"  |     {action['letale_refund']}")

    pf_gen = action.get("pf_gen", "")
    if pf_gen and "no" not in pf_gen and pf_consumed == 0:
        lines.append(f"  |     PF Gen: {pf_gen}")

    if action.get("armor_given"):
        lines.append(f"  |     Armor given: {action['armor_given']}")
    if action.get("armor_broken"):
        lines.append(f"  |     Armor BROKEN (absorbed: {action.get('armor_absorbed', 0)})")
    if action.get("hemo_applied"):
        lines.append(f"  |     Hemo: +{action['hemo_applied']}")
    if action.get("heal"):
        lines.append(f"  |     Heal: +{action['heal']}")
    if action.get("galopade_pm"):
        lines.append(f"  |     {action['galopade_pm']}")
    if action.get("surineur_buff"):
        lines.append(f"  |     {action['surineur_buff']}")

    sf = action.get("snap_final", {})
    if sf and sb:
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
        print(f"  |  Temerite: +{tl.get('temerite',0)*100:.0f}% (cumul)  "
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
    print(f"  WAKFU SRAM OPTIMIZER V{VERSION} -- Full Mechanics Engine")
    print(f"  Sram \"L'Immortel\" -- Niveau {LVL} -- Patch 1.91")
    print(f"  Sublimations: Rupture PA (Niv.4, +2PA, 2 act/tour), Rupture Violente (Niv.4, 40%, 2 act/tour)")
    print(f"  Temerite (+12%/break, cap 30%), Influence Lente (+2%CC/tour, cap 30)")
    print(f"  Relique: Ivory Dofus (+358 mast 1er coup/tour, +15% crit dmg >=4AP/>=1WP)")
    print(f"  V4.7: Real dmg values, Carnage fix, Assaut Brutal fix, Assassinat -100res,")
    print(f"         Galopade +3PM, Double simplifie, Sacapatate 0%/90%, Obstacles, Invuln boss")
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

    # Aggregate by combat
    loadout_stats = defaultdict(lambda: defaultdict(list))
    for r in results:
        key = (tuple(r["deck"]), tuple(r["passives"]))
        loadout_stats[r["combat"]][key].append(r)

    # Also aggregate globally (avg across ALL combats for each loadout)
    global_loadout_avg = defaultdict(list)
    for r in results:
        key = (tuple(r["deck"]), tuple(r["passives"]))
        global_loadout_avg[key].append(r["total_dmg"])

    print(f"\n{sep}")
    print(f"  RESULTATS PAR COMBAT")
    print(f"{sep}")

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
            spells = [a.get("spell", "?") for a in tl["actions"]
                     if a.get("dmg", 0) > 0 or a.get("spell","").startswith("[")]
            tmrt = f" Tem:+{tl.get('temerite',0)*100:.0f}%" if tl.get('temerite',0) > 0 else ""
            rpa = f" RupPA:{tl.get('rupture_pa',0)}" if tl.get('rupture_pa',0) > 0 else ""
            print(f"    T{tl['turn']}: {tl['turn_dmg']:>6,} dmg  HP:{tl['sram_hp']}  PF:{tl['pf']:>3}  "
                  f"WP:{tl.get('wp_remaining','?')}{tmrt}{rpa}  [{' > '.join(spells[:8])}]")

    # V4.7: Global best = best average DPT across ALL combats
    print(f"\n{sep}")
    print(f"  MEILLEUR BUILD GLOBAL (moyenne tous combats confondus)")
    print(f"{sep}")

    global_rankings = []
    for key, dmg_list in global_loadout_avg.items():
        avg = sum(dmg_list) / len(dmg_list)
        global_rankings.append((avg, key))
    global_rankings.sort(key=lambda x: -x[0])

    for i, (avg, key) in enumerate(global_rankings[:5], 1):
        deck, passives = key
        n_elem = sum(1 for s in deck if SPELLS.get(s, {}).get("element", "neutral") != "neutral")
        print(f"\n  #{i}  DPT moyen global: {avg:>10,.0f}")
        print(f"      Passifs: {', '.join(passives)}")
        print(f"      Deck ({len(deck)}): {n_elem} elem + {len(deck)-n_elem} neutres")
        print(f"      Sorts: {', '.join(deck)}")

        # Per-combat breakdown
        for combat in combats:
            runs = loadout_stats[combat].get(key, [])
            if runs:
                cavg = sum(r["total_dmg"] for r in runs) / len(runs)
                print(f"        {combat:20s}: {cavg:>10,.0f} DPT moy")

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
    wasted_perfide_count = 0

    for r in top_pct:
        for p in r["passives"]:
            passive_freq[p] += 1
        for tl in r["turn_logs"]:
            if tl.get("rupture_pa", 0) > 0:
                perfide_rupture_count += tl["rupture_pa"]
            perfide_cast = False
            armor_broken_turn = False
            prev = None
            for a in tl["actions"]:
                sp = a.get("spell_key") or a.get("spell", "")
                dmg_val = a.get("dmg", 0)
                el = a.get("element", "")
                if sp == "attaque_perfide" and dmg_val > 0:
                    perfide_cast = True
                if a.get("armor_broken", False):
                    armor_broken_turn = True
                if dmg_val > 0:
                    spell_freq[a.get("spell", sp)] += 1
                    if el:
                        elem_dmg[el] += dmg_val
                if prev and dmg_val > 0:
                    combo_freq[f"{prev} > {a.get('spell', sp)}"] += 1
                if dmg_val > 0 or sp.startswith("["):
                    prev = a.get("spell", sp)
            if perfide_cast and not armor_broken_turn:
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
        print(f"\n  #{i}  DPT: {r['total_dmg']:>10,}  Kills:{r['kills']}  Combat:{r['combat']}  "
              f"{'OK' if r['survived'] else 'MORT'}")
        print(f"      Deck: {', '.join(r['deck'][:6])}...")
        print(f"      Passifs: {', '.join(r['passives'])}")
        for tl in r["turn_logs"]:
            spells = [a.get("spell", "?") for a in tl["actions"]
                     if a.get("dmg", 0) > 0 or a.get("spell","").startswith("[")]
            print(f"      T{tl['turn']}: {tl['turn_dmg']:>6,}  AP:{tl['ap_remaining']} WP:{tl.get('wp_remaining','?')} PF:{tl['pf']}  "
                  f"Rup:{tl.get('rupture_pa',0)} Tem:{tl.get('temerite',0)*100:.0f}%  "
                  f"[{' > '.join(spells[:8])}]")

    print(f"\n{sep}")
    print(f"  Termine en {time.time()-t0:.1f}s")
    print(f"{sep}\n")

if __name__ == "__main__":
    main()
