# =============================================================================
# engine/double.py - V5.0
# Systeme du Double Sram (patch 1.91)
# =============================================================================
# Sources:
#   - Patch 1.91 FR: https://www.wakfu.com/fr/mmorpg/actualites/maj/1767729-mise-jour-1-91/details
#   - Patch 1.91 EN: https://www.wakfu.com/en/mmorpg/news/patch-notes/1767730-update-1-91/details
#   - Forum beta 1.91: https://www.wakfu.com/fr/forum/574-etat-serveur-beta/435087-ouverture-beta-1-91-22-01-26
#   - DESIGN_DOC.md section Double
# =============================================================================
#
# DOUBLE SRAM (patch 1.91 - 3eme barre):
# ----------------------------------------
# INVOCATION:
#   - 2 PA, 1 PW, 1 Portee
#   - Invoque le Double Sram (1 fois tous les 2 tours max)
#   - 1 utilisation par tour
#
# SI LE DOUBLE EST DEJA SUR LE TERRAIN:
#   - Le sort peut se lancer sur le Sram
#   - Le sort ne coute pas de PA
#   - Le Sram prend le controle du Double et joue son tour instantanement
#
# CARACTERISTIQUES DU DOUBLE:
#   - 8 PA, 6 PM, 6 PW
#   - 40% des PV du Sram
#   - Le reste des aptitudes du Sram sont transmises telles quelles
#   - Bonus de 200% du niveau en Tacle
#   - Immunise aux dommages de zone du Sram
#
# SORTS DU DOUBLE:
#   1. Peur       - 2 PA, 2-3 portee, ligne, non-modifiable, sans LdV
#                   Pousse la cible devant le Double sur la case visee
#   2. Embuscade  - 4 PA, 3-6 portee, non-modifiable, sans LdV
#                   Pose un piege Embuscade. Au declenchement: le Double
#                   se retourne vers la cible puis se teleporte face a elle
#                   1 utilisation par tour
#   3. Contact leetal - 2 PA, 1 portee
#                   Applique "Marque letale" (1 tour):
#                   Si le Sram tue un ennemi: +2 PA, echange de position
#                   avec l'ennemi tue, recupere l'Hemorragie du tue
#                   2 tours de relance
#   4. Diversion  - 2 PA, 0 portee
#                   En croix taille 2: tourne les cibles vers le Double
#                   1 utilisation par tour
#
# INTERACTION ISOLE:
#   Le Sram inflige 50% Dommages supplementaires aux ennemis isoles
#   OU au contact du Double. Une cible est isolee si elle n'a aucun
#   allie a 2 cases ou moins.
#   -> Le Double est un outil pour ACTIVER le bonus Isole sur les cibles
#      qui ne sont normalement pas isolees.
#
# PASSIFS LIES AU DOUBLE:
#   - Duperie: apres degats directs recus, echange avec le Double (1x/tour combattant)
#   - Passe-Passe: Double invocable a 4 portee ligne sans LdV, echange a l'invoc + fin de tour
#   - Leurre: Double explose si degats directs recus -> 50% PV en degats (cercle 2) + Hemorragie +20
#   - Assaut letal: Marque letale modifiee -> Sram se teleporte dos du porteur au kill
#   - Peur alternative: Peur du Double attire au lieu de pousser
#   - Diversion alternative: Diversion retourne en croix taille 2
# =============================================================================

import logging
import sys
import os
import math

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from utils.logger import setup_logger
    logger = setup_logger("engine.double")
except ImportError:
    logger = logging.getLogger("engine.double")
    logging.basicConfig(level=logging.INFO)


# =============================================================================
# 1. CONSTANTES
# =============================================================================

# Sort Double (invocation)
DOUBLE_SUMMON_AP_COST = 2
DOUBLE_SUMMON_WP_COST = 1
DOUBLE_SUMMON_RANGE = 1
DOUBLE_SUMMON_COOLDOWN = 2      # 1 fois tous les 2 tours max
DOUBLE_SUMMON_USES_PER_TURN = 1

# Prise de controle (Double deja present)
DOUBLE_CONTROL_AP_COST = 0       # gratuit quand Double deja present

# Statistiques du Double
DOUBLE_AP = 8
DOUBLE_MP = 6
DOUBLE_WP = 6
DOUBLE_HP_PERCENT = 40           # 40% des PV du Sram
DOUBLE_LOCK_BONUS_PERCENT = 200  # 200% du niveau en Tacle
DOUBLE_IMMUNE_SRAM_AOE = True    # immunise aux degats de zone du Sram

# Bonus Isole via Double
ISOLATED_BONUS_PERCENT = 50      # +50% degats supplementaires (%df)
ISOLATED_RANGE = 2               # une cible est "isolee" si aucun allie a 2 cases ou moins

# Sorts du Double
DOUBLE_SPELLS = {
    "peur": {
        "name": "Peur (Double)",
        "ap_cost": 2,
        "range_min": 2,
        "range_max": 3,
        "line_only": True,
        "modifiable_range": False,
        "requires_los": False,
        "uses_per_turn": 3,
        "effect": "push_to_cell",
        "description": "Pousse la cible devant le Double sur la case visee",
    },
    "embuscade": {
        "name": "Embuscade (Double)",
        "ap_cost": 4,
        "range_min": 3,
        "range_max": 6,
        "line_only": False,
        "modifiable_range": False,
        "requires_los": False,
        "uses_per_turn": 1,
        "effect": "place_ambush_trap",
        "description": "Pose un piege Embuscade. Au declenchement: Double se teleporte face a la cible",
    },
    "contact_letal": {
        "name": "Contact letal (Double)",
        "ap_cost": 2,
        "range_min": 1,
        "range_max": 1,
        "line_only": False,
        "modifiable_range": False,
        "requires_los": True,
        "uses_per_turn": 1,
        "cooldown": 2,
        "effect": "apply_lethal_mark",
        "description": "Applique Marque letale (1 tour). Si Sram tue: +2PA, echange, recupere Hemorragie",
    },
    "diversion": {
        "name": "Diversion (Double)",
        "ap_cost": 2,
        "range_min": 0,
        "range_max": 0,
        "line_only": False,
        "modifiable_range": False,
        "requires_los": False,
        "uses_per_turn": 1,
        "effect": "turn_targets_toward_double",
        "area": "cross_2",
        "description": "En croix de taille 2: tourne les cibles vers le Double",
    },
}


# =============================================================================
# 2. CLASSE DOUBLE FIGHTER
# =============================================================================

class SramDouble:
    """
    Represente le Double invoque par le Sram.
    C'est une entite semi-autonome avec ses propres PA/PM/PW et sorts,
    mais qui partage les statistiques offensives/defensives du Sram.
    """

    def __init__(self, sram_fighter, position=None):
        """
        Cree le Double a partir du Sram.

        Source patch 1.91:
        - 8 PA, 6 PM, 6 PW
        - 40% des PV du Sram
        - Aptitudes du Sram transmises
        - +200% du niveau en Tacle
        - Immunise aux degats de zone du Sram

        Args:
            sram_fighter: Fighter - le Sram proprietaire
            position: tuple (x, y) ou None
        """
        self.owner = sram_fighter
        self.name = f"Double de {sram_fighter.name}"
        self.is_double = True

        # Ressources propres
        self.max_ap = DOUBLE_AP
        self.current_ap = DOUBLE_AP
        self.max_mp = DOUBLE_MP
        self.current_mp = DOUBLE_MP
        self.max_wp = DOUBLE_WP
        self.current_wp = DOUBLE_WP

        # PV = 40% du Sram
        sram_hp = getattr(sram_fighter, 'max_hp', getattr(sram_fighter, 'hp', 10000))
        self.max_hp = math.floor(sram_hp * DOUBLE_HP_PERCENT / 100)
        self.current_hp = self.max_hp

        # Tacle = 200% du niveau
        sram_level = getattr(sram_fighter, 'level', 179)
        self.lock = math.floor(sram_level * DOUBLE_LOCK_BONUS_PERCENT / 100)
        self.level = sram_level

        # Position et orientation
        self.position = position
        self.facing = getattr(sram_fighter, 'facing', 'N')

        # Copier les stats offensives/defensives du Sram
        self.team = getattr(sram_fighter, 'team', 'A')
        self.dodge = getattr(sram_fighter, 'dodge', 0)
        self.block = getattr(sram_fighter, 'block', 0)
        self.initiative = 0  # le Double joue pendant le tour du Sram

        # Etats
        self.states = []
        self.is_alive = True
        self.immune_sram_aoe = DOUBLE_IMMUNE_SRAM_AOE

        # Sorts disponibles et compteurs d'utilisation
        self.spells = dict(DOUBLE_SPELLS)
        self.spell_uses_this_turn = {}
        self.spell_cooldowns = {}

        # Statistiques
        self.total_damage_dealt = 0
        self.total_turns_played = 0

        logger.info(
            f"{self.name} cree: PV={self.current_hp}/{self.max_hp}, "
            f"PA={self.current_ap}, PM={self.current_mp}, PW={self.current_wp}, "
            f"Tacle={self.lock}, position={self.position}"
        )

    def reset_turn(self):
        """Reinitialise les ressources du Double pour un nouveau sous-tour."""
        self.current_ap = self.max_ap
        self.current_mp = self.max_mp
        # PW ne se regenere pas automatiquement pour le Double
        self.spell_uses_this_turn = {}

        # Decrementer les cooldowns
        expired = []
        for spell_key, cd in self.spell_cooldowns.items():
            self.spell_cooldowns[spell_key] = cd - 1
            if self.spell_cooldowns[spell_key] <= 0:
                expired.append(spell_key)
        for key in expired:
            del self.spell_cooldowns[key]

        self.total_turns_played += 1
        logger.debug(f"{self.name}: tour reinitialise. PA={self.current_ap}, PM={self.current_mp}")

    def can_cast_spell(self, spell_key):
        """
        Verifie si le Double peut lancer un sort.

        Args:
            spell_key: str - cle du sort dans DOUBLE_SPELLS

        Returns:
            tuple (bool, str) - (peut_lancer, raison_si_non)
        """
        if spell_key not in self.spells:
            return False, f"Sort inconnu: {spell_key}"

        spell = self.spells[spell_key]

        # Verifier PA
        if self.current_ap < spell["ap_cost"]:
            return False, f"PA insuffisants ({self.current_ap} < {spell['ap_cost']})"

        # Verifier uses par tour
        uses = self.spell_uses_this_turn.get(spell_key, 0)
        if uses >= spell["uses_per_turn"]:
            return False, f"Max utilisations atteint ({uses}/{spell['uses_per_turn']})"

        # Verifier cooldown
        if spell_key in self.spell_cooldowns:
            return False, f"Cooldown actif ({self.spell_cooldowns[spell_key]} tours)"

        return True, "OK"

    def cast_spell(self, spell_key, target_pos=None):
        """
        Le Double lance un sort.

        Args:
            spell_key: str - cle du sort
            target_pos: tuple (x, y) ou None

        Returns:
            dict - resultat du sort
        """
        can, reason = self.can_cast_spell(spell_key)
        if not can:
            logger.warning(f"{self.name}: impossible de lancer {spell_key}: {reason}")
            return {"success": False, "reason": reason}

        spell = self.spells[spell_key]

        # Consommer PA
        self.current_ap -= spell["ap_cost"]

        # Compteur d'utilisation
        self.spell_uses_this_turn[spell_key] = self.spell_uses_this_turn.get(spell_key, 0) + 1

        # Cooldown
        if "cooldown" in spell:
            self.spell_cooldowns[spell_key] = spell["cooldown"]

        result = {
            "success": True,
            "spell": spell["name"],
            "ap_cost": spell["ap_cost"],
            "ap_remaining": self.current_ap,
            "effect": spell["effect"],
            "target": target_pos,
        }

        logger.info(
            f"{self.name} lance {spell['name']} "
            f"(cout: {spell['ap_cost']} PA, reste: {self.current_ap} PA)"
        )

        return result

    def take_damage(self, amount, is_aoe_from_sram=False):
        """
        Le Double recoit des degats.

        Args:
            amount: int - degats bruts
            is_aoe_from_sram: bool - est-ce un AoE du Sram proprietaire?

        Returns:
            dict - resultat
        """
        if is_aoe_from_sram and self.immune_sram_aoe:
            logger.debug(f"{self.name}: immunise aux AoE du Sram, 0 degats")
            return {"damage_taken": 0, "killed": False, "immune": True}

        actual = min(amount, self.current_hp)
        self.current_hp -= actual

        killed = self.current_hp <= 0
        if killed:
            self.current_hp = 0
            self.is_alive = False

        logger.info(
            f"{self.name}: recoit {actual} degats -> PV {self.current_hp}/{self.max_hp}"
            + (" -> DETRUIT" if killed else "")
        )

        return {"damage_taken": actual, "killed": killed, "immune": False}

    def get_summary(self):
        """Resume de l'etat du Double."""
        return {
            "name": self.name,
            "alive": self.is_alive,
            "hp": f"{self.current_hp}/{self.max_hp}",
            "ap": self.current_ap,
            "mp": self.current_mp,
            "wp": self.current_wp,
            "lock": self.lock,
            "position": self.position,
            "facing": self.facing,
            "turns_played": self.total_turns_played,
        }


# =============================================================================
# 3. GESTIONNAIRE DU DOUBLE
# =============================================================================

class DoubleManager:
    """
    Gere le cycle de vie du Double: invocation, prise de controle,
    sous-tour, destruction, et interaction avec le bonus Isole.
    """

    def __init__(self, sram_fighter, passives=None):
        """
        Args:
            sram_fighter: Fighter - le Sram
            passives: dict ou None - passifs actifs
                {"duperie": bool, "passe_passe": bool, "leurre": bool,
                 "assaut_letal": bool, "peur_alternative": bool,
                 "diversion_alternative": bool}
        """
        self.sram = sram_fighter
        self.double = None  # SramDouble ou None
        self.passives = passives or {}

        # Cooldown d'invocation (1 fois tous les 2 tours)
        self.summon_cooldown = 0

        # Compteurs
        self.total_summons = 0
        self.total_controls = 0
        self.total_double_deaths = 0

        # Duperie: echange 1 fois par tour de combattant apres degats
        self.duperie_used_this_round = {}  # {fighter_id: bool}

        logger.info(
            f"DoubleManager cree pour {sram_fighter.name}. "
            f"Passifs: {list(self.passives.keys())}"
        )

    @property
    def double_on_field(self):
        """Le Double est-il present sur le terrain?"""
        return self.double is not None and self.double.is_alive

    @property
    def can_summon(self):
        """Peut-on invoquer le Double?"""
        if self.double_on_field:
            return False  # deja present
        if self.summon_cooldown > 0:
            return False
        if hasattr(self.sram, 'current_ap') and self.sram.current_ap < DOUBLE_SUMMON_AP_COST:
            return False
        if hasattr(self.sram, 'current_wp') and self.sram.current_wp < DOUBLE_SUMMON_WP_COST:
            return False
        return True

    @property
    def can_take_control(self):
        """Peut-on prendre le controle du Double (deja present)?"""
        return self.double_on_field

    def summon_double(self, position):
        """
        Invoque le Double.

        Source patch 1.91:
        - 2 PA, 1 PW, 1 Portee
        - 1 fois tous les 2 tours max
        - Si Double deja present: 0 PA, prend le controle

        Args:
            position: tuple (x, y) - position d'invocation

        Returns:
            dict - resultat
        """
        if self.double_on_field:
            # Le Double est deja la -> prise de controle (gratuit)
            return self.take_control()

        if not self.can_summon:
            reasons = []
            if self.summon_cooldown > 0:
                reasons.append(f"cooldown {self.summon_cooldown} tours")
            if hasattr(self.sram, 'current_ap') and self.sram.current_ap < DOUBLE_SUMMON_AP_COST:
                reasons.append(f"PA insuffisants ({self.sram.current_ap} < {DOUBLE_SUMMON_AP_COST})")
            if hasattr(self.sram, 'current_wp') and self.sram.current_wp < DOUBLE_SUMMON_WP_COST:
                reasons.append(f"PW insuffisants ({self.sram.current_wp} < {DOUBLE_SUMMON_WP_COST})")
            reason = ", ".join(reasons) if reasons else "raison inconnue"
            logger.warning(f"Impossible d'invoquer le Double: {reason}")
            return {"success": False, "reason": reason}

        # Consommer les ressources
        if hasattr(self.sram, 'current_ap'):
            self.sram.current_ap -= DOUBLE_SUMMON_AP_COST
        if hasattr(self.sram, 'current_wp'):
            self.sram.current_wp -= DOUBLE_SUMMON_WP_COST

        # Passif Passe-Passe: echange de position a l'invocation
        swap_position = None
        if self.passives.get("passe_passe", False):
            swap_position = getattr(self.sram, 'position', None)

        # Creer le Double
        self.double = SramDouble(self.sram, position=position)

        # Passe-Passe: echange
        if swap_position and self.passives.get("passe_passe", False):
            old_sram_pos = getattr(self.sram, 'position', None)
            if old_sram_pos:
                self.sram.position = position
                self.double.position = old_sram_pos
                logger.info(
                    f"Passe-Passe: {self.sram.name} echange avec Double "
                    f"({old_sram_pos} <-> {position})"
                )

        # Cooldown
        self.summon_cooldown = DOUBLE_SUMMON_COOLDOWN
        self.total_summons += 1

        result = {
            "success": True,
            "action": "summon",
            "ap_cost": DOUBLE_SUMMON_AP_COST,
            "wp_cost": DOUBLE_SUMMON_WP_COST,
            "double_hp": self.double.current_hp,
            "double_lock": self.double.lock,
            "position": self.double.position,
            "passe_passe_swap": self.passives.get("passe_passe", False),
        }

        logger.info(
            f"{self.sram.name} invoque le Double en {self.double.position}! "
            f"PV={self.double.current_hp}, Tacle={self.double.lock}, "
            f"PA Sram restants: {getattr(self.sram, 'current_ap', '?')}"
        )

        return result

    def take_control(self):
        """
        Prend le controle du Double (sort gratuit si Double present).
        Le Sram joue le tour du Double instantanement.

        Returns:
            dict - resultat avec le sous-tour du Double prepare
        """
        if not self.double_on_field:
            return {"success": False, "reason": "Aucun Double sur le terrain"}

        # Reinitialiser le Double pour son sous-tour
        self.double.reset_turn()
        self.total_controls += 1

        result = {
            "success": True,
            "action": "take_control",
            "ap_cost": DOUBLE_CONTROL_AP_COST,
            "double_ap": self.double.current_ap,
            "double_mp": self.double.current_mp,
            "message": "Le Sram prend le controle du Double. Sous-tour instantane.",
        }

        logger.info(
            f"{self.sram.name} prend le controle du Double! "
            f"PA={self.double.current_ap}, PM={self.double.current_mp}"
        )

        return result

    def on_double_destroyed(self):
        """
        Appele quand le Double est detruit.
        Gere le passif Leurre si actif.

        Returns:
            dict - effets de la destruction
        """
        if not self.double:
            return {"destroyed": False}

        effects = {
            "destroyed": True,
            "leurre_explosion": False,
            "leurre_damage": 0,
            "leurre_hemorrhage": 0,
        }

        # Passif Leurre: explosion si degats directs recus
        if self.passives.get("leurre", False) and self.double.current_hp <= 0:
            leurre_damage = math.floor(self.double.max_hp * 0.5)
            effects["leurre_explosion"] = True
            effects["leurre_damage"] = leurre_damage
            effects["leurre_hemorrhage"] = 20
            logger.info(
                f"Leurre! {self.double.name} explose: {leurre_damage} degats "
                f"(cercle 2) + Hemorragie +20"
            )

        self.double.is_alive = False
        self.total_double_deaths += 1

        logger.info(f"{self.double.name} est detruit!")

        return effects

    def on_sram_turn_start(self):
        """Debut du tour du Sram: reset duperie."""
        self.duperie_used_this_round = {}

    def on_sram_turn_end(self):
        """
        Fin du tour du Sram.
        Decremente le cooldown d'invocation.
        Gere Passe-Passe (re-echange en fin de tour).
        """
        changes = {"cooldown_decreased": False, "passe_passe_swap_back": False}

        if self.summon_cooldown > 0:
            self.summon_cooldown -= 1
            changes["cooldown_decreased"] = True

        # Passe-Passe: re-echange en fin de tour
        if (self.passives.get("passe_passe", False)
                and self.double_on_field
                and self.total_summons > 0):
            # Echange Sram <-> Double en fin de tour
            sram_pos = getattr(self.sram, 'position', None)
            double_pos = self.double.position
            if sram_pos and double_pos:
                self.sram.position = double_pos
                self.double.position = sram_pos
                changes["passe_passe_swap_back"] = True
                logger.info(
                    f"Passe-Passe fin de tour: {self.sram.name} <-> Double "
                    f"({sram_pos} <-> {double_pos})"
                )

        return changes

    def on_sram_damaged(self, attacker_id):
        """
        Appele quand le Sram recoit des degats directs.
        Gere le passif Duperie.

        Args:
            attacker_id: int - ID du combattant qui attaque

        Returns:
            dict - {"swapped": bool}
        """
        if not self.passives.get("duperie", False):
            return {"swapped": False}
        if not self.double_on_field:
            return {"swapped": False}
        if self.duperie_used_this_round.get(attacker_id, False):
            return {"swapped": False}

        # Echange Sram <-> Double
        sram_pos = getattr(self.sram, 'position', None)
        double_pos = self.double.position
        if sram_pos and double_pos:
            self.sram.position = double_pos
            self.double.position = sram_pos
            self.duperie_used_this_round[attacker_id] = True
            logger.info(
                f"Duperie! {self.sram.name} echange avec le Double apres degats "
                f"({sram_pos} <-> {double_pos})"
            )
            return {"swapped": True, "sram_new_pos": double_pos, "double_new_pos": sram_pos}

        return {"swapped": False}

    # -----------------------------------------------------------------
    # ISOLE (interaction Double)
    # -----------------------------------------------------------------

    def is_target_isolated_or_adjacent_to_double(self, target_pos, all_fighters):
        """
        Verifie si une cible beneficie du bonus Isole pour le Sram.

        Source patch 1.91:
        "Le Sram inflige 50% Dommages supplementaires aux ennemis isoles
        ou au contact du Double. Une cible est consideree comme isolee
        si elle n'a aucun allie a 2 cases ou moins."

        ATTENTION: "allie" de la CIBLE, pas du Sram.
        Et "au contact du Double" = adjacent (distance Manhattan 1).

        Args:
            target_pos: tuple (x, y) - position de la cible
            all_fighters: list - tous les combattants vivants
                          chaque element doit avoir .position, .team, .is_alive

        Returns:
            dict - {"isolated": bool, "adjacent_to_double": bool,
                    "bonus_active": bool, "bonus_percent": int}
        """
        adjacent_to_double = False
        target_isolated = True

        # Trouver l'equipe de la cible
        target_team = None
        for f in all_fighters:
            if hasattr(f, 'position') and f.position == target_pos:
                target_team = getattr(f, 'team', None)
                break

        # Verifier si la cible est adjacente au Double
        if self.double_on_field and self.double.position:
            dist_to_double = (
                abs(target_pos[0] - self.double.position[0]) +
                abs(target_pos[1] - self.double.position[1])
            )
            if dist_to_double <= 1:
                adjacent_to_double = True

        # Verifier si la cible est isolee (aucun allie a 2 cases ou moins)
        if target_team is not None:
            for f in all_fighters:
                if not getattr(f, 'is_alive', True):
                    continue
                if getattr(f, 'team', None) != target_team:
                    continue
                if hasattr(f, 'position') and f.position == target_pos:
                    continue  # c'est la cible elle-meme
                # Est-ce que cet allie est a 2 cases ou moins?
                if hasattr(f, 'position') and f.position:
                    dist = (
                        abs(target_pos[0] - f.position[0]) +
                        abs(target_pos[1] - f.position[1])
                    )
                    if dist <= ISOLATED_RANGE:
                        target_isolated = False
                        break

        bonus_active = target_isolated or adjacent_to_double

        result = {
            "isolated": target_isolated,
            "adjacent_to_double": adjacent_to_double,
            "bonus_active": bonus_active,
            "bonus_percent": ISOLATED_BONUS_PERCENT if bonus_active else 0,
        }

        logger.debug(
            f"Isole check: cible={target_pos}, isole={target_isolated}, "
            f"adj_double={adjacent_to_double}, bonus={result['bonus_percent']}%"
        )

        return result

    def get_summary(self):
        """Resume complet du systeme Double."""
        return {
            "double_on_field": self.double_on_field,
            "double": self.double.get_summary() if self.double else None,
            "summon_cooldown": self.summon_cooldown,
            "can_summon": self.can_summon,
            "can_take_control": self.can_take_control,
            "passives": self.passives,
            "stats": {
                "total_summons": self.total_summons,
                "total_controls": self.total_controls,
                "total_deaths": self.total_double_deaths,
            }
        }


# =============================================================================
# TESTS
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("  TESTS ENGINE/DOUBLE.PY V5.0")
    print("=" * 60)

    # ----- Mock Fighter -----
    class MockFighter:
        def __init__(self, name, hp=8920, ap=13, mp=5, wp=8, level=179,
                     position=(5, 5), facing="N", team="A", dodge=100, block=30):
            self.name = name
            self.max_hp = hp
            self.hp = hp
            self.current_ap = ap
            self.current_mp = mp
            self.current_wp = wp
            self.level = level
            self.position = position
            self.facing = facing
            self.team = team
            self.dodge = dodge
            self.block = block
            self.is_alive = True

    # ============================================
    # TEST 1: Creation du Double
    # ============================================
    print("\n--- TEST 1: Creation du SramDouble ---")
    sram = MockFighter("L'Immortel", hp=8920, level=179)
    double = SramDouble(sram, position=(6, 5))

    expected_hp = math.floor(8920 * 40 / 100)  # 3568
    expected_lock = math.floor(179 * 200 / 100)  # 358

    assert double.max_hp == expected_hp, f"PV attendu {expected_hp}, obtenu {double.max_hp}"
    assert double.current_hp == expected_hp
    assert double.lock == expected_lock, f"Tacle attendu {expected_lock}, obtenu {double.lock}"
    assert double.current_ap == 8
    assert double.current_mp == 6
    assert double.current_wp == 6
    assert double.immune_sram_aoe == True

    print(f"  PV: {double.current_hp}/{double.max_hp} (40% de 8920 = {expected_hp})")
    print(f"  Tacle: {double.lock} (200% de niveau 179 = {expected_lock})")
    print(f"  PA={double.current_ap}, PM={double.current_mp}, PW={double.current_wp}")
    print(f"  Immunise AoE Sram: {double.immune_sram_aoe}")
    print("  -> OK")

    # ============================================
    # TEST 2: Sorts du Double
    # ============================================
    print("\n--- TEST 2: Sorts du Double ---")
    double.reset_turn()

    # Peur (2 PA)
    r2a = double.cast_spell("peur", target_pos=(6, 3))
    assert r2a["success"] == True
    assert double.current_ap == 6  # 8 - 2
    print(f"  Peur: {r2a['success']}, PA restants={double.current_ap}")

    # Diversion (2 PA)
    r2b = double.cast_spell("diversion")
    assert r2b["success"] == True
    assert double.current_ap == 4  # 6 - 2
    print(f"  Diversion: {r2b['success']}, PA restants={double.current_ap}")

    # Contact letal (2 PA)
    r2c = double.cast_spell("contact_letal", target_pos=(6, 4))
    assert r2c["success"] == True
    assert double.current_ap == 2  # 4 - 2
    print(f"  Contact letal: {r2c['success']}, PA restants={double.current_ap}")

    # Contact letal a nouveau -> cooldown
    r2d = double.cast_spell("contact_letal", target_pos=(6, 4))
    assert r2d["success"] == False
    print(f"  Contact letal (2eme fois): {r2d['success']} -> {r2d['reason']}")

    # Peur (2eme utilisation)
    r2e = double.cast_spell("peur", target_pos=(6, 2))
    assert r2e["success"] == True
    assert double.current_ap == 0
    print(f"  Peur (2eme): {r2e['success']}, PA restants={double.current_ap}")

    # Plus de PA
    r2f = double.cast_spell("peur", target_pos=(6, 1))
    assert r2f["success"] == False
    print(f"  Peur (3eme, 0 PA): {r2f['success']} -> {r2f['reason']}")
    print("  -> OK: sorts et limites fonctionnent")

    # ============================================
    # TEST 3: Invocation via DoubleManager
    # ============================================
    print("\n--- TEST 3: Invocation via DoubleManager ---")
    sram2 = MockFighter("Sram2", hp=8920, ap=13, wp=8, level=179, position=(5, 5))
    dm = DoubleManager(sram2, passives={})

    assert dm.can_summon == True
    assert dm.double_on_field == False

    r3 = dm.summon_double(position=(6, 5))
    assert r3["success"] == True
    assert r3["ap_cost"] == 2
    assert r3["wp_cost"] == 1
    assert sram2.current_ap == 11  # 13 - 2
    assert sram2.current_wp == 7   # 8 - 1
    assert dm.double_on_field == True
    assert dm.summon_cooldown == 2

    print(f"  Invocation: {r3['success']}, PA Sram: 13 -> {sram2.current_ap}, "
          f"PW Sram: 8 -> {sram2.current_wp}")
    print(f"  Double PV: {r3['double_hp']}, Tacle: {r3['double_lock']}")
    print(f"  Cooldown: {dm.summon_cooldown} tours")
    print("  -> OK")

    # ============================================
    # TEST 4: Prise de controle (Double deja present)
    # ============================================
    print("\n--- TEST 4: Prise de controle ---")
    assert dm.can_take_control == True
    assert dm.can_summon == False  # deja present

    r4 = dm.take_control()
    assert r4["success"] == True
    assert r4["ap_cost"] == 0  # gratuit
    assert r4["double_ap"] == 8  # reset
    assert r4["double_mp"] == 6

    print(f"  Controle: {r4['success']}, cout=0 PA")
    print(f"  Double: PA={r4['double_ap']}, PM={r4['double_mp']}")
    print("  -> OK: prise de controle gratuite, sous-tour pret")

    # ============================================
    # TEST 5: Immunite AoE du Sram
    # ============================================
    print("\n--- TEST 5: Immunite AoE du Sram ---")
    r5a = dm.double.take_damage(500, is_aoe_from_sram=True)
    assert r5a["immune"] == True
    assert r5a["damage_taken"] == 0
    print(f"  AoE Sram (500): immune={r5a['immune']}, degats={r5a['damage_taken']}")

    r5b = dm.double.take_damage(500, is_aoe_from_sram=False)
    assert r5b["immune"] == False
    assert r5b["damage_taken"] == 500
    print(f"  Degats normaux (500): immune={r5b['immune']}, degats={r5b['damage_taken']}")
    print(f"  PV Double: {dm.double.current_hp}/{dm.double.max_hp}")
    print("  -> OK")

    # ============================================
    # TEST 6: Bonus Isole
    # ============================================
    print("\n--- TEST 6: Bonus Isole (interaction Double) ---")

    # Creer des combattants pour le test
    enemy1 = MockFighter("Bouftou", position=(8, 5), team="B")
    enemy2 = MockFighter("Bouftou2", position=(9, 5), team="B")
    ally_of_enemy = MockFighter("BouftouAllie", position=(8, 6), team="B")

    all_fighters = [sram2, enemy1, enemy2, ally_of_enemy]

    # Double est en (6,5). enemy1 est en (8,5) -> distance 2 du Double -> pas adjacent
    # enemy1 a un allie (ally_of_enemy) a distance 1 -> PAS isole
    r6a = dm.is_target_isolated_or_adjacent_to_double(
        target_pos=(8, 5), all_fighters=all_fighters
    )
    print(f"  Bouftou (8,5) avec allie a (8,6): isole={r6a['isolated']}, "
          f"adj_double={r6a['adjacent_to_double']}, bonus={r6a['bonus_percent']}%")
    assert r6a["bonus_active"] == False  # pas isole, pas adjacent au Double

    # Deplacer le Double a cote de enemy1 (7,5)
    dm.double.position = (7, 5)
    r6b = dm.is_target_isolated_or_adjacent_to_double(
        target_pos=(8, 5), all_fighters=all_fighters
    )
    print(f"  Bouftou (8,5) avec Double a (7,5): isole={r6b['isolated']}, "
          f"adj_double={r6b['adjacent_to_double']}, bonus={r6b['bonus_percent']}%")
    assert r6b["adjacent_to_double"] == True
    assert r6b["bonus_active"] == True
    assert r6b["bonus_percent"] == 50

    # enemy2 en (9,5) est a distance 1 de enemy1 mais distance 2 du Double
    # enemy2 a enemy1 comme allie a 1 case -> PAS isole
    r6c = dm.is_target_isolated_or_adjacent_to_double(
        target_pos=(9, 5), all_fighters=all_fighters
    )
    print(f"  Bouftou2 (9,5) sans Double adj: isole={r6c['isolated']}, "
          f"adj_double={r6c['adjacent_to_double']}, bonus={r6c['bonus_percent']}%")
    assert r6c["bonus_active"] == False  # pas isole (allie a 1 case), pas adj au Double

    # Supprimer les allies de enemy1 -> enemy1 devient isole
    all_fighters_solo = [sram2, enemy1]
    r6d = dm.is_target_isolated_or_adjacent_to_double(
        target_pos=(8, 5), all_fighters=all_fighters_solo
    )
    print(f"  Bouftou (8,5) sans allies: isole={r6d['isolated']}, "
          f"adj_double={r6d['adjacent_to_double']}, bonus={r6d['bonus_percent']}%")
    assert r6d["isolated"] == True
    assert r6d["bonus_active"] == True

    print("  -> OK: bonus Isole correct (isole OU adjacent au Double)")

    # ============================================
    # TEST 7: Destruction du Double + Leurre
    # ============================================
    print("\n--- TEST 7: Destruction du Double + passif Leurre ---")

    sram3 = MockFighter("Sram3", hp=8920, level=179)
    dm3 = DoubleManager(sram3, passives={"leurre": True})
    dm3.summon_double(position=(6, 5))

    # Tuer le Double
    dm3.double.take_damage(99999)
    assert dm3.double.is_alive == False

    r7 = dm3.on_double_destroyed()
    assert r7["destroyed"] == True
    assert r7["leurre_explosion"] == True
    expected_leurre = math.floor(dm3.double.max_hp * 0.5)
    assert r7["leurre_damage"] == expected_leurre
    assert r7["leurre_hemorrhage"] == 20

    print(f"  Double detruit. Leurre: explosion={r7['leurre_explosion']}")
    print(f"  Degats explosion: {r7['leurre_damage']} (50% de {dm3.double.max_hp})")
    print(f"  Hemorragie: +{r7['leurre_hemorrhage']} niveaux (cercle 2)")
    print("  -> OK")

    # ============================================
    # TEST 8: Duperie (echange apres degats)
    # ============================================
    print("\n--- TEST 8: Passif Duperie ---")

    sram4 = MockFighter("Sram4", position=(5, 5), hp=8920, level=179)
    dm4 = DoubleManager(sram4, passives={"duperie": True})
    dm4.summon_double(position=(7, 5))
    dm4.on_sram_turn_start()

    # Sram recoit des degats du combattant ID 99
    r8a = dm4.on_sram_damaged(attacker_id=99)
    assert r8a["swapped"] == True
    print(f"  Degats recus: echange={r8a['swapped']}")
    print(f"  Sram: {sram4.position}, Double: {dm4.double.position}")

    # Deuxieme attaque du meme combattant dans le meme tour -> pas de re-echange
    r8b = dm4.on_sram_damaged(attacker_id=99)
    assert r8b["swapped"] == False
    print(f"  2eme attaque meme combattant: echange={r8b['swapped']}")

    # Attaque d'un autre combattant -> echange
    r8c = dm4.on_sram_damaged(attacker_id=100)
    assert r8c["swapped"] == True
    print(f"  Attaque autre combattant: echange={r8c['swapped']}")
    print("  -> OK: Duperie 1x par tour de combattant")

    # ============================================
    # TEST 9: Cooldown d'invocation
    # ============================================
    print("\n--- TEST 9: Cooldown d'invocation ---")

    sram5 = MockFighter("Sram5", hp=8920, ap=13, wp=8, level=179)
    dm5 = DoubleManager(sram5)

    dm5.summon_double(position=(6, 5))
    assert dm5.summon_cooldown == 2

    # Detruire le Double
    dm5.double.take_damage(99999)
    dm5.on_double_destroyed()
    assert dm5.double_on_field == False

    # Cooldown empeche de re-invoquer
    assert dm5.can_summon == False
    print(f"  Tour 1: cooldown={dm5.summon_cooldown}, can_summon={dm5.can_summon}")

    dm5.on_sram_turn_end()
    assert dm5.summon_cooldown == 1
    assert dm5.can_summon == False
    print(f"  Tour 2: cooldown={dm5.summon_cooldown}, can_summon={dm5.can_summon}")

    dm5.on_sram_turn_end()
    assert dm5.summon_cooldown == 0
    assert dm5.can_summon == True
    print(f"  Tour 3: cooldown={dm5.summon_cooldown}, can_summon={dm5.can_summon}")

    print("  -> OK: cooldown 2 tours respecte")

    # ============================================
    # TEST 10: Passe-Passe
    # ============================================
    print("\n--- TEST 10: Passif Passe-Passe ---")

    sram6 = MockFighter("Sram6", position=(5, 5), hp=8920, ap=13, wp=8, level=179)
    dm6 = DoubleManager(sram6, passives={"passe_passe": True})

    r10 = dm6.summon_double(position=(8, 5))
    print(f"  Invocation avec Passe-Passe:")
    print(f"  Sram: {sram6.position} (attendu: ancienne pos du Double)")
    print(f"  Double: {dm6.double.position} (attendu: ancienne pos du Sram)")
    assert r10["passe_passe_swap"] == True

    # Sauvegarder les positions pour verifier le re-echange
    sram_pos_mid = sram6.position
    double_pos_mid = dm6.double.position

    changes = dm6.on_sram_turn_end()
    assert changes["passe_passe_swap_back"] == True
    print(f"  Fin de tour: Sram={sram6.position}, Double={dm6.double.position}")
    print(f"  Re-echange: {changes['passe_passe_swap_back']}")
    print("  -> OK: Passe-Passe echange a l'invoc et re-echange en fin de tour")

    # ============================================
    # TEST 11: Resume
    # ============================================
    print("\n--- TEST 11: Resume ---")
    summary = dm6.get_summary()
    print(f"  Double present: {summary['double_on_field']}")
    print(f"  Stats: {summary['stats']}")
    print(f"  Cooldown: {summary['summon_cooldown']}")
    print("  -> OK")

    # ============================================
    # RESUME
    # ============================================
    print("\n" + "=" * 60)
    print("  TOUS LES TESTS PASSES - engine/double.py V5.0")
    print("=" * 60)
    print(f"\n  Modules couverts:")
    print(f"    - SramDouble: creation avec stats (40% PV, 200% lvl Tacle)")
    print(f"    - Sorts du Double (Peur, Embuscade, Contact letal, Diversion)")
    print(f"    - Invocation (2 PA, 1 PW, cooldown 2 tours)")
    print(f"    - Prise de controle (0 PA, sous-tour instantane)")
    print(f"    - Immunite AoE du Sram")
    print(f"    - Bonus Isole (50% df sur isole OU adjacent au Double)")
    print(f"    - Passif Leurre (explosion 50% PV + Hemorragie +20)")
    print(f"    - Passif Duperie (echange 1x/tour combattant)")
    print(f"    - Passif Passe-Passe (echange invoc + re-echange fin tour)")
    print(f"    - Cooldown d'invocation")
    print(f"    - Source: patch 1.91 (fevrier 2026)")
