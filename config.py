"""
WAKFU THEORYCRAFTER V5.0
Configuration globale du projet - AGNOSTIQUE DE LA CLASSE.
Les donnees specifiques a chaque classe sont dans data/classes/
Les profils joueur sont dans data/profiles/

Sources:
- Patch notes 1.91: https://www.wakfu.com/en/mmorpg/news/patch-notes/1767730-update-1-91/details
- Formules: https://methodwakfu.com/bien-debuter/informations-generales/
- Wiki: https://wakfu.wiki.gg/wiki/Sram
"""

VERSION = "5.0.0"
PROJECT_NAME = "Wakfu TheoryCrafter"

# === CONSTANTES UNIVERSELLES DU JEU ===

# Orientation (s'applique a TOUTES les classes)
ORIENTATION_FRONT = 1.0
ORIENTATION_SIDE = 1.1
ORIENTATION_REAR = 1.25

# Resistance: formule 1 - 0.8^(flat/100)
RESISTANCE_CAP = 90
RESISTANCE_REDUCTION_CAP = -200

# DI% plancher
DI_FLOOR = -50

# Critique
CRITICAL_MULTIPLIER = 1.25

# Limites hors combat
MAX_AP_BASE = 16
MAX_MP_BASE = 8
MAX_WP_BASE = 20
MAX_CC = 100

# Armure
ARMOR_CAP_PLAYER = 0.50       # 50% PV max
ARMOR_CAP_SUMMON = 1.00       # 100% PV max pour invocations
ARMOR_CAP_MONSTER = None       # pas de cap pour les monstres

# Bloc
BLOCK_REDUCTION_DEFAULT = 0.80
BLOCK_REDUCTION_EXPERT = 0.68

# === SIMULATION ===
MAX_TURNS = 8
SIMULATION_RUNS_PER_LOADOUT = 100
PARALLEL_PROCESSES = 15

# === PALIERS DE NIVEAU ===
LEVEL_BRACKETS = list(range(20, 246, 15))

# === CHEMINS ===
import os
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output")
RESULTS_DIR = os.path.join(OUTPUT_DIR, "results")
REPORTS_DIR = os.path.join(OUTPUT_DIR, "reports")
LOGS_DIR = os.path.join(PROJECT_ROOT, "logs")
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
CLASSES_DIR = os.path.join(DATA_DIR, "classes")
PROFILES_DIR = os.path.join(DATA_DIR, "profiles")
MONSTERS_DIR = os.path.join(DATA_DIR, "monsters")

# Dict de raccourci pour engine/damage.py
ORIENTATION_MULTIPLIERS = {
    "FRONT": ORIENTATION_FRONT,
    "SIDE": ORIENTATION_SIDE,
    "REAR": ORIENTATION_REAR,
}
