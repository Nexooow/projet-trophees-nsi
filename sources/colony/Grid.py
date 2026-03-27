import heapq
import math
import random

import pygame
from constants import CELL_STATES, DARK_DIRT_COLOR
from lib.utils import lerp_color


class Grid:
    CELL_SIZE = 8  # Taille d'une cellule en pixels

    def __init__(self, screen_size, start_y):
        """
        screen_size: tuple (pixel_width, pixel_height) de la surface de la grille (en pixels)
        start_y: position Y (en pixels) du début de la zone de grille dans le monde (utile si on convertit global->local)
        """
        self.start_y = start_y
        self.pixel_width = math.floor(screen_size[0])
        self.pixel_height = math.floor(screen_size[1])

        # Dimensions de la grille en cellules (8x8 pixels par cellule)
        self.width = math.ceil(self.pixel_width / self.CELL_SIZE)
        self.height = math.ceil(self.pixel_height / self.CELL_SIZE)

        self.cached_paths = {}

        # Initialiser la grille avec des cellules "full"
        self.grid = []
        self.dirty_cells = set()
        for y in range(self.height):
            row = []
            for x in range(self.width):
                # calcul de la probabilité de variante en fonction de la profondeur
                depth_ratio = y / self.height
                variant = 0

                if depth_ratio > 0.15:
                    # proba plus grande selon profondeur
                    stone_prob = (depth_ratio - 0.15) * 0.3
                    if random.random() < stone_prob:
                        variant = 3

                # si pas de pierre, chance d'avoir une variation de terre (1 ou 2)
                if variant == 0:
                    dirt_variant_prob = 0.02 + depth_ratio * 0.13
                    if random.random() < dirt_variant_prob:
                        variant = random.randint(1, 2)

                row.append(
                    {
                        "state": "full",  # "full", "empty", "partial", "room", "occupied_*"
                        "bitmap": None,  # Matrice 8x8 pour les cellules partielles
                        "variant": variant,
                    }
                )
                self.dirty_cells.add((x, y))
            self.grid.append(row)

    def __iter__(self):
        """Itère sur toutes les cellules de la grille"""
        for grid_y in range(len(self.grid)):
            for grid_x in range(len(self.grid[grid_y])):
                yield grid_x, grid_y, self.grid[grid_y][grid_x]

    def get_cell(self, cell_x, cell_y):
        """Retourne une cellule de la grille (ou None si hors limites)"""
        if 0 <= cell_x < self.width and 0 <= cell_y < self.height:
            return self.grid[cell_y][cell_x]
        return None

    def set_cell_state(self, cell_x, cell_y, state, bitmap=None):
        """
        Change l'état d'une cellule et marque la cellule (et ses voisines) comme 'dirty' pour redessin.
        """
        if 0 <= cell_x < self.width and 0 <= cell_y < self.height:
            self.grid[cell_y][cell_x]["state"] = state
            self.grid[cell_y][cell_x]["bitmap"] = bitmap
            self.dirty_cells.add((cell_x, cell_y))

            # ajouter le flag "dirty" aux cellules voisines
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    nx, ny = cell_x + dx, cell_y + dy
                    if 0 <= nx < self.width and 0 <= ny < self.height:
                        self.dirty_cells.add((nx, ny))

    def get_cell_center(self, x, y):
        """
        Retourne les coordonnées du centre d'une cellule (en pixels relatifs à la grille)
        """
        cell = self.pixel_to_cell(x, y)
        return cell[0] * self.CELL_SIZE + (self.CELL_SIZE // 2), cell[
            1
        ] * self.CELL_SIZE + (self.CELL_SIZE // 2)

    def pixel_to_cell(self, pixel_x, pixel_y):
        """Convertit des coordonnées pixel en coordonnées cellule (relatives à la grille)"""
        cell_x = pixel_x // self.CELL_SIZE
        cell_y = pixel_y // self.CELL_SIZE
        return math.floor(cell_x), math.floor(cell_y)

    def cell_to_pixel(self, cell_x, cell_y):
        """Convertit des coordonnées cellule en coordonnées pixel (coin haut-gauche de la cellule)"""
        pixel_x = cell_x * self.CELL_SIZE
        pixel_y = cell_y * self.CELL_SIZE
        return pixel_x, pixel_y

    def get_bitmap_coords(self, pixel_x, pixel_y, cell_x, cell_y):
        """
        Retourne les coordonnées dans le bitmap d'un pixel
        """
        cell_pixel_x, cell_pixel_y = self.cell_to_pixel(cell_x, cell_y)
        bmp_x = pixel_x - cell_pixel_x
        bmp_y = pixel_y - cell_pixel_y
        return bmp_x, bmp_y

    def supprimer_cellules(self, x, y, size):
        """
        Supprime les cellules dans un cercle.
        x, y : coin haut gauche du carré englobant le cercle (coordonnées relatives à la grille)
        size : diamètre du cercle
        """
        # x,y sont attendus relatifs à la surface de la grille (i.e. 0..pixel_width)
        y -= self.start_y

        # Centre et rayon du cercle
        radius = size / 2
        center_x = x + radius
        center_y = y + radius
        radius_sq = radius * radius

        x2 = x + size
        y2 = y + size
        cell_x1, cell_y1 = self.pixel_to_cell(x, y)
        cell_x2, cell_y2 = self.pixel_to_cell(x2, y2)
        for cell_y in range(cell_y1, cell_y2 + 1):
            for cell_x in range(cell_x1, cell_x2 + 1):
                if 0 <= cell_x < self.width and 0 <= cell_y < self.height:
                    self.update_cell_with_circle(
                        cell_x, cell_y, center_x, center_y, radius_sq
                    )

    def update_cell_with_circle(self, cell_x, cell_y, cx, cy, r_sq):
        """
        Met à jour une cellule en fonction d'un cercle de suppression
        """
        cell = self.grid[cell_y][cell_x]

        if cell["state"] == "empty":
            return

        cell_px, cell_py = self.cell_to_pixel(cell_x, cell_y)

        corners = [
            (cell_px, cell_py),
            (cell_px + self.CELL_SIZE, cell_py),
            (cell_px, cell_py + self.CELL_SIZE),
            (cell_px + self.CELL_SIZE, cell_py + self.CELL_SIZE),
        ]

        corners_inclus = 0
        for c_x, c_y in corners:
            if (c_x - cx) ** 2 + (c_y - cy) ** 2 <= r_sq:
                corners_inclus += 1

        if corners_inclus == 4:
            self.set_cell_state(cell_x, cell_y, "empty", None)
            return

        if cell["state"] == "full":
            bitmap = [
                [True for _ in range(self.CELL_SIZE)] for _ in range(self.CELL_SIZE)
            ]
        elif cell["state"] == "partial":
            bitmap = cell["bitmap"]
        else:
            return

        # Marquer les pixels supprimés dans le bitmap
        # On itère sur les pixels de la cellule
        for py in range(self.CELL_SIZE):
            pixel_world_y = cell_py + py + 0.5
            for px in range(self.CELL_SIZE):
                if not bitmap[py][px]:
                    continue  # Déjà creusé

                pixel_world_x = cell_px + px + 0.5

                # Si le pixel est dans le cercle
                if (pixel_world_x - cx) ** 2 + (pixel_world_y - cy) ** 2 <= r_sq:
                    bitmap[py][px] = False

        # Vérifier si la cellule est maintenant vide ou partielle
        est_pleine = any(any(row) for row in bitmap)
        if not est_pleine:
            self.set_cell_state(cell_x, cell_y, "empty", None)
        else:
            self.set_cell_state(cell_x, cell_y, "partial", bitmap)

    def is_cell_passable(self, cell_x, cell_y):
        """
        Vérifie si une cellule est "passable" pour le pathfinding
        """
        cell = self.get_cell(cell_x, cell_y)
        if cell is None:
            return False
        return (
            cell["state"] == "empty"
            or cell["state"] == "occupied_walkable"
            or cell["state"] == "room"
        )

    def build_room(self, x, y, width, height):
        """
        Construit une salle (met les cellules en état "room").
        x, y : coin haut gauche en pixels (relatifs à la grille)
        width, height : dimensions en pixels
        """
        y -= self.start_y
        cell_x1, cell_y1 = self.pixel_to_cell(x, y)
        cell_x2, cell_y2 = self.pixel_to_cell(x + width, y + height)

        for cell_y in range(cell_y1, cell_y2):
            for cell_x in range(cell_x1, cell_x2):
                if 0 <= cell_x < self.width and 0 <= cell_y < self.height:
                    self.set_cell_state(cell_x, cell_y, "room", None)

    def get_neighbors(self, cell_x, cell_y):
        """
        Retourne les voisins valides d'une cellule (x, y)
        Coordonnées en cellules (pas en pixels)
        """
        neighbors = []
        directions = [
            (0, 1),
            (1, 0),
            (0, -1),
            (-1, 0),
            (1, 1),
            (-1, 1),
            (1, -1),
            (-1, -1),
        ]

        for dx, dy in directions:
            nx, ny = cell_x + dx, cell_y + dy
            if 0 <= nx < self.width and 0 <= ny < self.height:
                # vérifier que la cellule est un chemin valide
                if self.is_cell_passable(nx, ny):
                    neighbors.append((nx, ny))

        return neighbors

    def heuristic(self, a, b):
        """
        Distance entre deux points
        """
        return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)

    def get_path(self, start, goal):
        """
        Retourne le chemin d'un point a vers un point b sur la grille.
        Utilise un cache pour éviter de recalculer les chemins.
        """
        start_cell = self.pixel_to_cell(start[0], start[1] - self.start_y)
        goal_cell = self.pixel_to_cell(goal[0], goal[1] - self.start_y)
        cache_key = f"{start_cell}:{goal_cell}"
        if cache_key in self.cached_paths:
            return self.cached_paths[cache_key]
        elif f"{goal_cell}:{start_cell}" in self.cached_paths:
            return self.cached_paths[cache_key][::-1]
        else:
            path = self.a_star(start_cell, goal_cell)
            self.cached_paths[cache_key] = path
            return path

    def a_star(self, start, goal):
        """
        Implémentation de l'algorithme A* pour trouver le chemin le plus court
        entre start et goal.
        """
        # Vérifier que start et goal sont dans les limites
        if not (0 <= start[0] < self.width and 0 <= start[1] < self.height):
            return None
        if not (0 <= goal[0] < self.width and 0 <= goal[1] < self.height):
            return None

        if not self.is_cell_passable(start[0], start[1]) or not self.is_cell_passable(
            goal[0], goal[1]
        ):
            return None

        counter = 0
        open_set = [(0.0, counter, start)]
        counter += 1

        g_score = {start: 0.0}
        f_score = {start: self.heuristic(start, goal)}
        came_from = {}
        visites = set()

        while open_set:
            # Récupérer le nœud avec le plus petit f_score
            current_f, _, current = heapq.heappop(open_set)

            if current == goal:
                # reconstruire le chemin
                chemin = []
                while current in came_from:
                    chemin.append(current)
                    current = came_from[current]
                chemin.append(start)
                chemin.reverse()
                return chemin

            # marquer comme visité
            visites.add(current)

            # Explorer les voisins
            for neighbor in self.get_neighbors(current[0], current[1]):
                if neighbor in visites:
                    continue

                # Calculer le coût pour atteindre ce voisin
                dx = abs(neighbor[0] - current[0])
                dy = abs(neighbor[1] - current[1])
                move_cost = math.sqrt(dx * dx + dy * dy)

                tentative_g_score = g_score[current] + move_cost

                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    # enregistrer chemin
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + self.heuristic(
                        neighbor, goal
                    )

                    heapq.heappush(open_set, (f_score[neighbor], counter, neighbor))
                    counter += 1

        return None

    def is_solid_pixel(self, gx, gy):
        """
        Vérifie si un pixel (coordonnées relatives à la grille) est solide.
        """
        if not (0 <= gx < self.pixel_width and 0 <= gy < self.pixel_height):
            return True

        cx, cy = self.pixel_to_cell(gx, gy)
        cell = self.get_cell(cx, cy)
        if not cell:
            return True

        if cell["state"] == "full":
            return True
        elif cell["state"] == "empty":
            return False
        elif cell["state"] == "partial":
            px, py = gx % self.CELL_SIZE, gy % self.CELL_SIZE
            bmp = cell.get("bitmap")
            if not bmp:
                return True
            return bmp[py][px]
        return True

    def render_dirty_cells(self, surface, light_dirt_rgb, light_gal_rgb):
        """
        Dessine uniquement les cellules marquées comme 'dirty'. (pour optimisation)
        """
        while self.dirty_cells:
            cell_x, cell_y = self.dirty_cells.pop()
            cell = self.get_cell(cell_x, cell_y)
            if cell:
                self.render_cell(
                    surface, cell_x, cell_y, cell, light_dirt_rgb, light_gal_rgb
                )

    def render_cell(self, surface, cell_x, cell_y, cell, light_dirt_rgb, light_gal_rgb):
        """
        Dessine une cellule sur la surface fournie.
        """
        state = cell["state"]
        pixel_x, pixel_y = self.cell_to_pixel(cell_x, cell_y)
        cell_size = self.CELL_SIZE

        # Calcul de la couleur de la terre en fonction de la profondeur
        depth_ratio = cell_y / max(1, self.height)

        # Interpolation vers une couleur de fond plus sombre
        current_dirt_rgb = lerp_color(light_dirt_rgb, DARK_DIRT_COLOR, depth_ratio)
        dirt_r, dirt_g, dirt_b = current_dirt_rgb

        if state == "empty" or state == "room":
            pygame.draw.rect(
                surface,
                light_gal_rgb,
                (pixel_x, pixel_y, cell_size, cell_size),
            )
        elif state == "full":
            pygame.draw.rect(
                surface,
                current_dirt_rgb,
                (pixel_x, pixel_y, cell_size, cell_size),
            )
            # Variation visuelle aléatoire (cailloux/bruit)
            if cell.get("variant", 0) == 1:
                pygame.draw.rect(
                    surface,
                    (
                        max(0, dirt_r - 30),
                        max(0, dirt_g - 30),
                        max(0, dirt_b - 30),
                    ),
                    (pixel_x + 2, pixel_y + 2, 2, 2),
                )
            elif cell.get("variant", 0) == 2:
                pygame.draw.rect(
                    surface,
                    (
                        min(255, dirt_r + 25),
                        min(255, dirt_g + 25),
                        min(255, dirt_b + 25),
                    ),
                    (pixel_x + 5, pixel_y + 1, 2, 2),
                )
            elif cell.get("variant", 0) == 3:
                pygame.draw.rect(
                    surface,
                    "#abafb9",
                    (pixel_x + 3, pixel_y + 3, 1, 1),
                )
            # "Autotiling" : ombres le long des bords où la cellule rencontre du vide
            neighbors = [
                (0, -1, (0, 0, cell_size, 1)),  # Haut
                (0, 1, (0, cell_size - 1, cell_size, 1)),  # Bas
                (-1, 0, (0, 0, 1, cell_size)),  # Gauche
                (1, 0, (cell_size - 1, 0, 1, cell_size)),  # Droite
            ]
            shadow_color = (
                max(0, current_dirt_rgb[0] - 40),
                max(0, current_dirt_rgb[1] - 40),
                max(0, current_dirt_rgb[2] - 40),
            )
            for dx, dy, rect in neighbors:
                nx, ny = cell_x + dx, cell_y + dy
                neighbor = self.get_cell(nx, ny)
                draw_shadow = False
                if neighbor:
                    if neighbor["state"] == "empty" or neighbor["state"] == "room":
                        draw_shadow = True
                    elif neighbor["state"] == "partial":
                        # vérifier si les pixels adjacents dans la cellule partielle sont vides
                        bitmap = neighbor.get("bitmap")
                        if bitmap:
                            has_dirt_contact = False
                            if dy == -1:
                                has_dirt_contact = any(
                                    bitmap[cell_size - 1][x] for x in range(cell_size)
                                )
                            elif dy == 1:
                                has_dirt_contact = any(
                                    bitmap[0][x] for x in range(cell_size)
                                )
                            elif dx == -1:
                                has_dirt_contact = any(
                                    bitmap[y][cell_size - 1] for y in range(cell_size)
                                )
                            elif dx == 1:
                                has_dirt_contact = any(
                                    bitmap[y][0] for y in range(cell_size)
                                )
                            if not has_dirt_contact:
                                draw_shadow = True
                        else:
                            draw_shadow = True

                if draw_shadow:
                    pygame.draw.rect(
                        surface,
                        shadow_color,
                        (
                            pixel_x + rect[0],
                            pixel_y + rect[1],
                            rect[2],
                            rect[3],
                        ),
                    )

        elif state == "partial":
            # Fond galerie (on considère que light_gal_rgb correspond à la couleur des galeries)
            pygame.draw.rect(
                surface,
                light_gal_rgb,
                (pixel_x, pixel_y, cell_size, cell_size),
            )

            bitmap = cell.get("bitmap")
            if bitmap:
                shadow_color = (
                    max(0, dirt_r - 50),
                    max(0, dirt_g - 50),
                    max(0, dirt_b - 50),
                )
                highlight_color = (
                    min(255, dirt_r + 30),
                    min(255, dirt_g + 30),
                    min(255, dirt_b + 30),
                )

                for py in range(cell_size):
                    for px in range(cell_size):
                        if bitmap[py][px]:
                            gx = pixel_x + px
                            gy = pixel_y + py

                            pygame.draw.rect(surface, current_dirt_rgb, (gx, gy, 1, 1))

                            # détecter les bords pour ajouter ombrage
                            if not self.is_solid_pixel(gx, gy - 1):
                                pygame.draw.rect(
                                    surface, highlight_color, (gx, gy, 1, 1)
                                )
                            elif not self.is_solid_pixel(gx, gy + 1):
                                pygame.draw.rect(surface, shadow_color, (gx, gy, 1, 1))

        elif state.startswith("occupied"):
            pygame.draw.rect(
                surface,
                light_gal_rgb,
                (pixel_x, pixel_y, cell_size, cell_size),
            )

    def serialize(self) -> list:
        """
        Sérialise la grille
        """
        rows = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                cell = self.grid[y][x]
                state = cell["state"]
                bitmap = cell.get("bitmap")
                # Only keep variant for 'full' cells; other states must have variant 0
                variant = cell.get("variant", 0) if state == "full" else 0
                if state == "full":
                    # store variant as full_v{variant+1} so full_v1 represents variant 0
                    code_key = f"full_v{variant + 1}"
                    row.append(CELL_STATES.get(code_key, CELL_STATES["full_v1"]))
                elif state == "empty":
                    row.append(CELL_STATES["empty"])
                elif state == "occupied":
                    row.append(CELL_STATES["occupied"])
                elif state == "occupied_walkable":
                    row.append(CELL_STATES["occupied_walkable"])
                elif state == "room":
                    row.append(CELL_STATES["room"])
                elif state == "partial" and bitmap is not None:
                    # Compresser le bitmap en liste d'entiers (1 entier = 1 ligne de 8 bits)
                    compressed = [
                        int("".join("1" if px else "0" for px in row_bmp), 2)
                        for row_bmp in bitmap
                    ]
                    row.append([compressed, variant])
                else:
                    row.append(None)
            rows.append(row)
        return rows

    def restore(self, rows: list):
        """
        Restaure la grille à partir de la sauvegarde.
        """
        self.cached_paths = {}

        INT_TO_STATE: dict = {}
        for key, code in CELL_STATES.items():
            if key.startswith("full_v"):
                # stored full_vN corresponds to variant N-1 (full_v1 -> variant 0)
                variant = int(key[len("full_v") :]) - 1
                INT_TO_STATE[code] = ("full", variant)
            elif key == "empty":
                INT_TO_STATE[code] = ("empty", 0)
            elif key == "occupied":
                INT_TO_STATE[code] = ("occupied", 0)
            elif key == "occupied_walkable":
                INT_TO_STATE[code] = ("occupied_walkable", 0)
            elif key == "room":
                INT_TO_STATE[code] = ("room", 0)

        for y, row in enumerate(rows):
            if y >= self.height:
                break
            for x, cell_data in enumerate(row):
                if x >= self.width:
                    break
                if isinstance(cell_data, int):
                    # État simple encodé comme un entier
                    state, variant = INT_TO_STATE.get(cell_data, ("full", 0))
                    bitmap = None
                elif isinstance(cell_data, list):
                    # Cellule partielle : [compressed_bitmap, variant]
                    compressed, variant = cell_data[0], cell_data[1]
                    state = "partial"
                    bitmap = []
                    for row_int in compressed:
                        brow = []
                        for bit in range(7, -1, -1):
                            brow.append(bool((row_int >> bit) & 1))
                        bitmap.append(brow)
                else:
                    state, variant, bitmap = "full", 0, None

                self.grid[y][x]["state"] = state
                self.grid[y][x]["bitmap"] = bitmap
                self.grid[y][x]["variant"] = variant
                self.dirty_cells.add((x, y))
