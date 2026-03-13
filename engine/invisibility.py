# =============================================================================
# engine/invisibility.py - V5.0
# Systeme d'invisibilite du Sram (patch 1.91)
# =============================================================================
# Sources:
#   - Patch 1.91 FR: https://www.wakfu.com/fr/mmorpg/actualites/maj/1767729-mise-jour-1-91/details
#   - Patch 1.91 EN: https://www.wakfu.com/en/mmorpg/news/patch-notes/1767730-update-1-91/details
#   - MethodWakfu:   https://methodwakfu.com/bien-debuter/informations-generales/
#   - DESIGN_DOC.md sections Invisibilite, Maitre des Ombres
# =============================================================================
#
# CYCLE D'INVISIBILITE DU SRAM (patch 1.91):
# -------------------------------------------
# 1. Le Sram lance Invisibilite (0 PA, 2 PW)
#    -> Devient Invisible (2 tours)
#    -> Gagne +2 PM max (1 tour)
#    -> Recoit Apparent (3 tours) = ne peut plus etre cible par Invisibilite
#    -> Recoit Maitre des Ombres (special):
#       "Au tour SUIVANT, +100% Dommages infliges au prochain sort de degats directs"
#
# 2. Tour suivant (Maitre des Ombres actif):
#    -> Le prochain sort de degats directs beneficie de +100% DI (x2 degats)
#    -> Apres ce sort, Maitre des Ombres est consomme
#
# 3. Avec le passif RETENUE:
#    -> Invisibilite n'est revelee que par un sort coutant >= 4 PA
#    -> Les sorts < 4 PA ne brisent PAS l'invisibilite
#    -> Permet de preparer (Kleptosram 2PA, etc.) avant le gros burst
#
# 4. Sans Retenue:
#    -> Tout sort offensif revele l'invisibilite
#
# STRATEGIE OPTIMALE:
# Tour N: Invisibilite -> se positionner dans le dos
# Tour N+1: Maitre des Ombres actif -> sorts < 4PA (avec Retenue) 
#           -> puis sort >= 4PA pour le burst x2 (revele l'invi)
# =============================================================================

import logging
import sys
import os

# Ajouter la racine du projet au path pour les imports absolus
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from utils.logger import setup_logger
    logger = setup_logger("engine.invisibility")
except ImportError:
    logger = logging.getLogger("engine.invisibility")
    logging.basicConfig(level=logging.INFO)


# =============================================================================
# 1. CONSTANTES
# =============================================================================

# Sort Invisibilite
INVISIBILITY_AP_COST = 0
INVISIBILITY_WP_COST = 2
INVISIBILITY_RANGE_MIN = 1
INVISIBILITY_RANGE_MAX = 4
INVISIBILITY_DURATION = 2           # tours d'invisibilite
INVISIBILITY_MP_BONUS = 2           # +2 PM max (1 tour)
INVISIBILITY_MP_BONUS_DURATION = 1
APPARENT_DURATION = 3               # tours d'Apparent (anti-re-invi)
INVISIBILITY_USES_PER_TURN = 1

# Maitre des Ombres
SHADOW_MASTER_DI_BONUS = 100        # +100% DI au prochain sort direct
SHADOW_MASTER_DELAY = 1             # s'active au tour SUIVANT

# Passif Retenue
RESTRAINT_MIN_AP_TO_REVEAL = 4      # sort >= 4 PA pour reveler

# Effets de l'Invisibilite (source: wiki + patch notes)
INVISIBLE_DODGE_BONUS_PERCENT = 30  # +30% du total d'Esquive
INVISIBLE_CANT_LOCK = True          # ne peut plus tacler
INVISIBLE_NO_LOS_BLOCK = True       # ne bloque plus la ligne de vue


# =============================================================================
# 2. CLASSE INVISIBILITY MANAGER
# =============================================================================

class InvisibilityManager:
    """
    Gere le cycle d'invisibilite du Sram pour un combattant.
    S'attache a un Fighter et suit son etat d'invisibilite,
    Maitre des Ombres, et Apparent.
    """
    
    def __init__(self, fighter, has_restraint=True):
        """
        Args:
            fighter: Fighter object - le Sram
            has_restraint: bool - le passif Retenue est-il equipe?
        """
        self.fighter = fighter
        self.has_restraint = has_restraint
        
        # Etats internes
        self.invisible_turns = 0         # tours restants d'invisibilite
        self.apparent_turns = 0          # tours restants d'Apparent
        self.shadow_master_ready = False # Maitre des Ombres pret (s'active tour suivant)
        self.shadow_master_active = False # Maitre des Ombres actif CE tour
        self.mp_bonus_turns = 0          # tours restants du bonus PM
        
        # Compteurs pour stats/logging
        self.total_invisibility_casts = 0
        self.total_shadow_master_procs = 0
        self.total_reveals = 0
        self.spells_cast_while_invisible = 0
        
        logger.info(
            f"InvisibilityManager cree pour {fighter.name} "
            f"(Retenue: {has_restraint})"
        )
    
    # -----------------------------------------------------------------
    # PROPRIETES
    # -----------------------------------------------------------------
    
    @property
    def is_invisible(self):
        """Le combattant est-il invisible?"""
        return self.invisible_turns > 0
    
    @property
    def is_apparent(self):
        """Le combattant a-t-il l'etat Apparent? (ne peut pas etre re-invisible)"""
        return self.apparent_turns > 0
    
    @property
    def can_cast_invisibility(self):
        """Peut-on lancer Invisibilite sur ce combattant?"""
        # Pas si deja Apparent
        if self.is_apparent:
            return False
        # Pas si deja Invisible
        if self.is_invisible:
            return False
        # Verifier les PW
        if hasattr(self.fighter, 'current_wp'):
            if self.fighter.current_wp < INVISIBILITY_WP_COST:
                return False
        return True
    
    @property
    def has_shadow_master(self):
        """Maitre des Ombres est-il actif ce tour?"""
        return self.shadow_master_active
    
    # -----------------------------------------------------------------
    # ACTIONS
    # -----------------------------------------------------------------
    
    def cast_invisibility(self, target=None):
        """
        Lance le sort Invisibilite.
        
        Source patch 1.91:
        - 0 PA, 2 PW, portee 1-4
        - Rend la cible Invisible (2 tours)
        - +2 PM max (1 tour)
        - Applique Apparent (3 tours)
        - Sram: Applique Maitre des Ombres (tour suivant, +100% DI prochain sort direct)
        - 1 utilisation par tour
        
        Args:
            target: Fighter or None - si None, cible = self.fighter
            
        Returns:
            dict - resultat de l'action avec tous les effets appliques
        """
        if target is None:
            target_mgr = self
            target_fighter = self.fighter
        else:
            # Si on cible un allie, il faut un autre InvisibilityManager
            # Pour simplifier, on gere seulement le cas du Sram lui-meme
            target_mgr = self
            target_fighter = self.fighter
        
        # Verifications
        if not self.can_cast_invisibility:
            reason = "Apparent" if self.is_apparent else "deja Invisible" if self.is_invisible else "PW insuffisants"
            logger.warning(
                f"{self.fighter.name} ne peut pas lancer Invisibilite: {reason}"
            )
            return {"success": False, "reason": reason}
        
        # Avec le passif Retenue, Invisibilite ne peut plus cibler un allie
        if self.has_restraint and target is not None and target != self.fighter:
            logger.warning(
                f"{self.fighter.name} a Retenue: Invisibilite ne peut plus cibler un allie"
            )
            return {"success": False, "reason": "Retenue interdit les allies"}
        
        # Consommer les PW
        wp_cost = INVISIBILITY_WP_COST
        if hasattr(self.fighter, 'current_wp'):
            self.fighter.current_wp -= wp_cost
        
        # Appliquer les effets
        target_mgr.invisible_turns = INVISIBILITY_DURATION
        target_mgr.apparent_turns = APPARENT_DURATION
        target_mgr.mp_bonus_turns = INVISIBILITY_MP_BONUS_DURATION
        
        # Maitre des Ombres: s'active au tour SUIVANT
        # On le met en "ready" et il passera en "active" au debut du prochain tour
        target_mgr.shadow_master_ready = True
        target_mgr.shadow_master_active = False
        
        # Bonus PM
        mp_gained = INVISIBILITY_MP_BONUS
        if hasattr(target_fighter, 'current_mp'):
            target_fighter.current_mp += mp_gained
        if hasattr(target_fighter, 'max_mp_bonus'):
            target_fighter.max_mp_bonus = getattr(target_fighter, 'max_mp_bonus', 0) + mp_gained
        
        self.total_invisibility_casts += 1
        
        result = {
            "success": True,
            "wp_cost": wp_cost,
            "invisible_duration": INVISIBILITY_DURATION,
            "apparent_duration": APPARENT_DURATION,
            "mp_bonus": mp_gained,
            "shadow_master": "ready (activera tour suivant)",
        }
        
        logger.info(
            f"{self.fighter.name} lance Invisibilite! "
            f"Invisible {INVISIBILITY_DURATION} tours, Apparent {APPARENT_DURATION} tours, "
            f"+{mp_gained} PM max, Maitre des Ombres pret. "
            f"PW restants: {getattr(self.fighter, 'current_wp', '?')}"
        )
        
        return result
    
    def on_spell_cast(self, spell_ap_cost, is_direct_damage=True):
        """
        Appele quand le Sram lance un sort offensif pendant l'invisibilite.
        Gere la revelation et la consommation de Maitre des Ombres.
        
        Source patch 1.91:
        - Avec Retenue: seuls les sorts >= 4 PA revelent l'invisibilite
        - Sans Retenue: tout sort offensif revele
        - Maitre des Ombres: +100% DI sur le prochain sort de degats directs
        
        Args:
            spell_ap_cost: int - cout en PA du sort lance
            is_direct_damage: bool - le sort inflige-t-il des degats directs?
            
        Returns:
            dict - {
                "di_bonus": int,        # bonus de DI applique (0 ou 100)
                "revealed": bool,       # l'invisibilite a-t-elle ete brisee?
                "shadow_master_consumed": bool
            }
        """
        di_bonus = 0
        revealed = False
        shadow_master_consumed = False
        
        # Maitre des Ombres: bonus au prochain sort de degats directs
        if self.shadow_master_active and is_direct_damage:
            di_bonus = SHADOW_MASTER_DI_BONUS
            self.shadow_master_active = False
            self.shadow_master_ready = False
            shadow_master_consumed = True
            self.total_shadow_master_procs += 1
            logger.info(
                f"{self.fighter.name}: Maitre des Ombres consomme! "
                f"+{di_bonus}% DI sur ce sort"
            )
        
        # Revelation de l'invisibilite
        if self.is_invisible:
            self.spells_cast_while_invisible += 1
            
            if self.has_restraint:
                # Avec Retenue: revele seulement si sort >= 4 PA
                if spell_ap_cost >= RESTRAINT_MIN_AP_TO_REVEAL:
                    revealed = True
                    logger.info(
                        f"{self.fighter.name}: sort {spell_ap_cost} PA >= {RESTRAINT_MIN_AP_TO_REVEAL} PA "
                        f"-> Invisibilite revelee! (Retenue)"
                    )
                else:
                    logger.info(
                        f"{self.fighter.name}: sort {spell_ap_cost} PA < {RESTRAINT_MIN_AP_TO_REVEAL} PA "
                        f"-> reste Invisible (Retenue)"
                    )
            else:
                # Sans Retenue: tout sort offensif revele
                revealed = True
                logger.info(
                    f"{self.fighter.name}: sort offensif -> Invisibilite revelee! (pas de Retenue)"
                )
            
            if revealed:
                self.invisible_turns = 0
                self.total_reveals += 1
        
        return {
            "di_bonus": di_bonus,
            "revealed": revealed,
            "shadow_master_consumed": shadow_master_consumed,
        }
    
    def on_damage_received(self, damage_amount):
        """
        Appele quand le Sram invisible recoit des degats.
        Les degats brisent l'invisibilite.
        
        Source: Wakfu wiki "tant qu'il ne subit aucun degat"
        Note patch 1.91: comportement inchange
        
        Args:
            damage_amount: int - degats recus
            
        Returns:
            bool - True si l'invisibilite a ete brisee
        """
        if self.is_invisible and damage_amount > 0:
            self.invisible_turns = 0
            self.total_reveals += 1
            logger.info(
                f"{self.fighter.name}: recoit {damage_amount} degats -> Invisibilite brisee!"
            )
            return True
        return False
    
    # -----------------------------------------------------------------
    # CYCLE DE TOUR
    # -----------------------------------------------------------------
    
    def on_turn_start(self):
        """
        Appele en debut de tour du Sram.
        Active Maitre des Ombres si il etait en "ready" (du tour precedent).
        
        Returns:
            dict - effets appliques en debut de tour
        """
        effects = {
            "shadow_master_activated": False,
            "invisible": self.is_invisible,
            "invisible_turns_remaining": self.invisible_turns,
        }
        
        # Maitre des Ombres: passe de "ready" a "active"
        if self.shadow_master_ready and not self.shadow_master_active:
            self.shadow_master_active = True
            self.shadow_master_ready = False
            effects["shadow_master_activated"] = True
            logger.info(
                f"{self.fighter.name}: Maitre des Ombres ACTIF! "
                f"+{SHADOW_MASTER_DI_BONUS}% DI au prochain sort direct"
            )
        
        if self.is_invisible:
            logger.info(
                f"{self.fighter.name}: Invisible ({self.invisible_turns} tour(s) restant(s))"
            )
        
        return effects
    
    def on_turn_end(self):
        """
        Appele en fin de tour du Sram.
        Decremente les compteurs d'etats.
        
        Returns:
            dict - changements effectues
        """
        changes = {
            "invisible_expired": False,
            "apparent_expired": False,
            "mp_bonus_expired": False,
        }
        
        # Decrementation Invisible
        if self.invisible_turns > 0:
            self.invisible_turns -= 1
            if self.invisible_turns == 0:
                changes["invisible_expired"] = True
                logger.info(f"{self.fighter.name}: Invisibilite expiree")
        
        # Decrementation Apparent
        if self.apparent_turns > 0:
            self.apparent_turns -= 1
            if self.apparent_turns == 0:
                changes["apparent_expired"] = True
                logger.info(f"{self.fighter.name}: Apparent expire")
        
        # Decrementation bonus PM
        if self.mp_bonus_turns > 0:
            self.mp_bonus_turns -= 1
            if self.mp_bonus_turns == 0:
                changes["mp_bonus_expired"] = True
                # Retirer le bonus PM
                if hasattr(self.fighter, 'current_mp'):
                    self.fighter.current_mp = max(
                        0, self.fighter.current_mp - INVISIBILITY_MP_BONUS
                    )
                if hasattr(self.fighter, 'max_mp_bonus'):
                    self.fighter.max_mp_bonus = max(
                        0, getattr(self.fighter, 'max_mp_bonus', 0) - INVISIBILITY_MP_BONUS
                    )
                logger.info(
                    f"{self.fighter.name}: bonus +{INVISIBILITY_MP_BONUS} PM max expire"
                )
        
        return changes
    
    # -----------------------------------------------------------------
    # UTILITAIRES
    # -----------------------------------------------------------------
    
    def get_combat_modifiers(self):
        """
        Retourne les modificateurs actifs lies a l'invisibilite.
        Utilise par le moteur de combat/degats pour appliquer les bonus.
        
        Returns:
            dict - modificateurs actifs
        """
        mods = {
            "invisible": self.is_invisible,
            "dodge_bonus_percent": INVISIBLE_DODGE_BONUS_PERCENT if self.is_invisible else 0,
            "can_lock": not INVISIBLE_CANT_LOCK if self.is_invisible else True,
            "blocks_los": not INVISIBLE_NO_LOS_BLOCK if self.is_invisible else True,
            "shadow_master_di": SHADOW_MASTER_DI_BONUS if self.shadow_master_active else 0,
            "mp_bonus": INVISIBILITY_MP_BONUS if self.mp_bonus_turns > 0 else 0,
        }
        return mods
    
    def get_optimal_rotation_advice(self):
        """
        Retourne des conseils sur la rotation optimale actuelle.
        Utile pour l'IA greedy et le debug.
        
        Returns:
            str - conseil textuel
        """
        if self.can_cast_invisibility:
            return (
                "PHASE 1: Lancer Invisibilite -> se positionner dans le dos de la cible. "
                "Maitre des Ombres s'activera au tour suivant."
            )
        
        if self.shadow_master_active and self.is_invisible and self.has_restraint:
            return (
                "PHASE 2 (BURST): Maitre des Ombres actif + Invisible + Retenue. "
                "Lancer d'abord les sorts < 4PA (Kleptosram 2PA pour +5 PF si dos, "
                "Arnaque 2PA pour consommer PF) -> rester invisible. "
                "Puis finir avec un sort >= 4PA (Traumatisme 4PA, Attaque letale 4PA, "
                "Chatiment 4PA) pour le burst x2 qui revele l'invisibilite."
            )
        
        if self.shadow_master_active and self.is_invisible and not self.has_restraint:
            return (
                "PHASE 2 (BURST DIRECT): Maitre des Ombres actif + Invisible (sans Retenue). "
                "Le premier sort offensif revele ET beneficie de +100% DI. "
                "Lancer directement le sort le plus puissant."
            )
        
        if self.shadow_master_active and not self.is_invisible:
            return (
                "PHASE 2 (BURST VISIBLE): Maitre des Ombres actif mais plus invisible. "
                "Lancer le sort de degats directs le plus puissant pour profiter du x2."
            )
        
        if self.is_invisible and not self.shadow_master_active:
            return (
                "TRANSITION: Invisible mais Maitre des Ombres pas encore actif. "
                "Se positionner dans le dos, preparer le terrain (pièges, PF)."
            )
        
        if self.is_apparent:
            return (
                f"COOLDOWN: Apparent ({self.apparent_turns} tour(s)). "
                "Impossibilite de relancer Invisibilite. "
                "Phase de degats normaux / pièges / double."
            )
        
        return "NEUTRE: Pas d'etat special. Invisibilite disponible si PW suffisants."
    
    def get_summary(self):
        """Retourne un resume de l'etat actuel pour le logging."""
        return {
            "invisible": self.is_invisible,
            "invisible_turns": self.invisible_turns,
            "apparent": self.is_apparent,
            "apparent_turns": self.apparent_turns,
            "shadow_master_ready": self.shadow_master_ready,
            "shadow_master_active": self.shadow_master_active,
            "mp_bonus_active": self.mp_bonus_turns > 0,
            "has_restraint": self.has_restraint,
            "stats": {
                "total_casts": self.total_invisibility_casts,
                "total_procs": self.total_shadow_master_procs,
                "total_reveals": self.total_reveals,
                "spells_while_invis": self.spells_cast_while_invisible,
            }
        }


# =============================================================================
# 3. FONCTIONS UTILITAIRES
# =============================================================================

def compute_invisibility_value(fighter_stats, remaining_ap, has_restraint=True):
    """
    Evalue si lancer Invisibilite est rentable ce tour.
    Utile pour l'IA greedy.
    
    L'invisibilite coute 2 PW et un tour de setup pour obtenir:
    - +100% DI au prochain sort direct (tour suivant)
    - +2 PM max pour le positionnement
    - Impossibilite d'etre cible
    
    La valeur depend de:
    - PW disponibles (cout d'opportunite: pieges, Entourloupe)
    - Degats potentiels au tour suivant avec +100% DI
    - Position actuelle (est-on deja dans le dos?)
    
    Args:
        fighter_stats: dict - stats du combattant
        remaining_ap: int - PA restants ce tour
        has_restraint: bool - passif Retenue equipe?
        
    Returns:
        float - score de valeur (0 = inutile, 100 = optimal)
    """
    score = 50.0  # base neutre
    
    # L'invisibilite ne coute pas de PA, donc pas de cout d'opportunite PA
    score += 10.0
    
    # PW: si on a beaucoup de PW, le cout est negligeable
    wp = fighter_stats.get("current_wp", 0)
    if wp >= 6:
        score += 15.0
    elif wp >= 4:
        score += 5.0
    elif wp < INVISIBILITY_WP_COST:
        return 0.0  # impossible
    
    # Retenue augmente enormement la valeur (permet de preparer avant burst)
    if has_restraint:
        score += 20.0
    
    # Si on a beaucoup de PA restants ce tour, on peut faire autre chose avant
    if remaining_ap >= 6:
        score += 5.0
    
    return min(100.0, max(0.0, score))


# =============================================================================
# TESTS
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("  TESTS ENGINE/INVISIBILITY.PY V5.0")
    print("=" * 60)
    
    # ----- Mock Fighter -----
    class MockFighter:
        def __init__(self, name, wp=8, mp=5):
            self.name = name
            self.current_wp = wp
            self.current_mp = mp
            self.max_mp_bonus = 0
    
    # ============================================
    # TEST 1: Creation et etat initial
    # ============================================
    print("\n--- TEST 1: Creation et etat initial ---")
    sram = MockFighter("L'Immortel", wp=8, mp=5)
    mgr = InvisibilityManager(sram, has_restraint=True)
    
    assert mgr.is_invisible == False
    assert mgr.is_apparent == False
    assert mgr.can_cast_invisibility == True
    assert mgr.has_shadow_master == False
    print(f"  {sram.name}: invisible={mgr.is_invisible}, "
          f"apparent={mgr.is_apparent}, peut_invi={mgr.can_cast_invisibility}")
    print("  -> OK: etat initial correct")
    
    # ============================================
    # TEST 2: Lancer Invisibilite
    # ============================================
    print("\n--- TEST 2: Lancer Invisibilite ---")
    result = mgr.cast_invisibility()
    
    assert result["success"] == True
    assert result["wp_cost"] == 2
    assert mgr.is_invisible == True
    assert mgr.invisible_turns == 2
    assert mgr.is_apparent == True
    assert mgr.apparent_turns == 3
    assert mgr.shadow_master_ready == True
    assert mgr.shadow_master_active == False
    assert sram.current_wp == 6
    assert sram.current_mp == 7  # 5 + 2 bonus
    
    print(f"  Resultat: {result}")
    print(f"  PW: 8 -> {sram.current_wp}, PM: 5 -> {sram.current_mp}")
    print(f"  Invisible: {mgr.invisible_turns} tours, Apparent: {mgr.apparent_turns} tours")
    print(f"  Maitre des Ombres: ready={mgr.shadow_master_ready}, active={mgr.shadow_master_active}")
    print("  -> OK")
    
    # ============================================
    # TEST 3: Impossibilite de relancer (Apparent)
    # ============================================
    print("\n--- TEST 3: Relancer Invisibilite (bloque par Apparent) ---")
    result2 = mgr.cast_invisibility()
    assert result2["success"] == False
    assert "Apparent" in result2.get("reason", "") or "Invisible" in result2.get("reason", "")
    print(f"  Tentative: {result2}")
    print("  -> OK: bloque correctement")
    
    # ============================================
    # TEST 4: Fin de tour (decrementation)
    # ============================================
    print("\n--- TEST 4: Fin du tour 1 (encore invisible) ---")
    changes = mgr.on_turn_end()
    print(f"  Invisible: {mgr.invisible_turns} tours, Apparent: {mgr.apparent_turns} tours")
    print(f"  MP bonus expire: {changes['mp_bonus_expired']}")
    assert mgr.invisible_turns == 1
    assert mgr.apparent_turns == 2
    assert changes["mp_bonus_expired"] == True  # le bonus PM ne dure qu'1 tour
    assert sram.current_mp == 5  # PM revenu a la normale
    print("  -> OK: decrementation correcte, bonus PM expire")
    
    # ============================================
    # TEST 5: Debut du tour 2 (Maitre des Ombres s'active)
    # ============================================
    print("\n--- TEST 5: Debut du tour 2 (Maitre des Ombres) ---")
    effects = mgr.on_turn_start()
    
    assert effects["shadow_master_activated"] == True
    assert mgr.shadow_master_active == True
    assert mgr.shadow_master_ready == False
    assert effects["invisible"] == True
    
    print(f"  Maitre des Ombres: active={mgr.shadow_master_active}")
    print(f"  Invisible: {mgr.invisible_turns} tour(s)")
    print(f"  Conseil: {mgr.get_optimal_rotation_advice()[:80]}...")
    print("  -> OK: Maitre des Ombres actif")
    
    # ============================================
    # TEST 6: Sort < 4 PA avec Retenue (reste invisible)
    # ============================================
    print("\n--- TEST 6: Sort 2 PA avec Retenue (reste invisible) ---")
    
    # Kleptosram 2PA - pas de degats directs pour ce test
    r6 = mgr.on_spell_cast(spell_ap_cost=2, is_direct_damage=True)
    
    print(f"  Sort 2PA: di_bonus={r6['di_bonus']}, revealed={r6['revealed']}, "
          f"shadow_master_consumed={r6['shadow_master_consumed']}")
    
    # Maitre des Ombres DEVRAIT etre consomme (c'est un sort de degats directs)
    assert r6["shadow_master_consumed"] == True
    assert r6["di_bonus"] == 100
    # MAIS avec Retenue, 2PA < 4PA -> reste invisible
    assert r6["revealed"] == False
    assert mgr.is_invisible == True
    
    print("  -> OK: +100% DI consomme, mais reste invisible (2PA < 4PA)")
    
    # ============================================
    # TEST 7: Sort >= 4 PA avec Retenue (revele)
    # ============================================
    print("\n--- TEST 7: Sort 4 PA avec Retenue (revele) ---")
    
    # Traumatisme 4PA
    r7 = mgr.on_spell_cast(spell_ap_cost=4, is_direct_damage=True)
    
    print(f"  Sort 4PA: di_bonus={r7['di_bonus']}, revealed={r7['revealed']}, "
          f"shadow_master_consumed={r7['shadow_master_consumed']}")
    
    # Maitre des Ombres deja consomme au test 6
    assert r7["shadow_master_consumed"] == False
    assert r7["di_bonus"] == 0
    # 4PA >= 4PA -> revele
    assert r7["revealed"] == True
    assert mgr.is_invisible == False
    
    print("  -> OK: invisible revele par sort >= 4PA")
    
    # ============================================
    # TEST 8: Sans Retenue (tout revele)
    # ============================================
    print("\n--- TEST 8: Sans Retenue (tout sort revele) ---")
    
    sram2 = MockFighter("Sram2", wp=8, mp=5)
    mgr2 = InvisibilityManager(sram2, has_restraint=False)
    
    mgr2.cast_invisibility()
    mgr2.on_turn_end()  # fin tour 1
    mgr2.on_turn_start()  # debut tour 2, Maitre des Ombres actif
    
    assert mgr2.is_invisible == True
    assert mgr2.shadow_master_active == True
    
    # Sort 2PA sans Retenue -> revele immediatement
    r8 = mgr2.on_spell_cast(spell_ap_cost=2, is_direct_damage=True)
    
    print(f"  Sort 2PA sans Retenue: di_bonus={r8['di_bonus']}, revealed={r8['revealed']}")
    assert r8["revealed"] == True
    assert r8["di_bonus"] == 100
    assert r8["shadow_master_consumed"] == True
    
    print("  -> OK: sans Retenue, tout sort offensif revele + Maitre des Ombres proc")
    
    # ============================================
    # TEST 9: Degats recus brisent l'invisibilite
    # ============================================
    print("\n--- TEST 9: Degats recus brisent l'invisibilite ---")
    
    sram3 = MockFighter("Sram3", wp=8, mp=5)
    mgr3 = InvisibilityManager(sram3, has_restraint=True)
    mgr3.cast_invisibility()
    
    assert mgr3.is_invisible == True
    broken = mgr3.on_damage_received(500)
    assert broken == True
    assert mgr3.is_invisible == False
    
    print(f"  500 degats recus -> invisible brise: {broken}")
    print("  -> OK")
    
    # ============================================
    # TEST 10: Cycle complet avec rotation optimale
    # ============================================
    print("\n--- TEST 10: Cycle complet (rotation optimale) ---")
    
    sram4 = MockFighter("Sram4", wp=8, mp=5)
    mgr4 = InvisibilityManager(sram4, has_restraint=True)
    
    print(f"  Tour 1: {mgr4.get_optimal_rotation_advice()[:60]}...")
    
    # Tour 1: Lancer Invisibilite
    mgr4.cast_invisibility()
    print(f"  -> Invisibilite lancee. PW={sram4.current_wp}, PM={sram4.current_mp}")
    
    # Fin tour 1
    mgr4.on_turn_end()
    
    # Tour 2: Maitre des Ombres s'active
    mgr4.on_turn_start()
    print(f"  Tour 2: {mgr4.get_optimal_rotation_advice()[:60]}...")
    
    # Lancer Kleptosram 2PA (dos) -> +5 PF, reste invisible, consomme MdO
    r10a = mgr4.on_spell_cast(spell_ap_cost=2, is_direct_damage=True)
    print(f"  Kleptosram 2PA: +{r10a['di_bonus']}% DI, revele={r10a['revealed']}")
    
    # Lancer Kleptosram 2PA (dos) -> pas de MdO (deja consomme)
    r10b = mgr4.on_spell_cast(spell_ap_cost=2, is_direct_damage=True)
    print(f"  Kleptosram 2PA: +{r10b['di_bonus']}% DI, revele={r10b['revealed']}")
    
    # Lancer Traumatisme 4PA -> revele
    r10c = mgr4.on_spell_cast(spell_ap_cost=4, is_direct_damage=True)
    print(f"  Traumatisme 4PA: +{r10c['di_bonus']}% DI, revele={r10c['revealed']}")
    
    assert r10a["di_bonus"] == 100 and r10a["revealed"] == False
    assert r10b["di_bonus"] == 0 and r10b["revealed"] == False
    assert r10c["di_bonus"] == 0 and r10c["revealed"] == True
    
    # Fin tour 2
    mgr4.on_turn_end()
    print(f"  Invisible: {mgr4.invisible_turns}, Apparent: {mgr4.apparent_turns}")
    
    # Tour 3: plus invisible, Apparent actif
    mgr4.on_turn_start()
    print(f"  Tour 3: {mgr4.get_optimal_rotation_advice()[:60]}...")
    assert mgr4.can_cast_invisibility == False  # encore Apparent
    
    mgr4.on_turn_end()
    
    # Tour 4: Apparent expire?
    mgr4.on_turn_start()
    print(f"  Tour 4: Apparent={mgr4.apparent_turns}, peut_invi={mgr4.can_cast_invisibility}")
    
    # Fin tour 4
    mgr4.on_turn_end()
    
    # Tour 5: Apparent devrait avoir expire
    mgr4.on_turn_start()
    print(f"  Tour 5: Apparent={mgr4.apparent_turns}, peut_invi={mgr4.can_cast_invisibility}")
    assert mgr4.can_cast_invisibility == True  # Apparent expire apres 3 tours
    
    print("  -> OK: cycle complet verifie")
    
    # ============================================
    # TEST 11: Statistiques
    # ============================================
    print("\n--- TEST 11: Resume et statistiques ---")
    summary = mgr4.get_summary()
    print(f"  Stats: {summary['stats']}")
    assert summary["stats"]["total_casts"] == 1
    assert summary["stats"]["total_procs"] == 1
    assert summary["stats"]["total_reveals"] == 1
    assert summary["stats"]["spells_while_invis"] == 3
    print("  -> OK")
    
    # ============================================
    # TEST 12: Valeur strategique
    # ============================================
    print("\n--- TEST 12: Evaluation strategique ---")
    
    val1 = compute_invisibility_value({"current_wp": 8}, remaining_ap=13, has_restraint=True)
    val2 = compute_invisibility_value({"current_wp": 8}, remaining_ap=13, has_restraint=False)
    val3 = compute_invisibility_value({"current_wp": 1}, remaining_ap=13, has_restraint=True)
    
    print(f"  WP=8, Retenue=True:  score={val1}")
    print(f"  WP=8, Retenue=False: score={val2}")
    print(f"  WP=1, Retenue=True:  score={val3} (PW insuffisants)")
    
    assert val1 > val2  # Retenue augmente la valeur
    assert val3 == 0.0  # pas assez de PW
    print("  -> OK")
    
    # ============================================
    # RESUME
    # ============================================
    print("\n" + "=" * 60)
    print("  TOUS LES TESTS PASSES - engine/invisibility.py V5.0")
    print("=" * 60)
    print(f"\n  Modules couverts:")
    print(f"    - Lancement d'Invisibilite (0 PA, 2 PW)")
    print(f"    - Etat Invisible (2 tours)")
    print(f"    - Etat Apparent (3 tours, anti-re-invi)")
    print(f"    - Maitre des Ombres (+100% DI tour suivant)")
    print(f"    - Passif Retenue (sort >= 4PA pour reveler)")
    print(f"    - Degats recus brisent l'invisibilite")
    print(f"    - Cycle complet: invi -> MdO -> burst -> cooldown")
    print(f"    - Bonus PM (+2, 1 tour)")
    print(f"    - Evaluation strategique pour IA")
    print(f"    - Source: patch 1.91 (fevrier 2026)")
