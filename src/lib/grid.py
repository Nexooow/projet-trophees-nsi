import heapq
import math

class Grid:
    CELL_SIZE = 8  # Taille d'une cellule en pixels

    def __init__(self, screen_size):
        self.pixel_width = math.floor(screen_size[0])
        self.pixel_height = math.floor(screen_size[1])

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
            
    def get_cell_center (self, x, y):
        """
        Retourne les coordonnées du centre d'une cellule
        """
        cell = self.pixel_to_cell(x, y)
        return cell[0] * self.CELL_SIZE + (self.CELL_SIZE // 2), cell[1] * self.CELL_SIZE + (self.CELL_SIZE // 2)

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

    def is_cell_passable(self, cell_x, cell_y):
        """
        Vérifie si une cellule est "passable" pour le pathfinding
        """
        cell = self.get_cell(cell_x, cell_y)
        if cell is None:
            return False
        return cell["state"] == "empty" or cell["state"] == "occupied_walkable"

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
