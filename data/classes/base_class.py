"""
DATA / CLASSES / BASE_CLASS.PY
Classe abstraite dont heritent toutes les classes du jeu.
Definit la structure commune: sorts, passifs, mecaniques innees.
Chaque classe (sram.py, iop.py, cra.py...) herite de cette base.
"""


class BaseClass:
    """Structure commune a toutes les classes Wakfu."""

    name = "Unknown"
    elements = []  # ex: ["fire", "water", "air"]

    # Sorts elementaires: dict de listes par element
    # Chaque sort est un dict avec: name, ap_cost, wp_cost, min_range, max_range,
    # is_melee, is_area, element, base_damage, base_damage_crit,
    # effects, uses_per_turn, uses_per_target, conditions, etc.
    spells = {}

    # Sorts neutres (support, mobilite, utilitaire)
    neutral_spells = {}

    # Passifs: dict avec name, description, effects
    passives = {}

    # Mecaniques innees (propres a la classe)
    innate_mechanics = {}

    @classmethod
    def get_spell(cls, spell_name):
        for element_spells in cls.spells.values():
            for spell in element_spells:
                if spell["name"] == spell_name:
                    return spell
        for spell in cls.neutral_spells.values():
            if isinstance(spell, dict) and spell.get("name") == spell_name:
                return spell
            elif isinstance(spell, list):
                for s in spell:
                    if s["name"] == spell_name:
                        return s
        return None

    @classmethod
    def get_passive(cls, passive_name):
        return cls.passives.get(passive_name, None)

    @classmethod
    def get_all_spells_flat(cls):
        result = []
        for element_spells in cls.spells.values():
            result.extend(element_spells)
        if isinstance(cls.neutral_spells, list):
            result.extend(cls.neutral_spells)
        elif isinstance(cls.neutral_spells, dict):
            for v in cls.neutral_spells.values():
                if isinstance(v, list):
                    result.extend(v)
                elif isinstance(v, dict):
                    result.append(v)
        return result

    @classmethod
    def list_spell_names(cls):
        return [s["name"] for s in cls.get_all_spells_flat()]

    @classmethod
    def list_passive_names(cls):
        return list(cls.passives.keys())
