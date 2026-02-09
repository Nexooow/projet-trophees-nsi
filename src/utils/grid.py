import math

class Grid:

    def __init__(self, start_y, screen_size):
        self.start_y = start_y
        self.size_x = screen_size[0]
        self.size_y = screen_size[1] - start_y
        self.cell_size = 8
        self.width = math.ceil(self.size_x / self.cell_size)
        self.height = math.ceil(self.size_y / self.cell_size)
        self.grid = [
            [
                {"state": "full", "bitmap": None} for _ in range(self.width)
            ] for _ in range(self.height)
        ]

    def __iter__(self):
        for grid_y in range(len(self.grid)):
            for grid_x in range(len(self.grid[grid_y])):
                yield grid_x, grid_y, self.grid[grid_y][grid_x]

    def set_state (self, x, y, state, bitmap=None):
        self.grid[y][x] = {"state": state, "bitmap": bitmap if state == "partial" else None}

    def cellules_en_collision (self, x, y, w, h):
        """
        Retourne les cellules en collision avec le rectangle (x,y) de largeur w et hauteur h
        """
        y = y - self.start_y
        x2 = x + w
        y2 = y + h

        grid_x1 = math.floor(max(0, x // self.cell_size))
        grid_y1 = math.floor(max(0, y // self.cell_size))
        grid_x2 = math.floor(min(self.width - 1, x2 // self.cell_size))
        grid_y2 = math.floor(min(self.height - 1, y2 // self.cell_size))

        # Itérer uniquement sur les cellules concernées
        for grid_y in range(grid_y1, grid_y2):
            for grid_x in range(grid_x1, grid_x2):
                yield grid_x, grid_y

    def supprimer_cellules (self, x, y, w, h):
        """
        pass
        """
        for grid_x, grid_y in self.cellules_en_collision(x, y, w, h):
            print(f"Cellule ({grid_x}, {grid_y}) en collision")
            self.set_state(grid_x, grid_y, "empty", bitmap=None)
            # TODO: vérifier les cellules adjacentes pour voir si le rectangle touche partiellement la cellule
