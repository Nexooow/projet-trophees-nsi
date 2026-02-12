from asyncio.events import AbstractEventLoopPolicy
import heapq
import math

class Grid:
    CELL_SIZE = 8  # Taille d'une cellule en pixels

    def __init__(self, start_y, screen_size):
        self.start_y = start_y
        self.pixel_width = math.floor(screen_size[0])
        self.pixel_height = math.floor(screen_size[1] - start_y)

        # Dimensions de la grille en cellules (8x8 pixels par cellule)
        self.width = math.ceil(self.pixel_width / self.CELL_SIZE)
        self.height = math.ceil(self.pixel_height / self.CELL_SIZE)

        # Initialiser la grille avec des cellules "full"
        self.grid = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                row.append(
                    {
                        "state": "full",  # "full", "empty", "partial"
                        "bitmap": None,  # Matrice 8x8 pour les cellules partielles
                    }
                )
            self.grid.append(row)

    def __iter__(self):
        """Itère sur toutes les cellules de la grille"""
        for grid_y in range(len(self.grid)):
            for grid_x in range(len(self.grid[grid_y])):
                yield grid_x, grid_y, self.grid[grid_y][grid_x]

    def get_cell(self, cell_x, cell_y):
        """Retourne une cellule de la grille"""
        if 0 <= cell_x < self.width and 0 <= cell_y < self.height:
            return self.grid[cell_y][cell_x]
        return None

    def set_cell_state(self, cell_x, cell_y, state, bitmap=None):
        """
        Change l'état d'une cellule
        """
        if 0 <= cell_x < self.width and 0 <= cell_y < self.height:
            self.grid[cell_y][cell_x]["state"] = state
            self.grid[cell_y][cell_x]["bitmap"] = bitmap

    def pixel_to_cell(self, pixel_x, pixel_y):
        """Convertit des coordonnées pixel en coordonnées cellule"""
        cell_x = pixel_x // self.CELL_SIZE
        cell_y = pixel_y // self.CELL_SIZE
        return math.floor(cell_x), math.floor(cell_y)

    def cell_to_pixel(self, cell_x, cell_y):
        """Convertit des coordonnées cellule en coordonnées pixel"""
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

    def supprimer_cellules(self, x, y, w, h):
        """
        Supprime les cellules dans un rectangle (x, y, w, h)
        Met à jour les cellules qui sont en collision avec le rectangle
        """
        # ajuster y pour les coordonnées de la grille
        y = y - self.start_y

        # coordonnées du rectangle en pixels
        rect_x1 = max(0, x)
        rect_y1 = max(0, y)
        rect_x2 = min(self.pixel_width, x + w)
        rect_y2 = min(self.pixel_height, y + h)

        # Convertir en coordonnées de cellules
        cell_x1, cell_y1 = self.pixel_to_cell(rect_x1, rect_y1)
        cell_x2, cell_y2 = self.pixel_to_cell(rect_x2 - 1, rect_y2 - 1)

        # parcourir toutes les cellules touchées
        for cell_y in range(cell_y1, cell_y2 + 1):
            for cell_x in range(cell_x1, cell_x2 + 1):
                if 0 <= cell_x < self.width and 0 <= cell_y < self.height:
                    self._update_cell_with_rect(
                        cell_x, cell_y, rect_x1, rect_y1, rect_x2, rect_y2
                    )

    def _update_cell_with_rect(
        self, cell_x, cell_y, rect_x1, rect_y1, rect_x2, rect_y2
    ):
        """
        Met à jour une cellule en fonction d'un rectangle de suppression
        """
        cell = self.grid[cell_y][cell_x]

        # Coordonnées pixel de la cellule
        cell_pixel_x, cell_pixel_y = self.cell_to_pixel(cell_x, cell_y)

        # Intersection entre la cellule et le rectangle de suppression
        inter_x1 = max(cell_pixel_x, rect_x1)
        inter_y1 = max(cell_pixel_y, rect_y1)
        inter_x2 = min(cell_pixel_x + self.CELL_SIZE, rect_x2)
        inter_y2 = min(cell_pixel_y + self.CELL_SIZE, rect_y2)

        # Si la cellule est entièrement dans le rectangle
        if (
            inter_x1 == cell_pixel_x
            and inter_y1 == cell_pixel_y
            and inter_x2 == cell_pixel_x + self.CELL_SIZE
            and inter_y2 == cell_pixel_y + self.CELL_SIZE
        ):
            self.set_cell_state(cell_x, cell_y, "empty", None)
            return

        # Sinon, créer ou mettre à jour le bitmap
        if cell["state"] == "full":
            bitmap = [
                [True for _ in range(self.CELL_SIZE)] for _ in range(self.CELL_SIZE)
            ]
        elif cell["state"] == "partial":
            bitmap = cell["bitmap"]
        else:  # empty
            return
        
        # Marquer les pixels supprimés dans le bitmap
        for py in range(math.floor(inter_y1), math.floor(inter_y2)):
            for px in range(math.floor(inter_x1), math.floor(inter_x2)):
                bmp_x = px - cell_pixel_x
                bmp_y = py - cell_pixel_y
                if 0 <= bmp_x < self.CELL_SIZE and 0 <= bmp_y < self.CELL_SIZE:
                    bitmap[bmp_y][bmp_x] = False

        # Vérifier si la cellule est maintenant vide ou partielle
        is_filled = any(any(row) for row in bitmap)

        if not is_filled:
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
        return cell["state"] == "empty"

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
            # Vérifier que le voisin est dans la grille
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

        # Vérifier que start et goal sont passables
        if not self.is_cell_passable(start[0], start[1]) or not self.is_cell_passable(
            goal[0], goal[1]
        ):
            return None

        # file de priorité
        counter = 0
        open_set = [(0.0, counter, start)]
        counter += 1

        # Dictionnaire des scores g (coût depuis le départ)
        g_score = {start: 0.0}

        # Dictionnaire des scores f (g + distance)
        f_score = {start: self.heuristic(start, goal)}

        # Dictionnaire pour reconstruire le chemin
        came_from = {}

        # Ensemble des positions déjà visitées
        visites = set()

        while open_set:
            # Récupérer le nœud avec le plus petit f_score
            current_f, _, current = heapq.heappop(open_set)

            # Si on a atteint le goal
            if current == goal:
                # Reconstruire le chemin
                chemin = []
                while current in came_from:
                    chemin.append(current)
                    current = came_from[current]
                chemin.append(start)
                chemin.reverse()
                return chemin

            # Marquer comme visité
            visites.add(current)

            # Explorer les voisins
            for neighbor in self.get_neighbors(current[0], current[1]):
                if neighbor in visites:
                    continue

                # Calculer le coût pour atteindre ce voisin
                # Coût de 1.0 pour les mouvements orthogonaux, ~1.414 pour les diagonales
                dx = abs(neighbor[0] - current[0])
                dy = abs(neighbor[1] - current[1])
                move_cost = math.sqrt(dx * dx + dy * dy)

                tentative_g_score = g_score[current] + move_cost

                # Si ce chemin vers le voisin est meilleur
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    # enregistrer chemin
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + self.heuristic(
                        neighbor, goal
                    )

                    # Ajouter à la file de priorité
                    heapq.heappush(open_set, (f_score[neighbor], counter, neighbor))
                    counter += 1

        # Aucun chemin trouvé
        return None
