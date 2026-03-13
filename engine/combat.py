"""
engine/combat.py - Boucle de combat WAKFU
Version 5.0

Orchestre un combat complet tour par tour:
  1. Initialisation: placement, calcul de l'ordre d'initiative
  2. Boucle de tours de table (round)
  3. Chaque tour de table: chaque combattant joue dans l'ordre fixe
  4. Chaque tour individuel: debut -> actions -> fin
  5. Conditions de fin: equipe eliminee ou max tours atteint

Vocabulaire:
  - Round (tour de table): tous les combattants jouent une fois
  - Turn (tour individuel): un seul combattant joue

Sources:
  - DESIGN_DOC.md sections 2, 3, 4, 5
  - MethodWakfu: https://methodwakfu.com/bien-debuter/informations-generales/
  - Patch 1.91: https://www.wakfu.com/en/mmorpg/news/patch-notes/1767730-update-1-91/details
"""

import sys, os, random, time, copy
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import config
from utils.logger import setup_logger
from engine.fighter import Fighter
from engine.grid import Grid
from engine.damage import calculate_damage, profile_to_stats

logger = setup_logger(__name__)


# ============================================================
# BONUS DE VELOCITE (CONFIRME PAR SAM)
# ============================================================

VELOCITY_BONUSES = {
    "prevention": {
        "display_name": "Prevention",
        "description": "Ajoute 20% des PV max en Armure",
        "type": "armor_percent_hp",
        "value": 20,
    },
    "ancrage": {
        "display_name": "Ancrage",
        "description": "Stabilise + ennemis au contact: -2 PM max",
        "type": "stabilize_and_pm_reduction",
        "stabilize_self": True,
        "enemy_pm_max_reduction": 2,
    },
    "meditation": {
        "display_name": "Meditation",
        "description": "+1 PW",
        "type": "gain_wp",
        "value": 1,
    },
    "brasier": {
        "display_name": "Brasier",
        "description": "Applique Embrasement aux ennemis",
        "type": "apply_state_enemies",
        "state_name": "embrasement",
        "state_level": 1,
        "state_duration": 2,
    },
    "liberation": {
        "display_name": "Liberation",
        "description": "Repousse de 2 cases allies et ennemis au contact",
        "type": "push_adjacent",
        "push_distance": 2,
    },
    "engouement": {
        "display_name": "Engouement",
        "description": "+2 PA pour le tour",
        "type": "gain_ap",
        "value": 2,
    },
}

VELOCITY_INTERVAL = 3


# ============================================================
# COMBAT
# ============================================================

class Combat:
    """Orchestre un combat complet.

    Usage:
        combat = Combat(grid, team_a=[fighter1], team_b=[fighter2, fighter3])
        result = combat.run()
    """

    def __init__(self, grid, team_a, team_b, max_rounds=None, seed=None,
                 velocity_strategy="engouement"):
        """
        Args:
            grid: instance de Grid deja configuree
            team_a: liste de Fighter (joueurs)
            team_b: liste de Fighter (monstres)
            max_rounds: nombre max de tours de table (defaut: config.MAX_TURNS)
            seed: graine RNG pour reproductibilite
            velocity_strategy: strategie de choix du bonus de velocite
                "engouement" = toujours prendre +2 PA
                "prevention" = toujours prendre armure
                "best" = choix optimal (futur IA)
                "random" = aleatoire
                "none" = toujours passer
        """
        self.grid = grid
        self.team_a = list(team_a)
        self.team_b = list(team_b)
        self.all_fighters = self.team_a + self.team_b
        self.max_rounds = max_rounds or config.MAX_TURNS
        self.velocity_strategy = velocity_strategy

        if seed is not None:
            random.seed(seed)
        self.seed = seed

        self.turn_order = []
        self.current_round = 0
        self.total_turns_played = 0
        self.combat_log = []
        self.is_finished = False
        self.winner = None

        self.velocity_bonuses_available_a = set(VELOCITY_BONUSES.keys())
        self.velocity_bonuses_available_b = set(VELOCITY_BONUSES.keys())

        self._compute_turn_order()

        self._sram_start_of_combat()

    def _compute_turn_order(self):
        """Calcule l'ordre des tours fixe pour tout le combat.
        Source: MethodWakfu section 1.3

        1. L'equipe avec la moyenne d'initiative la plus haute commence
        2. Au sein d'une equipe: ordre decroissant d'initiative
        3. Alternance A1 > B1 > A2 > B2 > ...
        4. Si une equipe a plus de combattants, les restants jouent a la suite
        """
        avg_a = sum(f.initiative for f in self.team_a) / max(len(self.team_a), 1)
        avg_b = sum(f.initiative for f in self.team_b) / max(len(self.team_b), 1)

        if avg_a >= avg_b:
            first_team = sorted(self.team_a, key=lambda f: f.initiative, reverse=True)
            second_team = sorted(self.team_b, key=lambda f: f.initiative, reverse=True)
            first_label = "A"
        else:
            first_team = sorted(self.team_b, key=lambda f: f.initiative, reverse=True)
            second_team = sorted(self.team_a, key=lambda f: f.initiative, reverse=True)
            first_label = "B"

        self.turn_order = []
        i, j = 0, 0
        while i < len(first_team) or j < len(second_team):
            if i < len(first_team):
                self.turn_order.append(first_team[i])
                i += 1
            if j < len(second_team):
                self.turn_order.append(second_team[j])
                j += 1

        order_str = " -> ".join(f"{f.name}({f.initiative})" for f in self.turn_order)
        logger.info(f"Ordre des tours (equipe {first_label} commence, avg {avg_a:.0f} vs {avg_b:.0f}): {order_str}")

    def _sram_start_of_combat(self):
        """Applique les bonus de debut de combat pour les Srams.
        Source: Patch 1.91 - innate mechanics
        +20% coup critique, +50 Point Faible
        """
        for f in self.all_fighters:
            if f.class_name == "sram" and f.is_alive:
                f.states.add_state("bonus_cc_debut", level=20, duration=999, source="sram_innate")
                f.add_weak_point(50)
                logger.info(f"  {f.name}: Sram innate -> +20%CC, +50 PF")

    # --------------------------------------------------------
    # VELOCITE
    # --------------------------------------------------------

    def _is_velocity_round(self):
        """Verifie si ce tour de table est un tour de velocite."""
        return self.current_round > 0 and self.current_round % VELOCITY_INTERVAL == 0

    def _get_velocity_available(self, fighter):
        """Retourne les bonus de velocite disponibles pour ce combattant."""
        if fighter.fighter_type != "player":
            return {}

        if fighter.team == "A":
            available = self.velocity_bonuses_available_a
        else:
            available = self.velocity_bonuses_available_b

        return {k: v for k, v in VELOCITY_BONUSES.items() if k in available}

    def _choose_velocity_bonus(self, fighter):
        """Choisit un bonus de velocite selon la strategie.
        Retourne le nom du bonus choisi ou None si passe.
        """
        available = self._get_velocity_available(fighter)
        if not available:
            return None

        strategy = self.velocity_strategy

        if strategy == "none":
            return None
        elif strategy == "engouement" and "engouement" in available:
            return "engouement"
        elif strategy == "prevention" and "prevention" in available:
            return "prevention"
        elif strategy == "random":
            return random.choice(list(available.keys()))
        elif strategy == "best":
            if "engouement" in available:
                return "engouement"
            elif "prevention" in available:
                return "prevention"
            elif "meditation" in available:
                return "meditation"
            else:
                return list(available.keys())[0] if available else None
        else:
            if strategy in available:
                return strategy
            return list(available.keys())[0] if available else None

    def _apply_velocity_bonus(self, fighter, bonus_name):
        """Applique un bonus de velocite a un combattant."""
        if bonus_name is None:
            return

        bonus = VELOCITY_BONUSES[bonus_name]

        if bonus["type"] == "gain_ap":
            fighter.gain_ap(bonus["value"])
            logger.info(f"  Velocite {bonus['display_name']}: {fighter.name} gagne +{bonus['value']} PA")

        elif bonus["type"] == "gain_wp":
            fighter.gain_wp(bonus["value"])
            logger.info(f"  Velocite {bonus['display_name']}: {fighter.name} gagne +{bonus['value']} PW")

        elif bonus["type"] == "armor_percent_hp":
            armor_amount = fighter.max_hp * bonus["value"] / 100
            fighter.gain_armor(armor_amount)
            logger.info(f"  Velocite {bonus['display_name']}: {fighter.name} gagne {armor_amount:.0f} armure")

        elif bonus["type"] == "stabilize_and_pm_reduction":
            fighter.states.add_state("stabilise", level=1, duration=1, source="velocite_ancrage")
            adjacent_enemies = [f for f in self.all_fighters
                                if f.team != fighter.team and f.is_alive
                                and fighter.is_adjacent(f)]
            for enemy in adjacent_enemies:
                enemy.states.add_state("pm_max_reduction", level=bonus["enemy_pm_max_reduction"],
                                       duration=1, source="velocite_ancrage")
            logger.info(f"  Velocite {bonus['display_name']}: {fighter.name} stabilise, {len(adjacent_enemies)} ennemis -2PM max")

        elif bonus["type"] == "apply_state_enemies":
            enemies = [f for f in self.all_fighters if f.team != fighter.team and f.is_alive]
            for enemy in enemies:
                enemy.states.add_state(bonus["state_name"], level=bonus["state_level"],
                                       duration=bonus["state_duration"], source="velocite_brasier")
            logger.info(f"  Velocite {bonus['display_name']}: Embrasement sur {len(enemies)} ennemis")

        elif bonus["type"] == "push_adjacent":
            logger.info(f"  Velocite {bonus['display_name']}: push {bonus['push_distance']} cases (TODO: impl grid push)")

        if fighter.team == "A":
            self.velocity_bonuses_available_a.discard(bonus_name)
        else:
            self.velocity_bonuses_available_b.discard(bonus_name)

    # --------------------------------------------------------
    # BOUCLE PRINCIPALE
    # --------------------------------------------------------

    def run(self, action_callback=None):
        """Lance le combat complet.

        Args:
            action_callback: fonction(combat, fighter) -> list[actions]
                Si None, les combattants passent leur tour (mode test).

        Retourne un dict avec les resultats du combat.
        """
        start_time = time.time()

        self._log_event("combat_start", {
            "team_a": [f.name for f in self.team_a],
            "team_b": [f.name for f in self.team_b],
            "turn_order": [f.name for f in self.turn_order],
        })

        logger.info(f"\n{'='*60}")
        logger.info(f"  COMBAT DEMARRE - Max {self.max_rounds} rounds")
        logger.info(f"{'='*60}")

        while not self.is_finished:
            self.current_round += 1

            if self.current_round > self.max_rounds:
                self.is_finished = True
                self.winner = "timeout"
                logger.info(f"\n  TIMEOUT - {self.max_rounds} rounds atteints")
                break

            is_velocity = self._is_velocity_round()
            if is_velocity:
                self.velocity_bonuses_available_a = set(VELOCITY_BONUSES.keys())
                self.velocity_bonuses_available_b = set(VELOCITY_BONUSES.keys())

            logger.info(f"\n--- ROUND {self.current_round} ---" +
                        (" [VELOCITE]" if is_velocity else ""))

            for fighter in self.turn_order:
                if not fighter.is_alive:
                    continue

                if self._check_win_condition():
                    break

                self._play_turn(fighter, is_velocity, action_callback)

                if self._check_win_condition():
                    break

        elapsed = time.time() - start_time

        result = {
            "winner": self.winner,
            "rounds": self.current_round,
            "total_turns": self.total_turns_played,
            "elapsed_seconds": round(elapsed, 3),
            "team_a_alive": sum(1 for f in self.team_a if f.is_alive),
            "team_b_alive": sum(1 for f in self.team_b if f.is_alive),
            "team_a_hp": sum(f.hp for f in self.team_a),
            "team_b_hp": sum(f.hp for f in self.team_b),
            "combat_log": self.combat_log,
            "seed": self.seed,
        }

        logger.info(f"\n{'='*60}")
        logger.info(f"  COMBAT TERMINE - Vainqueur: {self.winner}")
        logger.info(f"  Rounds: {self.current_round} | Tours joues: {self.total_turns_played}")
        logger.info(f"  Equipe A: {result['team_a_alive']} vivants, {result['team_a_hp']:.0f} PV")
        logger.info(f"  Equipe B: {result['team_b_alive']} vivants, {result['team_b_hp']:.0f} PV")
        logger.info(f"  Temps: {elapsed:.3f}s")
        logger.info(f"{'='*60}")

        return result

    def _play_turn(self, fighter, is_velocity_round, action_callback):
        """Joue le tour d'un combattant."""
        self.total_turns_played += 1

        fighter.start_of_turn()

        self._apply_start_of_turn_effects(fighter)

        if is_velocity_round and fighter.fighter_type == "player":
            bonus = self._choose_velocity_bonus(fighter)
            self._apply_velocity_bonus(fighter, bonus)

        if action_callback:
            actions = action_callback(self, fighter)
            if actions:
                for action in actions:
                    self._execute_action(fighter, action)
        else:
            logger.debug(f"  {fighter.name} passe son tour (pas de callback)")

        self._apply_end_of_turn_effects(fighter)

        fighter.end_of_turn()

        self._log_event("turn_end", {
            "fighter": fighter.name,
            "round": self.current_round,
            "hp": fighter.hp,
            "armor": round(fighter.armor),
            "states": list(fighter.states.list_states().keys()),
        })

    def _apply_start_of_turn_effects(self, fighter):
        """Applique les effets de debut de tour."""
        if fighter.class_name == "sram":
            if fighter.states.has_state("hemophilie"):
                level = fighter.states.get_level("hemophilie")
                poison_dmg = level * 4 * fighter.level / 100
                fighter.take_damage(poison_dmg)
                logger.info(f"  {fighter.name}: Hemophilie niv {level} -> {poison_dmg:.0f} degats")

    def _apply_end_of_turn_effects(self, fighter):
        """Applique les effets de fin de tour."""
        if fighter.class_name == "sram":
            is_isolated = fighter.is_isolated(self.all_fighters)
            has_meurtrier = fighter.states.has_state("meurtrier")
            if is_isolated and not has_meurtrier:
                fighter.add_weak_point(25)
                logger.info(f"  {fighter.name}: Isole sans Meurtrier -> +25 PF")

    def _execute_action(self, fighter, action):
        """Execute une action (sort, deplacement, etc.)
        Structure d'une action:
            {"type": "spell", "spell_name": "...", "target_id": N, ...}
            {"type": "move", "dx": N, "dy": N}
            {"type": "pass"}
        """
        action_type = action.get("type", "pass")

        if action_type == "pass":
            return

        elif action_type == "move":
            dx = action.get("dx", 0)
            dy = action.get("dy", 0)
            fighter.move(dx, dy, cost_mp=True)

        elif action_type == "spell":
            logger.debug(f"  {fighter.name} lance {action.get('spell_name', '?')} (TODO: impl spell execution)")

    def _check_win_condition(self):
        """Verifie si une equipe a gagne."""
        a_alive = any(f.is_alive for f in self.team_a)
        b_alive = any(f.is_alive for f in self.team_b)

        if not a_alive and not b_alive:
            self.is_finished = True
            self.winner = "draw"
            return True
        elif not b_alive:
            self.is_finished = True
            self.winner = "team_a"
            return True
        elif not a_alive:
            self.is_finished = True
            self.winner = "team_b"
            return True
        return False

    def _log_event(self, event_type, data):
        """Ajoute un evenement au log du combat."""
        self.combat_log.append({
            "round": self.current_round,
            "type": event_type,
            "data": data,
        })

    # --------------------------------------------------------
    # UTILITAIRES
    # --------------------------------------------------------

    def get_alive_fighters(self, team=None):
        """Retourne les combattants vivants, optionnellement filtres par equipe."""
        fighters = self.all_fighters
        if team:
            fighters = [f for f in fighters if f.team == team]
        return [f for f in fighters if f.is_alive]

    def get_enemies(self, fighter):
        """Retourne les ennemis vivants d'un combattant."""
        return [f for f in self.all_fighters
                if f.team != fighter.team and f.is_alive]

    def get_allies(self, fighter, include_self=False):
        """Retourne les allies vivants d'un combattant."""
        allies = [f for f in self.all_fighters
                  if f.team == fighter.team and f.is_alive]
        if not include_self:
            allies = [f for f in allies if f.id != fighter.id]
        return allies

    def get_combat_summary(self):
        """Retourne un resume lisible du combat."""
        lines = [f"=== Round {self.current_round}/{self.max_rounds} ==="]
        for f in self.turn_order:
            status = "ALIVE" if f.is_alive else "K.O."
            lines.append(f"  {f.summary()} [{status}]")
        return "\n".join(lines)


# ============================================================
# TESTS
# ============================================================

if __name__ == "__main__":
    from data.profiles.limmortel import PROFILE

    print("=" * 60)
    print("  TESTS ENGINE/COMBAT.PY V5.0")
    print("=" * 60)

    # --- Setup ---
    grid = Grid(15, 15)
    grid.set_cell_type(7, 7, "obstacle")

    sram = Fighter("L'Immortel", team="A", profile=PROFILE)
    grid.place_fighter(sram, 5, 5)
    sram.facing = "E"

    mob1 = Fighter("Bouftou Alpha", team="B", fighter_type="monster", level=179,
                    monster_template={
                        "hp": 12000, "ap": 8, "mp": 4, "initiative": 120,
                        "res_fire": 300, "res_water": 250,
                        "lock": 150, "dodge": 80,
                        "damage_inflicted": 30,
                        "masteries": {"fire": 600, "earth": 600, "melee": 400},
                    })
    grid.place_fighter(mob1, 7, 5)
    mob1.facing = "W"

    mob2 = Fighter("Bouftou Beta", team="B", fighter_type="monster", level=150,
                    monster_template={
                        "hp": 8000, "ap": 6, "mp": 3, "initiative": 90,
                        "res_fire": 200, "res_water": 200,
                        "lock": 100, "dodge": 60,
                        "damage_inflicted": 20,
                        "masteries": {"fire": 400, "water": 400, "melee": 300},
                    })
    grid.place_fighter(mob2, 9, 5)
    mob2.facing = "W"

    print(f"\n--- Setup ---")
    print(grid.render([sram, mob1, mob2]))

    # --- Test 1: Ordre d'initiative ---
    combat = Combat(grid, team_a=[sram], team_b=[mob1, mob2],
                    max_rounds=4, seed=42, velocity_strategy="engouement")
    print(f"\nTest 1 - Ordre: {[f.name for f in combat.turn_order]}")

    # --- Test 2: Combat sans actions (pass) ---
    print(f"\nTest 2 - Combat 4 rounds (tout le monde passe):")
    result = combat.run()
    print(f"  Vainqueur: {result['winner']}")
    print(f"  Rounds: {result['rounds']} | Tours joues: {result['total_turns']}")
    print(f"  Equipe A: {result['team_a_alive']} vivants, {result['team_a_hp']:.0f} PV")
    print(f"  Equipe B: {result['team_b_alive']} vivants, {result['team_b_hp']:.0f} PV")
    print(f"  Temps: {result['elapsed_seconds']}s")

    # --- Test 3: Verifier PF du Sram (debut combat +50, puis +25/tour isole) ---
    print(f"\nTest 3 - Point Faible du Sram apres combat:")
    print(f"  PF: {sram.weak_point}")
    print(f"  PA: {sram.ap} | PM: {sram.mp} | PW: {sram.wp}")
    print(f"  Hemorrhagie: {sram.states.get_level('hemorrhagie')}")

    # --- Test 4: Combat avec kill ---
    print(f"\nTest 4 - Combat avec kill simule:")
    grid2 = Grid(10, 10)
    sram2 = Fighter("Sram2", team="A", profile=PROFILE)
    grid2.place_fighter(sram2, 3, 3)
    weak_mob = Fighter("Larve", team="B", fighter_type="monster", level=10,
                        monster_template={"hp": 1, "ap": 4, "mp": 2, "initiative": 10})
    grid2.place_fighter(weak_mob, 5, 3)

    def kill_action(combat_inst, fighter):
        if fighter.name == "Sram2":
            enemies = combat_inst.get_enemies(fighter)
            if enemies:
                enemies[0].take_damage(9999)
                return [{"type": "pass"}]
        return [{"type": "pass"}]

    combat2 = Combat(grid2, team_a=[sram2], team_b=[weak_mob],
                     max_rounds=3, seed=123)
    result2 = combat2.run(action_callback=kill_action)
    print(f"  Vainqueur: {result2['winner']}")
    print(f"  Rounds: {result2['rounds']}")

    # --- Test 5: Velocite ---
    print(f"\nTest 5 - Velocite (round 3 et 6):")
    grid3 = Grid(10, 10)
    player = Fighter("TestPlayer", team="A", fighter_type="player", level=100,
                      monster_template={"hp": 5000, "ap": 10, "mp": 4, "initiative": 200})
    player.fighter_type = "player"
    grid3.place_fighter(player, 3, 3)
    dummy_mob = Fighter("Dummy", team="B", fighter_type="monster", level=100,
                         monster_template={"hp": 99999, "ap": 6, "mp": 3, "initiative": 50})
    grid3.place_fighter(dummy_mob, 7, 3)

    combat3 = Combat(grid3, team_a=[player], team_b=[dummy_mob],
                     max_rounds=7, seed=999, velocity_strategy="engouement")
    result3 = combat3.run()
    print(f"  Rounds joues: {result3['rounds']}")

    print(f"\n{'=' * 60}")
    print("  TOUS LES TESTS TERMINES")
    print(f"{'=' * 60}")
