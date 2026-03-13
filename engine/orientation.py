# =============================================================================
# engine/orientation.py - V5.0
# Module d'orientation, tacle/esquive et portee
# =============================================================================
# Sources:
#   - MethodWakfu: https://methodwakfu.com/bien-debuter/informations-generales/
#   - WakfuCalc:   https://sites.google.com/view/wakfucalc/en/guides/formulas
#   - DESIGN_DOC.md sections 1.1-1.3, 2.6
# =============================================================================

import math
import logging
import sys
import os

# Ajouter la racine du projet au path pour les imports absolus
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from utils.logger import setup_logger
    logger = setup_logger("engine.orientation")
except ImportError:
    logger = logging.getLogger("engine.orientation")
    logging.basicConfig(level=logging.INFO)

import config

# =============================================================================
# 1. DIRECTIONS ET CONSTANTES
# =============================================================================

# Les 4 directions cardinales
# En Wakfu, "facing" = la direction ou regarde le combattant
# NORTH = vers y negatif (haut de la grille), SOUTH = vers y positif, etc.
DIRECTIONS = {
    "N": (0, -1),   # Nord = regarde vers le haut
    "S": (0, 1),    # Sud = regarde vers le bas
    "E": (1, 0),    # Est = regarde vers la droite
    "W": (-1, 0),   # Ouest = regarde vers la gauche
}

# Opposites pour calculer le dos
OPPOSITE_DIR = {"N": "S", "S": "N", "E": "W", "W": "E"}

# Multiplicateurs d'orientation pour les degats
# Source: WakfuCalc - "1 if facing you; 1.1 if side; 1.25 if back"
ORIENTATION_MULTIPLIERS = {
    "FRONT": config.ORIENTATION_FRONT,   # 1.0
    "SIDE": config.ORIENTATION_SIDE,     # 1.1
    "REAR": config.ORIENTATION_REAR,     # 1.25
}

# =============================================================================
# 2. CALCUL D'ORIENTATION
# =============================================================================

def get_direction_vector(from_pos, to_pos):
    """
    Retourne le vecteur direction normalise de from_pos vers to_pos.
    Utilise le composant dominant (Manhattan) pour determiner la direction cardinale.
    
    Args:
        from_pos: tuple (x, y) position source
        to_pos: tuple (x, y) position destination
        
    Returns:
        tuple (dx, dy) direction normalisee, ou (0, 0) si meme case
    """
    dx = to_pos[0] - from_pos[0]
    dy = to_pos[1] - from_pos[1]
    
    if dx == 0 and dy == 0:
        return (0, 0)
    
    # On prend le composant dominant
    if abs(dx) >= abs(dy):
        return (1 if dx > 0 else -1, 0)
    else:
        return (0, 1 if dy > 0 else -1)


def facing_to_vector(facing):
    """
    Convertit une direction cardinale (N/S/E/W) en vecteur.
    
    Args:
        facing: str - "N", "S", "E" ou "W"
        
    Returns:
        tuple (dx, dy)
    """
    return DIRECTIONS.get(facing, (0, -1))


def determine_orientation(attacker_pos, defender_pos, defender_facing):
    """
    Determine l'orientation de l'attaque par rapport au defenseur.
    
    Regle Wakfu (MethodWakfu section 2.2 / WakfuCalc):
    - Si l'attaquant est DERRIERE le defenseur (meme direction que le regard) -> DOS (REAR)
    - Si l'attaquant est DEVANT le defenseur (direction opposee au regard) -> FACE (FRONT) 
    - Sinon -> COTE (SIDE)
    
    En clair: le defenseur regarde vers "facing". Si l'attaquant est dans 
    cette direction, l'attaquant est DEVANT (face). Si l'attaquant est dans
    la direction opposee, il est dans le DOS.
    
    Args:
        attacker_pos: tuple (x, y) - position de l'attaquant
        defender_pos: tuple (x, y) - position du defenseur
        defender_facing: str - direction ou regarde le defenseur ("N","S","E","W")
        
    Returns:
        str - "FRONT", "SIDE" ou "REAR"
    """
    if attacker_pos == defender_pos:
        return "FRONT"  # Cas degenere (sort sur soi)
    
    # Vecteur du defenseur vers l'attaquant
    attack_dir = get_direction_vector(defender_pos, attacker_pos)
    
    # Direction ou regarde le defenseur
    face_vec = facing_to_vector(defender_facing)
    
    # Direction opposee = le dos du defenseur
    back_vec = (-face_vec[0], -face_vec[1])
    
    # Si l'attaquant vient de la meme direction que le regard du defenseur
    # -> l'attaquant est DEVANT (FRONT)
    if attack_dir == face_vec:
        result = "FRONT"
    # Si l'attaquant vient de la direction du dos
    # -> l'attaquant est dans le DOS (REAR)
    elif attack_dir == back_vec:
        result = "REAR"
    else:
        result = "SIDE"
    
    logger.debug(
        f"Orientation: attaquant{attacker_pos} -> defenseur{defender_pos} "
        f"(regarde {defender_facing}) = {result}"
    )
    return result


def get_orientation_multiplier(orientation):
    """
    Retourne le multiplicateur de degats pour une orientation donnee.
    
    Source WakfuCalc:
    - FRONT: x1.0
    - SIDE:  x1.1
    - REAR:  x1.25
    
    Args:
        orientation: str - "FRONT", "SIDE" ou "REAR"
        
    Returns:
        float - multiplicateur
    """
    return ORIENTATION_MULTIPLIERS.get(orientation, 1.0)


# =============================================================================
# 3. TACLE / ESQUIVE
# =============================================================================

def compute_combined_lock(lockers, target_pos):
    """
    Calcule le Tacle combine de tous les adversaires adjacents.
    
    Source WakfuCalc:
    L = La + Lb/2 + Lc/3 + Ld/4
    (La, Lb, Lc, Ld = Tacle des adversaires adjacents, tries par ordre decroissant)
    
    Args:
        lockers: list of dict - [{"lock": int, "pos": (x,y), "facing": str}, ...]
            Les adversaires adjacents a la cible (deja filtres)
        target_pos: tuple (x, y) - position de la cible qui esquive
        
    Returns:
        float - tacle combine L
    """
    if not lockers:
        return 0.0
    
    # Trier par tacle decroissant
    lock_values = sorted([l["lock"] for l in lockers], reverse=True)
    
    combined = 0.0
    for i, lock_val in enumerate(lock_values):
        combined += lock_val / (i + 1)
    
    logger.debug(f"Tacle combine: valeurs={lock_values}, L={combined:.2f}")
    return combined


def compute_orientation_factor(lockers, target_pos, target_facing):
    """
    Calcule le facteur d'orientation pour le tacle/esquive.
    
    Source WakfuCalc:
    - 0 si au moins un tacleur est FACE au defenseur (= le defenseur regarde
      vers le tacleur, donc le tacleur est devant)
    - 1 si au moins un tacleur est de COTE (et aucun de face)
    - 2 si TOUS les tacleurs sont dans le DOS du defenseur
    
    ATTENTION a la semantique: ici "face au defenseur" signifie que le tacleur 
    est dans la direction ou le defenseur regarde (FRONT). C'est le cas le plus 
    efficace pour le tacle.
    
    Source MethodWakfu section 2.6:
    - De face: perte max 4 PM + 4 PA (lvl 100+)
    - De cote: perte max 4 PM + 3 PA (-1 PA)
    - De dos: perte max 3 PM + 3 PA (-1 PM -1 PA)
    
    Args:
        lockers: list of dict avec "pos" et "facing"
        target_pos: tuple (x, y)
        target_facing: str - direction ou regarde la cible
        
    Returns:
        int - 0 (face, meilleur tacle), 1 (cote) ou 2 (dos, pire tacle)
    """
    has_side = False
    
    for locker in lockers:
        # Orientation du tacleur par rapport a la cible
        # = d'ou vient le tacleur vu par la cible
        orientation = determine_orientation(locker["pos"], target_pos, target_facing)
        
        if orientation == "FRONT":
            # Au moins un tacleur est devant la cible -> pire cas pour la cible
            logger.debug(f"Tacleur a {locker['pos']} est FACE -> facteur 0")
            return 0
        elif orientation == "SIDE":
            has_side = True
    
    if has_side:
        logger.debug("Au moins un tacleur de COTE -> facteur 1")
        return 1
    
    logger.debug("Tous les tacleurs de DOS -> facteur 2")
    return 2


def compute_dodge_losses(dodge, lockers, target_pos, target_facing, target_level):
    """
    Calcule les pertes de PM et PA lors d'une esquive de tacle.
    
    Source WakfuCalc (formule complete):
    L = La + Lb/2 + Lc/3 + Ld/4
    X = (7/3) * (L - Dodge) / (L + Dodge)   [L et Dodge >= 0]
    Y = floor((X + 1) * 4 * OrientationFactor)   [OrientationFactor: 0, 1, ou 2]
    
    ATTENTION: le facteur d'orientation de WakfuCalc est INVERSE par rapport
    a l'intuition:
    - 0 = tous les tacleurs sont de DOS (pire tacle pour eux)
    - 1 = au moins un de cote
    - 2 = au moins un de FACE (meilleur tacle)
    
    Correction: apres relecture de WakfuCalc, le facteur est:
    {2 si tous les tacleurs montrent leur dos a la cible;
     1 si au moins un montre son cote;
     0 si au moins un fait face a la cible}
     
    Mais "montrent leur dos a la cible" = la cible les voit de dos = 
    ils regardent DANS LA MEME DIRECTION que la cible = ils sont dans
    le dos de la cible. C'est le cas ou le tacle est le MOINS efficace.
    
    Donc facteur 2 = tacle le moins efficace (tacleurs de dos).
    Et facteur 0 = pas de perte (tacleurs de face = tacle inefficace??)
    
    NON. Relisons WakfuCalc attentivement:
    "Orientation factor = {2 if all the locking opponents are showing their 
    back to the target; 1 if at least one of the locking opponents is showing 
    their side to the target; 0 if at least one of the locking opponents is 
    facing the target}"
    
    "showing their back to the target" = le tacleur montre son dos a la cible
    = la cible voit le dos du tacleur. Cela veut dire que le tacleur regarde 
    LOIN de la cible. Le tacle est MOINS efficace de dos.
    
    Et MethodWakfu dit:
    - "Le Tacle est MOINS efficace lorsque le tacleur est de cote, et encore 
      moins efficace lorsqu'il est de dos"
    
    Donc la logique est:
    - Facteur 0 = au moins un tacleur FAIT FACE a la cible (meilleur tacle)
      -> Y = 0 toujours?? Non, ca fait Y = floor((X+1)*4*0) = 0. Pas de perte.
    
    PROBLEME: si facteur = 0 quand le tacleur fait face -> Y = 0 -> aucune perte.
    C'est l'INVERSE de ce que dit MethodWakfu.
    
    Resolution: WakfuCalc dit "facing the target" = le tacleur FAIT FACE a la cible.
    Cela signifie que le tacleur REGARDE VERS la cible. C'est la position la plus
    mena§ante. MAIS le facteur est 0, ce qui donne Y=0 = aucune perte.
    
    C'est FAUX d'apres MethodWakfu. Il y a une incoherence dans ma lecture.
    
    RELISONS une derniere fois WakfuCalc:
    "Orientation factor = {2 if all the locking opponents are showing their 
    back to the target}"
    
    "showing their back" = montrent leur dos. Si le tacleur montre son dos,
    il regarde DANS L'AUTRE DIRECTION. La cible voit son dos. C'est le cas 
    ou le tacle est le MOINS efficace.
    
    MAIS facteur = 2 donne le Y le plus GRAND = le plus de pertes.
    
    Conclusion: le facteur d'orientation dans la formule WakfuCalc mesure 
    l'efficacite du tacle du point de vue de la CIBLE QUI ESQUIVE, pas du tacleur.
    
    WAIT. Relisons MethodWakfu:
    "Le Tacle est MOINS efficace lorsque le tacleur est de cote"
    Ici "le tacleur est de cote" = l'orientation du tacleur par rapport a la 
    cible. Le tacleur montre son COTE a la cible.
    
    Et WakfuCalc dit: facteur 1 quand le tacleur montre son cote.
    facteur 2 quand le tacleur montre son dos (encore moins efficace).
    
    Avec facteur plus eleve = Y plus grand = PLUS de pertes PM/PA.
    
    C'est contradictoire avec "moins efficace" = moins de pertes.
    
    SAUF SI... le facteur n'est pas un simple multiplicateur de severite
    mais un facteur d'attenuation applique differemment.
    
    En fait, en relisant la formule EXACTE de WakfuCalc:
    Y = floor((X + 1) * 4 * OrientationFactor)
    
    Quand X est negatif (Dodge > Lock), (X+1) < 1, donc Y est petit.
    Quand X est positif (Lock > Dodge), (X+1) > 1, donc Y est grand.
    
    X va de -7/3 (Dodge >> Lock) a +7/3 (Lock >> Dodge).
    Donc (X+1) va de -4/3 a +10/3.
    
    Avec facteur 2 (dos): Y = floor((X+1)*4*2) = floor((X+1)*8)
    Avec facteur 0 (face): Y = floor((X+1)*4*0) = 0 toujours
    
    Donc facteur 0 = AUCUNE perte = tacle INEFFICACE.
    Et facteur 2 = pertes MAXIMALES = tacle EFFICACE.
    
    Mais WakfuCalc dit facteur 0 = "facing the target" et facteur 2 = "showing back".
    Et MethodWakfu dit "tacle MOINS efficace quand tacleur est de dos".
    
    CONTRADICTION RESOLUE:
    "facing the target" dans WakfuCalc = le tacleur fait face a la cible 
    = le tacleur regarde la cible = position optimale du tacleur.
    MAIS facteur 0 = aucune perte.
    
    C'est l'INVERSE de la realite du jeu. Donc soit WakfuCalc a une erreur
    dans le labelling, soit le facteur fonctionne autrement.
    
    SOLUTION DEFINITIVE apres reflexion:
    Le facteur d'orientation est du point de vue de la cible qui esquive.
    - Si le tacleur fait face a la cible: depuis la cible, le tacleur est 
      DEVANT elle. Pour s'echapper, la cible doit partir en arriere. C'est 
      le cas ou le tacle est le PLUS efficace (pertes max).
    - Si le tacleur montre son dos: la cible peut partir facilement.
    
    MAIS la formule dit facteur 0 pour "facing" et 2 pour "back".
    Facteur 0 -> Y=0 -> aucune perte -> tacle inefficace.
    Facteur 2 -> Y grand -> pertes -> tacle efficace.
    
    C'est INCOHERENT avec le jeu. MethodWakfu est clair:
    "De face: perte max 4 PM + 4 PA"
    "De dos: perte max 3 PM + 3 PA"
    
    Donc le facteur devrait etre INVERSE dans mon code:
    - Face du tacleur -> facteur 2 (pertes max)
    - Dos du tacleur -> facteur 0 ou reduit
    
    Je vais donc implementer selon MethodWakfu qui est plus clair,
    et utiliser des caps de perte max selon l'orientation.
    
    IMPLEMENTATION FINALE (basee sur MethodWakfu):
    On calcule Y avec facteur_orientation = 1 (neutre),
    puis on applique les caps de perte max selon l'orientation.
    
    Args:
        dodge: int - Esquive de la cible
        lockers: list of dict - [{"lock": int, "pos": (x,y), "facing": str}]
        target_pos: tuple (x, y)
        target_facing: str - direction ou regarde la cible
        target_level: int - niveau de la cible
        
    Returns:
        dict - {"mp_loss": int, "ap_loss": int, "orientation": str, 
                "combined_lock": float, "details": str}
    """
    if not lockers:
        return {
            "mp_loss": 0, "ap_loss": 0, "orientation": "NONE",
            "combined_lock": 0.0, "details": "Aucun tacleur adjacent"
        }
    
    # --- Caps selon le niveau (Source: MethodWakfu section 2.6) ---
    if target_level < 50:
        max_mp_face, max_ap_face = 2, 2
    elif target_level < 100:
        max_mp_face, max_ap_face = 3, 3
    else:
        max_mp_face, max_ap_face = 4, 4
    
    # --- Tacle combine ---
    L = compute_combined_lock(lockers, target_pos)
    
    # --- Seuils (Source: MethodWakfu) ---
    # Aucune perte si Esquive >= 1.95 * L (de face)
    # Perte max si L >= 2.5 * Esquive (de face)
    
    # Si L ou Dodge sont 0, on traite les cas limites
    effective_L = max(L, 0)
    effective_dodge = max(dodge, 0)
    
    # Eviter la division par zero
    if effective_L + effective_dodge == 0:
        return {
            "mp_loss": 0, "ap_loss": 0, "orientation": "NONE",
            "combined_lock": 0.0, "details": "Lock et Dodge a 0"
        }
    
    # --- Formule WakfuCalc ---
    # X = (7/3) * (L - Dodge) / (L + Dodge)
    X = (7.0 / 3.0) * (effective_L - effective_dodge) / (effective_L + effective_dodge)
    
    # --- Determiner la meilleure orientation du tacleur ---
    # On cherche quel tacleur a la meilleure position (face > cote > dos)
    best_orientation = "REAR"  # pire cas pour le tacleur
    for locker in lockers:
        # Comment la cible voit le tacleur
        # "Le tacleur montre sa face" = il regarde vers la cible
        # Du point de vue de la cible, le tacleur est devant elle
        
        # Direction du tacleur par rapport a la cible
        locker_dir = get_direction_vector(target_pos, locker["pos"])
        locker_face_vec = facing_to_vector(locker["facing"])
        locker_back_vec = (-locker_face_vec[0], -locker_face_vec[1])
        
        # Le tacleur fait-il face a la cible? (= regarde vers la cible)
        # Le vecteur du tacleur vers la cible
        tacleur_vers_cible = get_direction_vector(locker["pos"], target_pos)
        
        if tacleur_vers_cible == locker_face_vec:
            # Le tacleur regarde directement vers la cible -> FACE (meilleur tacle)
            best_orientation = "FRONT"
            break  # On ne peut pas faire mieux
        elif tacleur_vers_cible != locker_back_vec and best_orientation != "FRONT":
            # Le tacleur ne regarde ni vers ni loin de la cible -> COTE
            if best_orientation == "REAR":
                best_orientation = "SIDE"
    
    # --- Caps selon l'orientation du tacleur (Source: MethodWakfu) ---
    # Face: max_mp, max_ap (plein)
    # Cote: max_mp, max_ap - 1
    # Dos: max_mp - 1, max_ap - 1
    if best_orientation == "FRONT":
        cap_mp = max_mp_face
        cap_ap = max_ap_face
        # WakfuCalc: facteur effectif = le plus severe
        # On utilise un facteur de 1.0 (standard, pas d'attenuation)
        orientation_factor = 1.0
    elif best_orientation == "SIDE":
        cap_mp = max_mp_face
        cap_ap = max(max_ap_face - 1, 0)
        orientation_factor = 0.75  # Attenuation de cote
    else:  # REAR
        cap_mp = max(max_mp_face - 1, 0)
        cap_ap = max(max_ap_face - 1, 0)
        orientation_factor = 0.5  # Forte attenuation de dos
    
    # --- Calcul de Y avec attenuation d'orientation ---
    # Y de base (comme si de face)
    Y_raw = (X + 1) * 4 * 2  # facteur 2 = face (pertes max possibles)
    Y_adjusted = Y_raw * orientation_factor
    Y = max(0, math.floor(Y_adjusted))
    
    # --- Conversion Y -> pertes PM/PA ---
    # Source WakfuCalc: PM = ceil(Y/2), AP = floor(Y/2)
    mp_loss = min(math.ceil(Y / 2), cap_mp)
    ap_loss = min(math.floor(Y / 2), cap_ap)
    
    # Garantir que les pertes respectent l'ordre de gravite
    # (Source MethodWakfu: PM augmente toujours en premier)
    if mp_loss < ap_loss:
        ap_loss = mp_loss
    
    details = (
        f"L={L:.1f}, Dodge={dodge}, X={X:.3f}, "
        f"Y_raw={Y_raw:.1f}, Y_adj={Y_adjusted:.1f}, Y={Y}, "
        f"orientation_tacleur={best_orientation}, "
        f"caps=({cap_mp}PM,{cap_ap}PA)"
    )
    
    logger.info(
        f"Esquive: {details} -> perte {mp_loss}PM {ap_loss}PA"
    )
    
    return {
        "mp_loss": mp_loss,
        "ap_loss": ap_loss,
        "orientation": best_orientation,
        "combined_lock": L,
        "details": details
    }


# =============================================================================
# 4. UTILITAIRES DE PORTEE
# =============================================================================

def manhattan_distance(pos1, pos2):
    """Distance de Manhattan entre deux positions."""
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])


def is_in_range(caster_pos, target_pos, min_range, max_range, 
                castable_on_self=False, line_only=False, diagonal=False):
    """
    Verifie si une cible est a portee d'un sort.
    
    Source MethodWakfu section 2.1:
    - "lançable sur soi" est SEPARE de la portee min/max
    - Si retrait de PO, la portee min reste, mais "lançable sur soi" reste aussi
    
    Args:
        caster_pos: tuple (x, y)
        target_pos: tuple (x, y)
        min_range: int - portee minimum du sort
        max_range: int - portee maximum du sort
        castable_on_self: bool - le sort peut-il etre lance sur soi?
        line_only: bool - le sort doit-il etre lance en ligne?
        diagonal: bool - le sort peut-il etre lance en diagonale?
        
    Returns:
        bool
    """
    # Cas special: sort sur soi
    if caster_pos == target_pos:
        return castable_on_self
    
    dist = manhattan_distance(caster_pos, target_pos)
    
    # Verification de la portee
    if dist < min_range or dist > max_range:
        return False
    
    # Verification ligne droite
    if line_only:
        dx = target_pos[0] - caster_pos[0]
        dy = target_pos[1] - caster_pos[1]
        if diagonal:
            # Ligne ou diagonale
            if dx != 0 and dy != 0 and abs(dx) != abs(dy):
                return False
        else:
            # Ligne droite uniquement (horizontale ou verticale)
            if dx != 0 and dy != 0:
                return False
    
    return True


def is_melee(caster_pos, target_pos):
    """
    Determine si l'attaque est en melee (distance 1-2) ou a distance (3+).
    
    Source WakfuCalc:
    "Melee mastery if the target is 1 or 2 cells away from the caster, 
     OR distance mastery if the target is 3 cells away or more"
    
    Args:
        caster_pos: tuple (x, y)
        target_pos: tuple (x, y)
        
    Returns:
        bool - True si melee (1-2 cases), False si distance (3+)
    """
    return manhattan_distance(caster_pos, target_pos) <= 2


# =============================================================================
# 5. GESTION DE L'ORIENTATION EN COMBAT
# =============================================================================

def turn_to_face(fighter_pos, target_pos):
    """
    Calcule la nouvelle direction pour qu'un combattant fasse face a une cible.
    Utilise lors du lancement de sort ou du deplacement.
    
    Args:
        fighter_pos: tuple (x, y) - position du combattant
        target_pos: tuple (x, y) - position de la cible
        
    Returns:
        str - nouvelle direction ("N", "S", "E", "W") ou None si meme case
    """
    if fighter_pos == target_pos:
        return None
    
    direction_vec = get_direction_vector(fighter_pos, target_pos)
    
    # Trouver la direction cardinale correspondante
    for dir_name, dir_vec in DIRECTIONS.items():
        if direction_vec == dir_vec:
            return dir_name
    
    return None  # Ne devrait pas arriver


def auto_orient_on_cast(caster, target_pos):
    """
    Oriente automatiquement le lanceur vers sa cible lors du lancement d'un sort.
    C'est le comportement par defaut dans Wakfu.
    
    Args:
        caster: Fighter object (doit avoir .position et .facing)
        target_pos: tuple (x, y)
        
    Returns:
        str - ancienne direction (pour log)
    """
    if not hasattr(caster, 'position') or not hasattr(caster, 'facing'):
        logger.warning("auto_orient_on_cast: objet caster invalide")
        return None
    
    old_facing = caster.facing
    new_facing = turn_to_face(caster.position, target_pos)
    
    if new_facing and new_facing != old_facing:
        caster.facing = new_facing
        logger.debug(
            f"{caster.name} se tourne: {old_facing} -> {new_facing} "
            f"(vise {target_pos})"
        )
    
    return old_facing


def get_back_position(fighter_pos, fighter_facing):
    """
    Retourne la position derriere un combattant (pour le positionnement optimal).
    
    Args:
        fighter_pos: tuple (x, y)
        fighter_facing: str - "N", "S", "E", "W"
        
    Returns:
        tuple (x, y) - position dans le dos du combattant
    """
    opposite = OPPOSITE_DIR.get(fighter_facing, "S")
    back_vec = DIRECTIONS[opposite]
    return (fighter_pos[0] + back_vec[0], fighter_pos[1] + back_vec[1])


def get_side_positions(fighter_pos, fighter_facing):
    """
    Retourne les deux positions de cote d'un combattant.
    
    Args:
        fighter_pos: tuple (x, y)
        fighter_facing: str - "N", "S", "E", "W"
        
    Returns:
        list of tuple - les deux positions de cote
    """
    face_vec = facing_to_vector(fighter_facing)
    
    # Les cotes sont perpendiculaires au regard
    side1 = (fighter_pos[0] + face_vec[1], fighter_pos[1] + face_vec[0])
    side2 = (fighter_pos[0] - face_vec[1], fighter_pos[1] - face_vec[0])
    
    return [side1, side2]


# =============================================================================
# 6. FORCE DE VOLONTE - RETRAITS PA/PM
# =============================================================================

def compute_removal(base_removal, caster_fow, target_fow, rng_roll=None):
    """
    Calcule le retrait effectif de PA/PM en fonction de la Volonte.
    
    Source WakfuCalc:
    FF = (1 + CasterFoW/100) * (TargetFoW/100)  [borne 0-2]
    Effective = Base * 0.5 * FF
    Partie decimale = % chance d'arrondir vers le haut
    
    Source MethodWakfu section 2.7:
    - Max atteint si lanceur a +100 Volonte vs cible
    - A Volonte egale: moitie du retrait
    - Aucun retrait si cible a +100 Volonte vs lanceur
    - Lineaire entre ces points
    
    La cible gagne +10 Volonte par PA/PM retire (reset en fin de son tour).
    Les retraits PA max / PM max / PO ne sont PAS affectes par la Volonte.
    
    Args:
        base_removal: int - retrait de base du sort
        caster_fow: int - Volonte du lanceur
        target_fow: int - Volonte de la cible
        rng_roll: float or None - valeur 0-1 pour le tirage (None = retourne esperance)
        
    Returns:
        dict - {"removal": int, "probability_up": float, "expected": float, "ff": float}
    """
    # Calcul du facteur de Volonte
    # Source MethodWakfu section 2.7 (formule lineaire):
    #   - Difference = CasterFoW - TargetFoW
    #   - A difference 0 (egal): 50% du retrait
    #   - A difference +100 (lanceur domine): 100% du retrait
    #   - A difference -100 (cible domine): 0% du retrait
    #   - Lineaire entre ces points
    # FF = (difference + 100) / 200, borne [0, 1]
    difference = caster_fow - target_fow
    ff = (difference + 100) / 200.0
    ff = max(0.0, min(1.0, ff))
    
    # Retrait effectif = base * FF (pas de facteur 0.5, FF est deja entre 0 et 1)
    effective = base_removal * ff
    
    # Partie entiere et probabilite d'arrondir
    removal_floor = math.floor(effective)
    probability_up = effective - removal_floor
    
    # Si on a un tirage, on determine le resultat
    if rng_roll is not None:
        final_removal = removal_floor + (1 if rng_roll < probability_up else 0)
    else:
        final_removal = None
    
    result = {
        "removal": final_removal if final_removal is not None else removal_floor,
        "probability_up": round(probability_up, 4),
        "expected": round(effective, 4),
        "ff": round(ff, 4),
    }
    
    logger.debug(
        f"Retrait: base={base_removal}, FoW lanceur={caster_fow}, "
        f"FoW cible={target_fow}, FF={ff:.4f}, effectif={effective:.2f}, "
        f"resultat={result['removal']}"
    )
    
    return result


# =============================================================================
# 7. STABILISE / DESTABILISE
# =============================================================================

def can_be_displaced(fighter):
    """
    Verifie si un combattant peut etre deplace (pousse, attire, teleporte, echange).
    
    Source MethodWakfu section 2.8:
    Stabilise empeche: poussee, attraction, charge, teleportation, echange de place,
    changement d'orientation par sort.
    Seule la marche est autorisee.
    
    Args:
        fighter: Fighter object (doit avoir .states)
        
    Returns:
        bool - True si le combattant peut etre deplace
    """
    if hasattr(fighter, 'states'):
        for state in fighter.states:
            if state.get("name", "").lower() == "stabilise":
                return False
    return True


def apply_stabilized(caster, target, team_source="enemy"):
    """
    Applique l'etat Stabilise et le Destabilise correspondant.
    
    Source MethodWakfu section 2.8:
    - Stabilise empeche tous les deplacements sauf la marche
    - Applique aussi Destabilise (empeche d'etre re-Stabilise par la meme equipe, 3 tours)
    - Les Destabilises sont independants (allies vs ennemis)
    
    Args:
        caster: Fighter - celui qui stabilise
        target: Fighter - celui qui est stabilise
        team_source: str - "ally" ou "enemy"
        
    Returns:
        bool - True si l'application a reussi
    """
    if not hasattr(target, 'states'):
        return False
    
    # Verifier si la cible a deja Destabilise de cette source
    destab_name = f"destabilise_{team_source}"
    for state in target.states:
        if state.get("name", "").lower() == destab_name:
            logger.info(
                f"{target.name} a deja {destab_name}, "
                f"Stabilise impossible de cette source"
            )
            return False
    
    # Appliquer Stabilise
    target.states.append({
        "name": "stabilise",
        "duration": 1,
        "source": caster.name if hasattr(caster, 'name') else "unknown"
    })
    
    # Appliquer Destabilise (3 tours)
    target.states.append({
        "name": destab_name,
        "duration": 3,
        "source": caster.name if hasattr(caster, 'name') else "unknown"
    })
    
    logger.info(
        f"{target.name} est Stabilise par {caster.name if hasattr(caster, 'name') else '???'} "
        f"(source: {team_source}). Destabilise_{team_source} applique pour 3 tours."
    )
    
    return True


# =============================================================================
# TESTS
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("  TESTS ENGINE/ORIENTATION.PY V5.0")
    print("=" * 60)
    
    # ============================================
    # TEST 1: Orientation basique
    # ============================================
    print("\n--- TEST 1: Orientation basique ---")
    
    # Defenseur en (5,5) regarde vers le Nord (y negatif)
    # Attaquant en (5,4) = au nord du defenseur = DEVANT lui
    o1 = determine_orientation((5, 4), (5, 5), "N")
    print(f"  Attaquant(5,4) vs Defenseur(5,5) facing N: {o1}")
    assert o1 == "FRONT", f"Attendu FRONT, obtenu {o1}"
    
    # Attaquant en (5,6) = au sud du defenseur = dans son DOS
    o2 = determine_orientation((5, 6), (5, 5), "N")
    print(f"  Attaquant(5,6) vs Defenseur(5,5) facing N: {o2}")
    assert o2 == "REAR", f"Attendu REAR, obtenu {o2}"
    
    # Attaquant en (6,5) = a l'est du defenseur = COTE
    o3 = determine_orientation((6, 5), (5, 5), "N")
    print(f"  Attaquant(6,5) vs Defenseur(5,5) facing N: {o3}")
    assert o3 == "SIDE", f"Attendu SIDE, obtenu {o3}"
    
    # Attaquant en (4,5) = a l'ouest du defenseur = COTE
    o4 = determine_orientation((4, 5), (5, 5), "N")
    print(f"  Attaquant(4,5) vs Defenseur(5,5) facing N: {o4}")
    assert o4 == "SIDE", f"Attendu SIDE, obtenu {o4}"
    
    print("  -> OK: Face, Dos, Cote gauche, Cote droit")
    
    # ============================================
    # TEST 2: Multiplicateurs
    # ============================================
    print("\n--- TEST 2: Multiplicateurs d'orientation ---")
    
    m_front = get_orientation_multiplier("FRONT")
    m_side = get_orientation_multiplier("SIDE")
    m_rear = get_orientation_multiplier("REAR")
    
    print(f"  FRONT: x{m_front}")
    print(f"  SIDE:  x{m_side}")
    print(f"  REAR:  x{m_rear}")
    
    assert m_front == 1.0
    assert m_side == 1.1
    assert m_rear == 1.25
    print("  -> OK")
    
    # ============================================
    # TEST 3: Portee et melee/distance
    # ============================================
    print("\n--- TEST 3: Portee et melee/distance ---")
    
    # Sort 1-4, ligne de vue, pas sur soi
    assert is_in_range((5, 5), (5, 5), 1, 4, castable_on_self=False) == False
    assert is_in_range((5, 5), (5, 5), 1, 4, castable_on_self=True) == True
    assert is_in_range((5, 5), (5, 3), 1, 4) == True  # dist 2
    assert is_in_range((5, 5), (5, 0), 1, 4) == False  # dist 5, hors portee
    assert is_in_range((5, 5), (5, 3), 1, 4, line_only=True) == True  # en ligne
    assert is_in_range((5, 5), (6, 3), 1, 4, line_only=True) == False  # pas en ligne
    
    print(f"  Portee 1-4: sur soi=False (non-castable), sur soi=True (castable)")
    print(f"  Dist 2: OK, Dist 5: hors portee, Ligne: OK/Refuse")
    
    # Melee vs distance
    assert is_melee((5, 5), (5, 4)) == True   # dist 1 = melee
    assert is_melee((5, 5), (5, 3)) == True   # dist 2 = melee
    assert is_melee((5, 5), (5, 2)) == False  # dist 3 = distance
    assert is_melee((5, 5), (5, 1)) == False  # dist 4 = distance
    
    print(f"  Melee: dist 1-2 = True, dist 3+ = False")
    print("  -> OK")
    
    # ============================================
    # TEST 4: Tacle / Esquive
    # ============================================
    print("\n--- TEST 4: Tacle / Esquive ---")
    
    # Cas 1: un seul tacleur de face, Lock 200 vs Dodge 100
    lockers_face = [{"lock": 200, "pos": (5, 4), "facing": "S"}]
    # Le tacleur est en (5,4), regarde vers le Sud (vers la cible en 5,5)
    # -> Le tacleur FAIT FACE a la cible = meilleur tacle
    result1 = compute_dodge_losses(
        dodge=100, lockers=lockers_face,
        target_pos=(5, 5), target_facing="N", target_level=179
    )
    print(f"  Lock 200 vs Dodge 100 (face, lvl 179):")
    print(f"    Perte: {result1['mp_loss']} PM, {result1['ap_loss']} PA")
    print(f"    Details: {result1['details']}")
    
    # Cas 2: meme chose mais tacleur de dos
    lockers_back = [{"lock": 200, "pos": (5, 4), "facing": "N"}]
    # Le tacleur regarde vers le Nord (loin de la cible) -> il montre son DOS
    result2 = compute_dodge_losses(
        dodge=100, lockers=lockers_back,
        target_pos=(5, 5), target_facing="N", target_level=179
    )
    print(f"  Lock 200 vs Dodge 100 (dos, lvl 179):")
    print(f"    Perte: {result2['mp_loss']} PM, {result2['ap_loss']} PA")
    print(f"    Details: {result2['details']}")
    
    # Le tacle de face doit donner plus de pertes que de dos
    assert result1["mp_loss"] >= result2["mp_loss"], \
        f"Face devrait donner >= pertes PM que dos ({result1['mp_loss']} vs {result2['mp_loss']})"
    print(f"  -> OK: face ({result1['mp_loss']}PM) >= dos ({result2['mp_loss']}PM)")
    
    # Cas 3: Esquive >> Lock (aucune perte)
    lockers_weak = [{"lock": 50, "pos": (5, 4), "facing": "S"}]
    result3 = compute_dodge_losses(
        dodge=500, lockers=lockers_weak,
        target_pos=(5, 5), target_facing="N", target_level=179
    )
    print(f"  Lock 50 vs Dodge 500 (face):")
    print(f"    Perte: {result3['mp_loss']} PM, {result3['ap_loss']} PA")
    assert result3["mp_loss"] == 0 and result3["ap_loss"] == 0
    print("  -> OK: aucune perte (Esquive dominante)")
    
    # Cas 4: deux tacleurs
    lockers_two = [
        {"lock": 200, "pos": (5, 4), "facing": "S"},
        {"lock": 150, "pos": (6, 5), "facing": "W"},
    ]
    result4 = compute_dodge_losses(
        dodge=100, lockers=lockers_two,
        target_pos=(5, 5), target_facing="N", target_level=179
    )
    L_expected = 200 + 150 / 2  # 275
    print(f"  Deux tacleurs (200+150): L={result4['combined_lock']:.1f} (attendu ~{L_expected:.1f})")
    print(f"    Perte: {result4['mp_loss']} PM, {result4['ap_loss']} PA")
    
    # ============================================
    # TEST 5: Volonte et retraits
    # ============================================
    print("\n--- TEST 5: Volonte et retraits PA/PM ---")
    
    # Volonte egale: moitie du retrait
    r1 = compute_removal(base_removal=4, caster_fow=50, target_fow=50)
    print(f"  Retrait 4PM, FoW egal (50 vs 50): effectif={r1['expected']}, FF={r1['ff']}")
    assert abs(r1['expected'] - 2.0) < 0.01, f"Attendu ~2.0, obtenu {r1['expected']}"
    
    # Lanceur +100 FoW: retrait max
    r2 = compute_removal(base_removal=4, caster_fow=100, target_fow=0)
    print(f"  Retrait 4PM, FoW 100 vs 0: effectif={r2['expected']}, FF={r2['ff']}")
    assert abs(r2['expected'] - 4.0) < 0.01, f"Attendu ~4.0, obtenu {r2['expected']}"
    
    # Cible +100 FoW: aucun retrait
    r3 = compute_removal(base_removal=4, caster_fow=0, target_fow=100)
    print(f"  Retrait 4PM, FoW 0 vs 100: effectif={r3['expected']}, FF={r3['ff']}")
    assert abs(r3['expected'] - 0.0) < 0.01, f"Attendu ~0.0, obtenu {r3['expected']}"
    
    # Avec tirage aleatoire
    # FoW 75 vs 25: diff=50, FF=150/200=0.75, retrait=2*0.75=1.5
    # floor=1, proba_up=0.5, roll=0.3 < 0.5 -> arrondi vers le haut -> retrait=2
    r4 = compute_removal(base_removal=2, caster_fow=75, target_fow=25, rng_roll=0.3)
    print(f"  Retrait 2PM, FoW 75 vs 25, roll=0.3: retrait={r4['removal']}, "
          f"proba_up={r4['probability_up']}, expected={r4['expected']}")
    assert abs(r4['expected'] - 1.5) < 0.01, f"Attendu ~1.5, obtenu {r4['expected']}"
    assert r4['removal'] == 2, f"Attendu retrait=2 (roll 0.3 < proba 0.5), obtenu {r4['removal']}"
    
    print("  -> OK")
    
    # ============================================
    # TEST 6: Orientation automatique
    # ============================================
    print("\n--- TEST 6: Orientation automatique ---")
    
    class MockFighter:
        def __init__(self, name, pos, facing):
            self.name = name
            self.position = pos
            self.facing = facing
    
    sram = MockFighter("Sram", (5, 5), "N")
    print(f"  Sram a (5,5) regarde {sram.facing}")
    
    old = auto_orient_on_cast(sram, (5, 3))
    print(f"  Lance sort vers (5,3): old={old}, new={sram.facing}")
    assert sram.facing == "N"  # (5,3) est au nord, deja face au nord
    
    old = auto_orient_on_cast(sram, (7, 5))
    print(f"  Lance sort vers (7,5): old={old}, new={sram.facing}")
    assert sram.facing == "E"  # (7,5) est a l'est
    
    old = auto_orient_on_cast(sram, (5, 8))
    print(f"  Lance sort vers (5,8): old={old}, new={sram.facing}")
    assert sram.facing == "S"  # (5,8) est au sud
    
    print("  -> OK: auto-orientation fonctionne")
    
    # ============================================
    # TEST 7: Positions dos/cote
    # ============================================
    print("\n--- TEST 7: Positions dos et cote ---")
    
    back = get_back_position((5, 5), "N")
    print(f"  Dos de (5,5) facing N: {back}")
    assert back == (5, 6)  # Le dos du Nord est au Sud
    
    sides = get_side_positions((5, 5), "N")
    print(f"  Cotes de (5,5) facing N: {sides}")
    assert (4, 5) in sides or (6, 5) in sides
    
    back_e = get_back_position((5, 5), "E")
    print(f"  Dos de (5,5) facing E: {back_e}")
    assert back_e == (4, 5)  # Le dos de l'Est est a l'Ouest
    
    print("  -> OK")
    
    # ============================================
    # TEST 8: Stabilise / Destabilise
    # ============================================
    print("\n--- TEST 8: Stabilise / Destabilise ---")
    
    class MockFighter2:
        def __init__(self, name):
            self.name = name
            self.states = []
    
    caster = MockFighter2("Sram")
    target = MockFighter2("Bouftou")
    
    # Premiere application: OK
    ok1 = apply_stabilized(caster, target, "enemy")
    print(f"  Premier Stabilise (enemy): {ok1}")
    assert ok1 == True
    assert can_be_displaced(target) == False
    print(f"  Peut etre deplace? {can_be_displaced(target)}")
    
    # Deuxieme application par la meme equipe: refuse (Destabilise)
    ok2 = apply_stabilized(caster, target, "enemy")
    print(f"  Deuxieme Stabilise (enemy): {ok2}")
    assert ok2 == False
    
    # Application par l'autre equipe: OK
    ally_caster = MockFighter2("Eni")
    ok3 = apply_stabilized(ally_caster, target, "ally")
    print(f"  Stabilise par allie: {ok3}")
    assert ok3 == True
    
    print("  -> OK: Stabilise/Destabilise correct")
    
    # ============================================
    # RESUME
    # ============================================
    print("\n" + "=" * 60)
    print("  TOUS LES TESTS PASSES - engine/orientation.py V5.0")
    print("=" * 60)
    print(f"\n  Modules couverts:")
    print(f"    - Orientation (FRONT/SIDE/REAR)")
    print(f"    - Multiplicateurs de degats (x1.0 / x1.1 / x1.25)")
    print(f"    - Portee et melee/distance")
    print(f"    - Tacle/Esquive (formule WakfuCalc + caps MethodWakfu)")
    print(f"    - Volonte et retraits PA/PM")
    print(f"    - Orientation automatique au lancement de sort")
    print(f"    - Positions dos/cote")
    print(f"    - Stabilise/Destabilise")


