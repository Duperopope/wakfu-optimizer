"""
engine/fighter.py - Representation d'un combattant en combat
Version 5.0

Un Fighter est cree a partir d'un profil (joueur) ou d'un template (monstre).
Il gere ses ressources (PA/PM/PW/PF/PV), ses etats, sa position sur la grille,
son orientation, et son armure.

Sources:
  - DESIGN_DOC.md sections 1.4, 4, 6, 7
  - MethodWakfu: https://methodwakfu.com/bien-debuter/informations-generales/
  - WakfuCalc: https://sites.google.com/view/wakfucalc/en/guides/formulas
"""

import sys, os, copy
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import config
from utils.logger import setup_logger
from engine.damage import profile_to_stats, compute_hp

logger = setup_logger(__name__)


# ============================================================
# DIRECTIONS ET ORIENTATION
# ============================================================

DIRECTIONS = {
    "N": (0, -1),
    "S": (0, 1),
    "E": (1, 0),
    "W": (-1, 0),
}

OPPOSITE = {"N": "S", "S": "N", "E": "W", "W": "E"}

def get_relative_position(attacker_x, attacker_y, target_x, target_y, target_facing):
    """Determine si l'attaquant est devant, sur le cote ou dans le dos de la cible.
    Retourne: "FRONT", "SIDE" ou "REAR"

    La cible regarde dans la direction 'target_facing' (N/S/E/W).
    On calcule le vecteur attaquant->cible et on compare avec la direction
    ou regarde la cible.

    Source: DESIGN_DOC.md section 1.4
    """
    dx = attacker_x - target_x
    dy = attacker_y - target_y

    if dx == 0 and dy == 0:
        return "FRONT"

    face_dx, face_dy = DIRECTIONS[target_facing]

    dot = dx * face_dx + dy * face_dy

    if abs(dx) + abs(dy) == 0:
        return "FRONT"

    cross = abs(dx * face_dy - dy * face_dx)
    parallel = abs(dot)

    if parallel >= cross:
        if dot > 0:
            return "FRONT"
        else:
            return "REAR"
    else:
        return "SIDE"


# ============================================================
# ETATS (BUFFS / DEBUFFS)
# ============================================================

class StateManager:
    """Gere les etats (buffs/debuffs) d'un combattant.
    Chaque etat a un nom, un niveau, une duree restante, et des metadonnees.

    Regles:
      - Incurable/Friable: ne s'empilent PAS, remplacent si superieur
      - La plupart des etats decrementent de 1 a la fin du tour du porteur
      - Certains etats ont des effets speciaux (Hemorrhagie = +1% degats/niveau)
    Source: MethodWakfu section 2.5, DESIGN_DOC.md section 7
    """

    def __init__(self):
        self.states = {}

    def add_state(self, name, level=1, duration=1, source="unknown", replace_if_higher=False):
        """Ajoute ou met a jour un etat.
        replace_if_higher: pour Incurable/Friable, ne remplace que si nouveau > existant
        """
        if name in self.states and replace_if_higher:
            if level <= self.states[name]["level"]:
                logger.debug(f"  Etat {name}: niveau {level} <= existant {self.states[name]['level']}, ignore")
                return False

        self.states[name] = {
            "level": level,
            "duration": duration,
            "source": source,
        }
        logger.debug(f"  Etat {name}: niveau {level}, duree {duration} tours (source: {source})")
        return True

    def remove_state(self, name):
        """Retire un etat."""
        if name in self.states:
            del self.states[name]
            return True
        return False

    def has_state(self, name):
        """Verifie si un etat est present."""
        return name in self.states

    def get_level(self, name):
        """Retourne le niveau d'un etat (0 si absent)."""
        if name in self.states:
            return self.states[name]["level"]
        return 0

    def get_duration(self, name):
        """Retourne la duree restante d'un etat (0 si absent)."""
        if name in self.states:
            return self.states[name]["duration"]
        return 0

    def tick_end_of_turn(self):
        """Decremente la duree de tous les etats de 1.
        Retire ceux qui tombent a 0.
        Appele en fin de tour du porteur.
        """
        expired = []
        for name, state in self.states.items():
            state["duration"] -= 1
            if state["duration"] <= 0:
                expired.append(name)

        for name in expired:
            del self.states[name]
            logger.debug(f"  Etat {name} expire")

        return expired

    def list_states(self):
        """Retourne la liste des etats actifs avec leurs details."""
        return {name: copy.copy(info) for name, info in self.states.items()}

    def clear(self):
        """Retire tous les etats."""
        self.states.clear()


# ============================================================
# COMBATTANT
# ============================================================

class Fighter:
    """Represente un combattant en combat (joueur, monstre ou invocation).

    Attributs principaux:
      - Identite: name, team, fighter_type, class_name, level
      - Position: x, y, facing
      - Ressources: ap, mp, wp, hp, max_hp, armor
      - Sram: weak_point (PF), hemorrhage gere via StateManager
      - Combat: stats (dict structure), etats (StateManager)
      - Limites: uses_per_turn et uses_per_target par sort
    """

    _next_id = 0

    def __init__(self, name, team, fighter_type="player", level=1,
                 class_name="unknown", profile=None, monster_template=None):
        """
        Args:
            name: nom affiche du combattant
            team: "A" ou "B" (equipe)
            fighter_type: "player", "monster", "summon"
            level: niveau du combattant
            class_name: nom de la classe (sram, iop, etc.)
            profile: dict profil joueur (format plat de data/profiles/*.py)
            monster_template: dict template monstre (futur: data/monsters/*.json)
        """
        Fighter._next_id += 1
        self.id = Fighter._next_id
        self.name = name
        self.team = team
        self.fighter_type = fighter_type
        self.class_name = class_name.lower()
        self.level = level
        self.is_alive = True
        self.is_ko = False

        self.x = 0
        self.y = 0
        self.facing = "S"

        self.states = StateManager()

        self._spell_uses_this_turn = {}
        self._spell_uses_this_turn_per_target = {}

        if profile:
            self._init_from_profile(profile)
        elif monster_template:
            self._init_from_monster(monster_template)
        else:
            self._init_default(level)

        self.base_ap = self.ap
        self.base_mp = self.mp
        self.base_wp = self.wp

        self.initiative = self.stats.get("initiative", 0)

        self.weak_point = 0

        self.heal_resistance = 0.0

        self.will_bonus = 0

        logger.info(
            f"Fighter cree: {self.name} (ID:{self.id}) | {self.team} | "
            f"{self.fighter_type} | {self.class_name} L{self.level} | "
            f"PV:{self.hp}/{self.max_hp} PA:{self.ap} PM:{self.mp} PW:{self.wp}"
        )

    def _init_from_profile(self, profile):
        """Initialise depuis un profil joueur plat."""
        self.level = profile.get("level", self.level)
        self.class_name = profile.get("class", self.class_name).lower()

        self.stats = profile_to_stats(profile)

        self.ap = profile.get("ap", 6)
        self.mp = profile.get("mp", 3)
        self.wp = profile.get("wp", 6)

        self.max_hp = profile.get("hp", compute_hp(self.level))
        self.hp = self.max_hp
        self.armor = 0

    def _init_from_monster(self, template):
        """Initialise depuis un template monstre."""
        self.level = template.get("level", self.level)
        self.class_name = template.get("class", "monster").lower()

        self.stats = {
            "masteries": template.get("masteries", {
                "fire": 0, "water": 0, "earth": 0, "air": 0,
                "melee": 0, "distance": 0, "rear": 0,
                "critical": 0, "berserk": 0, "healing": 0,
                "area": 0, "single_target": 0,
            }),
            "hp": template.get("hp", 1000),
            "ap": template.get("ap", 6),
            "mp": template.get("mp", 3),
            "wp": template.get("wp", 0),
            "critical_hit": template.get("critical_hit", 0),
            "block": template.get("block", 0),
            "dodge": template.get("dodge", 0),
            "lock": template.get("lock", 0),
            "initiative": template.get("initiative", 100),
            "force_of_will": template.get("force_of_will", 0),
            "damage_inflicted": template.get("damage_inflicted", 0),
            "res_fire": template.get("res_fire", 0),
            "res_water": template.get("res_water", 0),
            "res_earth": template.get("res_earth", 0),
            "res_air": template.get("res_air", 0),
        }

        self.ap = template.get("ap", 6)
        self.mp = template.get("mp", 3)
        self.wp = template.get("wp", 0)

        self.max_hp = template.get("hp", 1000)
        self.hp = self.max_hp
        self.armor = 0

    def _init_default(self, level):
        """Initialise avec des valeurs par defaut."""
        self.stats = profile_to_stats({
            "level": level, "hp": compute_hp(level),
            "ap": 6, "mp": 3, "wp": 6,
        })
        self.ap = 6
        self.mp = 3
        self.wp = 6
        self.max_hp = compute_hp(level)
        self.hp = self.max_hp
        self.armor = 0

    # --------------------------------------------------------
    # POSITION ET ORIENTATION
    # --------------------------------------------------------

    def place(self, x, y, facing="S"):
        """Place le combattant sur la grille."""
        self.x = x
        self.y = y
        self.facing = facing
        logger.debug(f"  {self.name} place en ({x},{y}) face {facing}")

    def move(self, dx, dy, cost_mp=True):
        """Deplace le combattant de (dx,dy). Coute 1 PM par case si cost_mp."""
        distance = abs(dx) + abs(dy)
        if cost_mp and self.mp < distance:
            logger.warning(f"  {self.name}: pas assez de PM ({self.mp} < {distance})")
            return False
        self.x += dx
        self.y += dy
        if cost_mp:
            self.mp -= distance
        logger.debug(f"  {self.name} deplace en ({self.x},{self.y}) | PM restants: {self.mp}")
        return True

    def turn_to_face(self, target_x, target_y):
        """Tourne le combattant pour faire face a une position cible."""
        dx = target_x - self.x
        dy = target_y - self.y
        if abs(dx) >= abs(dy):
            self.facing = "E" if dx > 0 else "W"
        else:
            self.facing = "S" if dy > 0 else "N"

    def distance_to(self, other):
        """Distance de Manhattan a un autre combattant."""
        return abs(self.x - other.x) + abs(self.y - other.y)

    def is_adjacent(self, other):
        """Verifie si un autre combattant est adjacent (distance 1)."""
        return self.distance_to(other) == 1

    def get_orientation_from(self, attacker):
        """Retourne l'orientation de l'attaquant par rapport a ce combattant.
        Retourne: "FRONT", "SIDE" ou "REAR"
        """
        return get_relative_position(
            attacker.x, attacker.y,
            self.x, self.y,
            self.facing
        )

    # --------------------------------------------------------
    # RESSOURCES
    # --------------------------------------------------------

    def spend_ap(self, amount):
        """Depense des PA. Retourne True si suffisant."""
        if self.ap >= amount:
            self.ap -= amount
            return True
        logger.warning(f"  {self.name}: PA insuffisants ({self.ap} < {amount})")
        return False

    def spend_mp(self, amount):
        """Depense des PM. Retourne True si suffisant."""
        if self.mp >= amount:
            self.mp -= amount
            return True
        logger.warning(f"  {self.name}: PM insuffisants ({self.mp} < {amount})")
        return False

    def spend_wp(self, amount):
        """Depense des PW. Retourne True si suffisant."""
        if self.wp >= amount:
            self.wp -= amount
            return True
        logger.warning(f"  {self.name}: PW insuffisants ({self.wp} < {amount})")
        return False

    def gain_ap(self, amount):
        """Gagne des PA (pas de cap en combat)."""
        self.ap += amount

    def gain_mp(self, amount):
        """Gagne des PM (pas de cap en combat)."""
        self.mp += amount

    def gain_wp(self, amount):
        """Gagne des PW (cap 20)."""
        self.wp = min(self.wp + amount, config.MAX_WP_BASE)

    def start_of_turn(self):
        """Debut de tour: restaure PA/PM de base, reset des compteurs."""
        self.ap = self.base_ap
        self.mp = self.base_mp
        self._spell_uses_this_turn.clear()
        self._spell_uses_this_turn_per_target.clear()
        self.will_bonus = 0
        logger.info(f"--- Tour de {self.name}: PA:{self.ap} PM:{self.mp} PW:{self.wp} PV:{self.hp}/{self.max_hp} Armure:{self.armor}")

    def end_of_turn(self):
        """Fin de tour: decremente les etats, reset volonte bonus."""
        expired = self.states.tick_end_of_turn()
        self.will_bonus = 0
        if expired:
            logger.debug(f"  {self.name}: etats expires: {expired}")

    # --------------------------------------------------------
    # DEGATS ET SOIN
    # --------------------------------------------------------

    def take_damage(self, amount):
        """Recoit des degats. L'armure absorbe en premier.
        Retourne le dict {armor_absorbed, hp_lost, overkill, killed}
        """
        armor_absorbed = min(self.armor, amount)
        self.armor -= armor_absorbed
        remaining = amount - armor_absorbed

        hp_lost = min(self.hp, remaining)
        self.hp -= hp_lost
        overkill = remaining - hp_lost

        killed = False
        if self.hp <= 0:
            self.hp = 0
            self.is_alive = False
            self.is_ko = True
            killed = True

        result = {
            "armor_absorbed": round(armor_absorbed, 1),
            "hp_lost": round(hp_lost, 1),
            "overkill": round(overkill, 1),
            "killed": killed,
            "hp_remaining": self.hp,
            "armor_remaining": round(self.armor, 1),
        }

        logger.info(
            f"  {self.name} recoit {amount:.0f} degats: "
            f"armure -{armor_absorbed:.0f} | PV -{hp_lost:.0f} | "
            f"restant PV:{self.hp:.0f} armure:{self.armor:.0f}"
            + (" | K.O.!" if killed else "")
        )

        return result

    def heal(self, amount):
        """Recoit des soins. Ne depasse pas max_hp.
        Met a jour la resistance soin.
        Retourne le dict {actual_heal, hp_after, heal_resistance_after}
        """
        actual = min(amount, self.max_hp - self.hp)
        self.hp += actual

        if self.max_hp > 0:
            self.heal_resistance += (actual / self.max_hp) * 20

        return {
            "actual_heal": round(actual, 1),
            "hp_after": round(self.hp, 1),
            "heal_resistance_after": round(self.heal_resistance, 2),
        }

    def gain_armor(self, amount, cap_hp=True):
        """Gagne de l'armure. Cap a 50% PV max (joueur) ou 100% (invocation).
        Les monstres ennemis n'ont pas de cap.
        Source: MethodWakfu section 2.3
        """
        self.armor += amount
        if cap_hp and self.max_hp > 0:
            if self.fighter_type == "summon":
                cap = self.max_hp * config.ARMOR_CAP_SUMMON
            elif self.fighter_type == "player":
                cap = self.max_hp * config.ARMOR_CAP_PLAYER
            else:
                return self.armor
            self.armor = min(self.armor, cap)
        return round(self.armor, 1)

    # --------------------------------------------------------
    # SRAM: POINT FAIBLE (PF)
    # --------------------------------------------------------

    def add_weak_point(self, amount):
        """Ajoute des Points Faibles (Sram). Cap 100.
        Chaque tranche de 25 PF consommee donne +1 AP, +1 MP, +1 WP, +10 Hemorrhagie.
        Source: Patch 1.91
        """
        self.weak_point += amount
        refunds = 0
        while self.weak_point >= 25:
            self.weak_point -= 25
            refunds += 1
            self.gain_ap(1)
            self.gain_mp(1)
            self.gain_wp(1)
            hemorrhage_level = self.states.get_level("hemorrhagie") + 10
            hemorrhage_level = min(hemorrhage_level, 40)
            self.states.add_state("hemorrhagie", level=hemorrhage_level, duration=2, source="weak_point_refund")
            logger.info(f"  {self.name}: PF refund! +1AP +1MP +1WP +10 Hemorrhagie (niv {hemorrhage_level})")

        self.weak_point = min(self.weak_point, 100)
        return refunds

    def consume_weak_point(self):
        """Consomme tous les PF et retourne la valeur consommee.
        Utilise par Mise a Mort, Traumatisme, Arnaque, Effroi.
        """
        consumed = self.weak_point
        self.weak_point = 0
        return consumed

    # --------------------------------------------------------
    # GESTION DES SORTS (limites par tour/cible)
    # --------------------------------------------------------

    def can_use_spell(self, spell_name, target_id=None, spell_data=None):
        """Verifie si un sort peut etre utilise (limites par tour et par cible).
        Retourne (bool, raison) : True si OK, False avec la raison sinon.
        """
        if spell_data is None:
            return True, "ok"

        uses_this_turn = self._spell_uses_this_turn.get(spell_name, 0)
        max_per_turn = spell_data.get("uses_per_turn", 99)
        if uses_this_turn >= max_per_turn:
            return False, f"max {max_per_turn} utilisations/tour atteint"

        if target_id is not None:
            key = f"{spell_name}_{target_id}"
            uses_on_target = self._spell_uses_this_turn_per_target.get(key, 0)
            max_per_target = spell_data.get("uses_per_target", 99)
            if uses_on_target >= max_per_target:
                return False, f"max {max_per_target} utilisations/cible atteint"

        ap_cost = spell_data.get("ap_cost", 0)
        wp_cost = spell_data.get("wp_cost", 0)
        if self.ap < ap_cost:
            return False, f"PA insuffisants ({self.ap} < {ap_cost})"
        if self.wp < wp_cost:
            return False, f"PW insuffisants ({self.wp} < {wp_cost})"

        cooldown_key = f"cooldown_{spell_name}"
        if self.states.has_state(cooldown_key):
            remaining = self.states.get_duration(cooldown_key)
            return False, f"cooldown {remaining} tour(s) restant(s)"

        return True, "ok"

    def register_spell_use(self, spell_name, target_id=None, spell_data=None):
        """Enregistre l'utilisation d'un sort (compteurs par tour/cible)."""
        self._spell_uses_this_turn[spell_name] = self._spell_uses_this_turn.get(spell_name, 0) + 1

        if target_id is not None:
            key = f"{spell_name}_{target_id}"
            self._spell_uses_this_turn_per_target[key] = self._spell_uses_this_turn_per_target.get(key, 0) + 1

        if spell_data and spell_data.get("cooldown", 0) > 0:
            cooldown_key = f"cooldown_{spell_name}"
            self.states.add_state(cooldown_key, level=1, duration=spell_data["cooldown"], source="spell_cooldown")

    # --------------------------------------------------------
    # UTILITAIRES
    # --------------------------------------------------------

    def get_effective_will(self):
        """Retourne la Volonte effective (base + bonus des retraits subis)."""
        base_will = self.stats.get("force_of_will", 0)
        return base_will + self.will_bonus

    def is_berserk(self):
        """Verifie si le combattant est en mode berserk (<= 50% PV max)."""
        if self.max_hp <= 0:
            return False
        return (self.hp / self.max_hp) <= 0.5

    def is_isolated(self, all_fighters):
        """Verifie si le combattant est isole (aucun allie adjacent).
        Pour le Sram, adjacent au Double compte comme 'pas isole' pour l'ennemi.
        Source: Patch 1.91 - +50% degats sur cible isolee OU adjacente au Double
        """
        for f in all_fighters:
            if f.id == self.id:
                continue
            if f.team == self.team and f.is_alive and self.is_adjacent(f):
                return False
        return True

    def resurrect(self, hp_percent=20):
        """Ressuscite le combattant avec un % de ses PV max."""
        self.is_alive = True
        self.is_ko = False
        self.hp = max(1, round(self.max_hp * hp_percent / 100))
        self.armor = 0
        logger.info(f"  {self.name} ressuscite avec {self.hp} PV")

    def summary(self):
        """Retourne un resume compact du combattant."""
        states_str = ", ".join(
            f"{n}:{s['level']}({s['duration']}t)"
            for n, s in self.states.list_states().items()
            if not n.startswith("cooldown_")
        )
        return (
            f"{self.name} [{self.team}] L{self.level} {self.class_name} | "
            f"PV:{self.hp}/{self.max_hp} Arm:{round(self.armor)} | "
            f"PA:{self.ap} PM:{self.mp} PW:{self.wp} PF:{self.weak_point} | "
            f"Pos:({self.x},{self.y}) Face:{self.facing} | "
            f"Etats: [{states_str or 'aucun'}]"
        )

    def __repr__(self):
        return f"<Fighter {self.name} ID:{self.id} {self.team} {'ALIVE' if self.is_alive else 'KO'}>"


# ============================================================
# TESTS
# ============================================================

if __name__ == "__main__":
    from data.profiles.limmortel import PROFILE

    print("=" * 60)
    print("  TESTS ENGINE/FIGHTER.PY V5.0")
    print("=" * 60)

    # --- Test 1: Creation depuis profil ---
    sram = Fighter("L'Immortel", team="A", profile=PROFILE)
    print(f"\nTest 1 - Creation:")
    print(f"  {sram.summary()}")

    # --- Test 2: Placement et orientation ---
    sram.place(5, 5, "N")

    dummy = Fighter("Sacapatate", team="B", fighter_type="monster", level=179,
                     monster_template={
                         "hp": 5000, "ap": 6, "mp": 3, "initiative": 50,
                         "res_fire": 200, "res_water": 200,
                         "lock": 100, "dodge": 50,
                         "masteries": {"fire": 500, "water": 500, "melee": 300},
                     })
    dummy.place(5, 4, "S")

    orientation = dummy.get_orientation_from(sram)
    print(f"\nTest 2 - Orientation:")
    print(f"  Sram en (5,5) face N, Sacapatate en (5,4) face S")
    print(f"  Sram attaque Sacapatate: {orientation}")
    print(f"  Distance: {sram.distance_to(dummy)} | Adjacent: {sram.is_adjacent(dummy)}")

    # --- Test 3: Degats et armure ---
    dummy.gain_armor(1000)
    print(f"\nTest 3 - Degats avec armure:")
    print(f"  Armure: {dummy.armor}")
    result = dummy.take_damage(1500)
    print(f"  Apres 1500 degats: {result}")
    print(f"  {dummy.summary()}")

    # --- Test 4: Soin ---
    heal_result = dummy.heal(800)
    print(f"\nTest 4 - Soin:")
    print(f"  Soin 800: {heal_result}")

    # --- Test 5: Point Faible (Sram) ---
    print(f"\nTest 5 - Point Faible:")
    sram.add_weak_point(60)
    print(f"  +60 PF: PF restant={sram.weak_point}, PA={sram.ap}, PM={sram.mp}, PW={sram.wp}")
    print(f"  Hemorrhagie: niv {sram.states.get_level('hemorrhagie')}")

    # --- Test 6: Etats ---
    print(f"\nTest 6 - Etats:")
    sram.states.add_state("invisible", level=1, duration=2, source="sort_invisibilite")
    sram.states.add_state("apparent", level=1, duration=3, source="sort_invisibilite")
    sram.states.add_state("maitre_des_ombres", level=1, duration=1, source="sort_invisibilite")
    print(f"  {sram.summary()}")
    sram.end_of_turn()
    print(f"  Apres fin de tour:")
    print(f"  {sram.summary()}")

    # --- Test 7: Gestion des sorts ---
    print(f"\nTest 7 - Limites de sorts:")
    spell = {"ap_cost": 2, "wp_cost": 0, "uses_per_turn": 3, "uses_per_target": 2}
    for i in range(4):
        can, reason = sram.can_use_spell("premier_sang", target_id=dummy.id, spell_data=spell)
        if can:
            sram.register_spell_use("premier_sang", target_id=dummy.id, spell_data=spell)
            print(f"  Utilisation {i+1}: OK")
        else:
            print(f"  Utilisation {i+1}: REFUSE - {reason}")

    # --- Test 8: Kill ---
    print(f"\nTest 8 - Kill:")
    dummy.take_damage(99999)
    print(f"  {dummy}")
    print(f"  is_alive: {dummy.is_alive} | is_ko: {dummy.is_ko}")
    dummy.resurrect(hp_percent=20)
    print(f"  Apres rez: {dummy.summary()}")

    print(f"\n{'=' * 60}")
    print("  TOUS LES TESTS TERMINES")
    print(f"{'=' * 60}")
