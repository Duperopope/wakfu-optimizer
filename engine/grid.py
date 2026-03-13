"""
engine/grid.py - Grille de combat WAKFU
Version 5.0

Gere le terrain 2D, le placement des combattants, la ligne de vue,
le pathfinding et les distances.

La grille est un systeme de coordonnees (x, y) ou chaque case peut contenir:
  - EMPTY: case vide, traversable
  - OBSTACLE: bloque mouvement ET ligne de vue
  - HOLE: infranchissable sauf teleportation
  - FIGHTER: occupee par un combattant (bloque mouvement, peut bloquer LdV)
  - TRAP: piege pose (traversable, declenche un effet)
  - GLYPH: zone d'effet persistante (traversable)
  - MECHANISM: mecanisme de donjon (variable)

Sources:
  - DESIGN_DOC.md sections 1.1, 1.2, 1.3
  - MethodWakfu: https://methodwakfu.com/bien-debuter/informations-generales/
"""

import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.logger import setup_logger

logger = setup_logger(__name__)


# ============================================================
# TYPES DE CASES
# ============================================================

CELL_EMPTY = "empty"
CELL_OBSTACLE = "obstacle"
CELL_HOLE = "hole"
CELL_MECHANISM = "mechanism"


class Cell:
    """Represente une case de la grille."""

    def __init__(self, x, y, cell_type=CELL_EMPTY):
        self.x = x
        self.y = y
        self.cell_type = cell_type
        self.fighter_id = None
        self.traps = []
        self.glyphs = []
        self.effects = []

    @property
    def is_walkable(self):
        """La case peut etre traversee a pied."""
        return (self.cell_type == CELL_EMPTY
                and self.fighter_id is None)

    @property
    def is_teleportable(self):
        """La case peut recevoir une teleportation (tout sauf obstacle et occupee)."""
        return (self.cell_type != CELL_OBSTACLE
                and self.fighter_id is None)

    @property
    def blocks_los(self):
        """La case bloque la ligne de vue."""
        return self.cell_type == CELL_OBSTACLE

    def __repr__(self):
        content = self.cell_type[0].upper()
        if self.fighter_id:
            content = "F"
        if self.traps:
            content = "T"
        return content


# ============================================================
# GRILLE DE COMBAT
# ============================================================

class Grid:
    """Grille 2D de combat.

    Utilise un dictionnaire (x,y)->Cell plutot qu'un tableau 2D
    pour supporter des formes de terrain variables (non rectangulaires).
    """

    def __init__(self, width=20, height=20, default_type=CELL_EMPTY):
        """Cree une grille rectangulaire de base.
        Pour les donjons avec formes speciales, utiliser add_cell/remove_cell.
        """
        self.cells = {}
        self.width = width
        self.height = height
        self._fighter_positions = {}

        for x in range(width):
            for y in range(height):
                self.cells[(x, y)] = Cell(x, y, default_type)

        logger.info(f"Grille creee: {width}x{height} ({len(self.cells)} cases)")

    def get_cell(self, x, y):
        """Retourne la cellule a (x,y) ou None si hors grille."""
        return self.cells.get((x, y))

    def is_valid(self, x, y):
        """Verifie si (x,y) est dans la grille."""
        return (x, y) in self.cells

    def is_walkable(self, x, y):
        """Verifie si (x,y) est traversable a pied."""
        cell = self.get_cell(x, y)
        return cell is not None and cell.is_walkable

    def is_teleportable(self, x, y):
        """Verifie si (x,y) peut recevoir une teleportation."""
        cell = self.get_cell(x, y)
        return cell is not None and cell.is_teleportable

    # --------------------------------------------------------
    # MODIFICATION DU TERRAIN
    # --------------------------------------------------------

    def set_cell_type(self, x, y, cell_type):
        """Change le type d'une case."""
        cell = self.get_cell(x, y)
        if cell:
            cell.cell_type = cell_type
            return True
        return False

    def add_cell(self, x, y, cell_type=CELL_EMPTY):
        """Ajoute une case (pour terrains non rectangulaires)."""
        self.cells[(x, y)] = Cell(x, y, cell_type)

    def remove_cell(self, x, y):
        """Retire une case de la grille."""
        if (x, y) in self.cells:
            del self.cells[(x, y)]

    # --------------------------------------------------------
    # PLACEMENT DES COMBATTANTS
    # --------------------------------------------------------

    def place_fighter(self, fighter, x, y):
        """Place un combattant sur la grille.
        Retourne True si OK, False si case invalide/occupee.
        """
        cell = self.get_cell(x, y)
        if cell is None:
            logger.warning(f"  Place {fighter.name}: ({x},{y}) hors grille")
            return False
        if cell.fighter_id is not None:
            logger.warning(f"  Place {fighter.name}: ({x},{y}) deja occupee")
            return False
        if cell.cell_type in (CELL_OBSTACLE, CELL_HOLE):
            logger.warning(f"  Place {fighter.name}: ({x},{y}) est {cell.cell_type}")
            return False

        if fighter.id in self._fighter_positions:
            old_x, old_y = self._fighter_positions[fighter.id]
            old_cell = self.get_cell(old_x, old_y)
            if old_cell:
                old_cell.fighter_id = None

        cell.fighter_id = fighter.id
        self._fighter_positions[fighter.id] = (x, y)
        fighter.x = x
        fighter.y = y

        logger.debug(f"  {fighter.name} place en ({x},{y})")
        return True

    def move_fighter(self, fighter, new_x, new_y):
        """Deplace un combattant vers une nouvelle position.
        Ne verifie PAS le chemin (utiliser get_path pour ca).
        """
        return self.place_fighter(fighter, new_x, new_y)

    def remove_fighter(self, fighter):
        """Retire un combattant de la grille (mort, desincarne)."""
        if fighter.id in self._fighter_positions:
            x, y = self._fighter_positions[fighter.id]
            cell = self.get_cell(x, y)
            if cell:
                cell.fighter_id = None
            del self._fighter_positions[fighter.id]

    def get_fighter_position(self, fighter):
        """Retourne (x,y) du combattant ou None."""
        return self._fighter_positions.get(fighter.id)

    def swap_fighters(self, fighter_a, fighter_b):
        """Echange les positions de deux combattants (Entourloupe, etc.)."""
        pos_a = self._fighter_positions.get(fighter_a.id)
        pos_b = self._fighter_positions.get(fighter_b.id)
        if pos_a is None or pos_b is None:
            return False

        cell_a = self.get_cell(*pos_a)
        cell_b = self.get_cell(*pos_b)

        cell_a.fighter_id = fighter_b.id
        cell_b.fighter_id = fighter_a.id
        self._fighter_positions[fighter_a.id] = pos_b
        self._fighter_positions[fighter_b.id] = pos_a
        fighter_a.x, fighter_a.y = pos_b
        fighter_b.x, fighter_b.y = pos_a

        logger.info(f"  Swap: {fighter_a.name} ({pos_a}->{pos_b}) <-> {fighter_b.name} ({pos_b}->{pos_a})")
        return True

    # --------------------------------------------------------
    # DISTANCE ET VOISINS
    # --------------------------------------------------------

    @staticmethod
    def manhattan_distance(x1, y1, x2, y2):
        """Distance de Manhattan entre deux points."""
        return abs(x1 - x2) + abs(y1 - y2)

    def get_neighbors(self, x, y, include_diagonals=False):
        """Retourne les cases adjacentes valides."""
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        if include_diagonals:
            directions += [(-1, -1), (-1, 1), (1, -1), (1, 1)]

        neighbors = []
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if self.is_valid(nx, ny):
                neighbors.append((nx, ny))
        return neighbors

    def get_adjacent_fighters(self, x, y, fighter_list):
        """Retourne les combattants vivants adjacents a (x,y)."""
        adjacent = []
        for f in fighter_list:
            if f.is_alive and self.manhattan_distance(x, y, f.x, f.y) == 1:
                adjacent.append(f)
        return adjacent

    def get_cells_in_range(self, x, y, min_range, max_range, line_only=False):
        """Retourne toutes les cases a portee (distance de Manhattan).
        Si line_only: seulement les 4 lignes droites.
        """
        cells = []
        if line_only:
            for direction in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
                for dist in range(min_range, max_range + 1):
                    nx = x + direction[0] * dist
                    ny = y + direction[1] * dist
                    if self.is_valid(nx, ny):
                        cells.append((nx, ny))
        else:
            for cx, cy in self.cells:
                d = self.manhattan_distance(x, y, cx, cy)
                if min_range <= d <= max_range:
                    cells.append((cx, cy))
        return cells

    # --------------------------------------------------------
    # LIGNE DE VUE (LdV)
    # --------------------------------------------------------

    def has_line_of_sight(self, x1, y1, x2, y2, ignore_fighters=False):
        """Verifie la ligne de vue entre (x1,y1) et (x2,y2).
        Utilise l'algorithme de Bresenham pour tracer la ligne.

        Bloquee par:
          - Obstacles (toujours)
          - Combattants (sauf si ignore_fighters=True)
        Les combattants Invisibles ne bloquent PAS la LdV.

        Source: DESIGN_DOC.md section 1.2
        """
        if x1 == x2 and y1 == y2:
            return True

        points = self._bresenham(x1, y1, x2, y2)

        for px, py in points[1:-1]:
            cell = self.get_cell(px, py)
            if cell is None:
                return False
            if cell.blocks_los:
                return False
            if not ignore_fighters and cell.fighter_id is not None:
                return False

        return True

    @staticmethod
    def _bresenham(x1, y1, x2, y2):
        """Algorithme de Bresenham pour tracer une ligne entre deux points.
        Retourne la liste des points (x,y) de la ligne.
        """
        points = []
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy

        cx, cy = x1, y1
        while True:
            points.append((cx, cy))
            if cx == x2 and cy == y2:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                cx += sx
            if e2 < dx:
                err += dx
                cy += sy
        return points

    # --------------------------------------------------------
    # PATHFINDING (BFS simple)
    # --------------------------------------------------------

    def get_path(self, start_x, start_y, end_x, end_y, max_distance=None):
        """Trouve le chemin le plus court (BFS) entre deux points.
        Respecte les obstacles et les combattants (pas traversables).
        Retourne la liste des cases du chemin (excluant le depart),
        ou None si aucun chemin.
        """
        if not self.is_valid(start_x, start_y) or not self.is_valid(end_x, end_y):
            return None

        if start_x == end_x and start_y == end_y:
            return []

        from collections import deque
        queue = deque()
        queue.append((start_x, start_y, []))
        visited = {(start_x, start_y)}

        while queue:
            cx, cy, path = queue.popleft()

            if max_distance is not None and len(path) >= max_distance:
                continue

            for nx, ny in self.get_neighbors(cx, cy):
                if (nx, ny) in visited:
                    continue

                if nx == end_x and ny == end_y:
                    return path + [(nx, ny)]

                if not self.is_walkable(nx, ny):
                    continue

                visited.add((nx, ny))
                queue.append((nx, ny, path + [(nx, ny)]))

        return None

    def get_reachable_cells(self, start_x, start_y, max_pm):
        """Retourne toutes les cases atteignables avec max_pm PM.
        Utilise BFS. Utile pour l'IA.
        """
        from collections import deque
        reachable = {}
        queue = deque()
        queue.append((start_x, start_y, 0))
        visited = {(start_x, start_y)}
        reachable[(start_x, start_y)] = 0

        while queue:
            cx, cy, cost = queue.popleft()
            if cost >= max_pm:
                continue
            for nx, ny in self.get_neighbors(cx, cy):
                if (nx, ny) in visited:
                    continue
                if not self.is_walkable(nx, ny):
                    continue
                visited.add((nx, ny))
                new_cost = cost + 1
                reachable[(nx, ny)] = new_cost
                queue.append((nx, ny, new_cost))

        return reachable

    # --------------------------------------------------------
    # PIEGES
    # --------------------------------------------------------

    def place_trap(self, x, y, trap_data):
        """Place un piege sur une case."""
        cell = self.get_cell(x, y)
        if cell is None:
            return False
        cell.traps.append(trap_data)
        logger.debug(f"  Piege place en ({x},{y}): {trap_data.get('name', '?')}")
        return True

    def remove_trap(self, x, y, trap_index=0):
        """Retire un piege d'une case."""
        cell = self.get_cell(x, y)
        if cell and cell.traps and trap_index < len(cell.traps):
            removed = cell.traps.pop(trap_index)
            return removed
        return None

    def get_traps_at(self, x, y):
        """Retourne les pieges sur une case."""
        cell = self.get_cell(x, y)
        if cell:
            return cell.traps
        return []

    # --------------------------------------------------------
    # AFFICHAGE (DEBUG)
    # --------------------------------------------------------

    def render(self, fighters=None):
        """Affiche la grille en ASCII pour le debug.
        . = vide, # = obstacle, O = trou, F = combattant, T = piege
        """
        fighters_by_pos = {}
        if fighters:
            for f in fighters:
                if f.is_alive:
                    fighters_by_pos[(f.x, f.y)] = f.name[0]

        lines = []
        header = "  " + "".join(f"{x:2d}" for x in range(self.width))
        lines.append(header)

        for y in range(self.height):
            row = f"{y:2d} "
            for x in range(self.width):
                cell = self.get_cell(x, y)
                if cell is None:
                    row += "  "
                elif (x, y) in fighters_by_pos:
                    row += f" {fighters_by_pos[(x, y)]}"
                elif cell.traps:
                    row += " T"
                elif cell.cell_type == CELL_OBSTACLE:
                    row += " #"
                elif cell.cell_type == CELL_HOLE:
                    row += " O"
                else:
                    row += " ."
            lines.append(row)

        return "\n".join(lines)


# ============================================================
# TESTS
# ============================================================

if __name__ == "__main__":
    from engine.fighter import Fighter
    from data.profiles.limmortel import PROFILE

    print("=" * 60)
    print("  TESTS ENGINE/GRID.PY V5.0")
    print("=" * 60)

    # --- Test 1: Creation de grille ---
    grid = Grid(10, 10)
    print(f"\nTest 1 - Grille 10x10: {len(grid.cells)} cases")

    # --- Test 2: Terrain ---
    grid.set_cell_type(3, 3, CELL_OBSTACLE)
    grid.set_cell_type(3, 4, CELL_OBSTACLE)
    grid.set_cell_type(5, 5, CELL_HOLE)
    print(f"\nTest 2 - Terrain modifie (obstacles en 3,3 et 3,4 / trou en 5,5)")

    # --- Test 3: Placement ---
    sram = Fighter("L'Immortel", team="A", profile=PROFILE)
    enemy = Fighter("Goblin", team="B", fighter_type="monster", level=100,
                     monster_template={"hp": 3000, "ap": 6, "mp": 3, "initiative": 80,
                                       "res_fire": 150, "lock": 200})

    grid.place_fighter(sram, 2, 3)
    grid.place_fighter(enemy, 4, 3)
    print(f"\nTest 3 - Placement: Sram ({sram.x},{sram.y}), Goblin ({enemy.x},{enemy.y})")

    # --- Test 4: Ligne de vue ---
    los_direct = grid.has_line_of_sight(2, 3, 6, 3)
    los_blocked = grid.has_line_of_sight(2, 3, 4, 3)
    print(f"\nTest 4 - Ligne de vue:")
    print(f"  (2,3) -> (6,3) sans combattant entre: {los_direct}")
    print(f"  (2,3) -> (4,3) avec goblin en (4,3) = arrive, pas bloque: {los_blocked}")

    los_obstacle = grid.has_line_of_sight(2, 3, 4, 4)
    print(f"  (2,3) -> (4,4) a travers obstacle (3,3): {los_obstacle}")

    # --- Test 5: Pathfinding ---
    path = grid.get_path(2, 3, 6, 3)
    print(f"\nTest 5 - Chemin (2,3) -> (6,3):")
    print(f"  Chemin: {path}")
    print(f"  Longueur: {len(path) if path else 'impossible'} cases")

    path_blocked = grid.get_path(2, 2, 4, 5)
    print(f"  Chemin (2,2) -> (4,5) contournant obstacles: {path_blocked}")
    print(f"  Longueur: {len(path_blocked) if path_blocked else 'impossible'} cases")

    # --- Test 6: Cases atteignables ---
    reachable = grid.get_reachable_cells(2, 3, max_pm=3)
    print(f"\nTest 6 - Cases atteignables depuis (2,3) avec 3 PM:")
    print(f"  {len(reachable)} cases atteignables")

    # --- Test 7: Portee ---
    in_range = grid.get_cells_in_range(2, 3, 1, 4, line_only=False)
    in_line = grid.get_cells_in_range(2, 3, 1, 4, line_only=True)
    print(f"\nTest 7 - Portee depuis (2,3):")
    print(f"  Portee 1-4 (zone): {len(in_range)} cases")
    print(f"  Portee 1-4 (ligne): {len(in_line)} cases")

    # --- Test 8: Swap ---
    print(f"\nTest 8 - Swap:")
    print(f"  Avant: Sram ({sram.x},{sram.y}), Goblin ({enemy.x},{enemy.y})")
    grid.swap_fighters(sram, enemy)
    print(f"  Apres: Sram ({sram.x},{sram.y}), Goblin ({enemy.x},{enemy.y})")

    # --- Test 9: Pieges ---
    grid.place_trap(5, 3, {"name": "piege_repulsion", "owner_id": sram.id, "ap_refund": 2})
    traps = grid.get_traps_at(5, 3)
    print(f"\nTest 9 - Piege en (5,3): {traps}")

    # --- Test 10: Rendu ASCII ---
    grid.swap_fighters(sram, enemy)
    print(f"\nTest 10 - Rendu grille:")
    print(grid.render([sram, enemy]))

    print(f"\n{'=' * 60}")
    print("  TOUS LES TESTS TERMINES")
    print(f"{'=' * 60}")
