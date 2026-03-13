"""
DATA / CLASSES / COMMON.PY
Passifs et sorts communs a TOUTES les classes de Wakfu.
Chaque classe herite automatiquement de ces elements.

Valeurs verifiees manuellement en jeu par Sam (patch 1.91).
"""


# ================================================================
# PASSIFS COMMUNS (disponibles pour toutes les classes)
# ================================================================
COMMON_PASSIVES = {
    "evasion": {
        "display_name": "Evasion",
        "unlock_level": 20,
        "effects": [
            {"type": "dodge_bonus", "value": "100% du niveau"},
            {"type": "dodge_bonus_on_dodge", "value": "35% du niveau", "duration": 3,
             "condition": "Apres avoir esquive (avec pertes)"},
        ],
        "description": "Pour s'echapper un moment, ou meme durablement, ce passif est ideal !",
    },
    "interception": {
        "display_name": "Interception",
        "unlock_level": 20,
        "effects": [
            {"type": "lock_bonus", "value": "100% du niveau"},
            {"type": "lock_bonus_on_lock", "value": "35% du niveau", "duration": 3,
             "condition": "Apres avoir tacle une cible"},
        ],
        "description": "Hopla ! Ou croyez-vous aller ? Restez donc ici !",
    },
    "inspiration": {
        "display_name": "Inspiration",
        "unlock_level": 25,
        "effects": [
            {"type": "initiative_bonus", "value": "50% du niveau"},
            {"type": "di_bonus", "value": 10, "condition": "cible avec initiative superieure"},
        ],
        "description": "Une bonne respiration, une boisson fraiche et on entame le combat !",
    },
    "motivation": {
        "display_name": "Motivation",
        "unlock_level": 35,
        "effects": [
            {"type": "ap_bonus", "value": 1},
            {"type": "di_penalty", "value": -20},
            {"type": "force_of_will_bonus", "value": 10},
        ],
        "description": "En etant motive, on peut rapidement prendre le pas sur ses adversaires.",
    },
    "medecine": {
        "display_name": "Medecine",
        "unlock_level": 55,
        "effects": [
            {"type": "heals_performed_bonus", "value": 30},
            {"type": "armor_given_bonus", "value": 25},
            {"type": "di_penalty", "value": -15},
        ],
        "description": "Besoin d'un soigneur dans votre equipe ? Je suis la !",
    },
    "rock": {
        "display_name": "Rock",
        "unlock_level": 65,
        "effects": [
            {"type": "hp_percent_bonus", "value": 60},
            {"type": "heals_received_bonus", "value": 25},
            {"type": "di_penalty", "value": -25},
            {"type": "heals_performed_penalty", "value": -50},
        ],
        "description": "Plus solide que la montagne, je prendrai les degats pour vous !",
    },
    "carnage": {
        "display_name": "Carnage",
        "unlock_level": 75,
        "effects": [
            {"type": "di_bonus", "value": 15},
            {"type": "di_bonus_on_armor", "value": 10, "condition": "cible ayant de l'Armure"},
            {"type": "heals_performed_penalty", "value": -30},
        ],
        "description": "Soif de sang et de pouvoir, je suis la pour faire des degats !",
    },
}


# ================================================================
# SORTS NEUTRES COMMUNS (disponibles pour toutes les classes)
# ================================================================
COMMON_SPELLS = [
    {
        "name": "maitrise_des_armes",
        "display_name": "Maitrise des Armes",
        "element": "neutral",
        "description": "Sort actif commun a toutes les classes",
        "effects": "TODO_VERIFIER_EN_JEU",
        "unlock_level": "TODO",
    },
    {
        "name": "os_a_moelle",
        "display_name": "Os a Moelle",
        "element": "neutral",
        "description": "Sort actif commun a toutes les classes",
        "effects": "TODO_VERIFIER_EN_JEU",
        "unlock_level": "TODO",
    },
    {
        "name": "sort_commun_3",
        "display_name": "TODO_NOM_INCONNU",
        "element": "neutral",
        "description": "3eme sort actif commun (pas encore debloque par Sam)",
        "effects": "TODO_VERIFIER_EN_JEU",
        "unlock_level": "TODO",
    },
]


# ================================================================
# EMPLACEMENTS DE SORTS ET PASSIFS (progression par niveau)
# ================================================================
SPELL_SLOTS = {
    "base": 8,
    "bonus_slots": {30: 1, 40: 1, 60: 1, 80: 1},
    "total_max": 12,
}

PASSIVE_SLOTS = {
    "base_level": 20,
    "slots_by_level": {20: 1, 30: 1, 50: 1, 100: 1, 150: 1, 200: 1},
    "total_max": 6,
}
