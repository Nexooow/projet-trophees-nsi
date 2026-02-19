import pygame

from colony.ants.Worker import Worker
from colony.BuildMode import BuildMode
from colony.rooms.Depot import Depot
from colony.rooms.Nursery import Nursery
from colony.rooms.Queen import Queen
from colony.TaskManager import TaskManager
from constants import (
    UIColors,
    colony_height,
    colony_underground_start,
    colony_width,
    dark_dirt_color,
    dirt_color,
)
from lib.grid import Grid
from lib.perlin import Perlin
from lib.ui import Label, ProgressBar
from lib.utils import import_asset

from .State import State

_leaf_image = import_asset("icons", "leaf.png")


class ColonyState(State):
    def __init__(self, state_manager):
        super().__init__(state_manager, "colony", [])
        self.tasks = TaskManager(self)

        self.world = pygame.Surface(
            (colony_width, colony_height), pygame.SRCALPHA | pygame.HWSURFACE
        )
        self.camera_x = -100
        self.camera_y = 0

        self.build_mode = BuildMode(self)

        self.grid_surface = pygame.Surface(
            (colony_width, colony_height - colony_underground_start), pygame.SRCALPHA
        )
        self.grid = Grid(self.grid_surface.get_size(), colony_underground_start)
        grid_x_center = self.grid.width // 2

        self.perlin = Perlin(
            seed=42,
            scale=60,
            octaves=1,
            persistence=0.5,
            lacunarity=1.5,
            threshold=0.47,
            threshold_values=(0.0, 1.0),
        )

        self.rooms = [
            Depot(self, {"x": grid_x_center, "y": 0, "width": 13, "height": 8}),
            Queen(self, {"x": grid_x_center + 42, "y": 71, "width": 17, "height": 17}),
            Nursery(self, {"x": grid_x_center - 30, "y": 87, "width": 15, "height": 7}),
        ]

        self.ants = []
        # self.ennemies = []

        self.food = 200
        # self.science = 0

        self.generate_grid()

    def enable(self):
        w, h = self.game.width, self.game.height

        info_w = 376
        info_h = 130
        info_x = w - (info_w + 8)
        info_y = 8

        self.ui.panel(
            "colony_info_panel",
            (info_x, info_y, info_w, info_h),
        ).set_z_index(10)

        self.ui.panel(
            "colony_time_preview_panel",
            (info_x + 2, info_y + 2, 100, info_h - 4),
        ).set_bg_color((255, 0, 255)).set_border(None).set_z_index(11)

        self.ui.label(
            "colony_time",
            self.game.time.format(),
            (info_x + 104, info_y + 4, info_w - 108, 42),
        ).set_font("assets/fonts/monogram.ttf", 32).set_text_color(
            UIColors.TEXT
        ).set_align("center", "center").set_z_index(11)

        small_w = info_w // 2
        small_h = 32 + 12
        small_x = info_x + info_w - small_w
        small_y = info_y + info_h + 8

        self.ui.panel(
            "colony_food_panel",
            (small_x, small_y, small_w, small_h),
        ).set_z_index(10)

        icon_y = small_y + (small_h - 32) // 2
        self.ui.image(
            "colony_food_icon",
            _leaf_image,
            (small_x + 8, icon_y, 32, 32),
        ).set_z_index(11)

        self.ui.label(
            "colony_food_count",
            f"{self.food}",
            (small_x + 8 + 32 + 4, small_y - 2, small_w - 8 - 32 - 4 - 8, small_h),
        ).set_font("assets/fonts/monogram.ttf", 32 + 6).set_text_color(
            UIColors.TEXT
        ).set_align("right", "center").set_z_index(11)

        self.ui.label(
            "colony_build_mode_hint",
            "",
            (8, h - 40, 300, 32),
        ).set_font("assets/fonts/monogram.ttf", 22).set_text_color(
            UIColors.TEXT_DISABLED
        ).set_align("left", "center").set_z_index(10)

    def disable(self):
        """Supprime les éléments UI de la colonie."""
        self.ui.clear()

    def get_room(self, room_name):
        """
        Renvoie les coordonnées d'une pièce
        """
        for room in self.rooms:
            if room.name == room_name:
                return room
        return None

    def get_room_coords(self, room_name):
        room = self.get_room(room_name)
        if room:
            return (room.x, room.y)
        return None

    def update(self, events):
        keys = pygame.key.get_pressed()
        screen_width, screen_height = self.game.screen.get_size()

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_b:
                    self.build_mode.switch()
                    self.update_build_mode_hint()

        if self.build_mode.enabled:
            self.build_mode.update(events)

        # Calcul des limites de la caméra pour que le monde reste toujours visible
        min_camera_x = screen_width - colony_width
        min_camera_y = screen_height - colony_height

        # Déplacements
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.camera_x = max(min_camera_x, self.camera_x - 5)
        elif keys[pygame.K_LEFT] or keys[pygame.K_q]:
            self.camera_x = min(0, self.camera_x + 5)
        if keys[pygame.K_UP] or keys[pygame.K_z]:
            self.camera_y = min(0, self.camera_y + 5)
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.camera_y = max(min_camera_y, self.camera_y - 5)

        for ant in self.ants:
            ant.update()
        for room in self.rooms:
            room.update()

        self.sync_ui()

    def sync_ui(self):
        """Met à jour les valeurs dynamiques des éléments UI."""
        food_label = self.ui.get("colony_food_count")
        if isinstance(food_label, Label):
            food_label.set_text(f"{self.food}")
        time_label = self.ui.get("colony_time")
        if isinstance(time_label, Label):
            print("maj")
            time_label.set_text(self.game.time.format())

    def update_build_mode_hint(self):
        """Affiche ou efface l'indicateur de mode construction."""
        hint = self.ui.get("colony_build_mode_hint")
        if isinstance(hint, Label):
            if self.build_mode.enabled:
                hint.set_text("[B] Mode construction actif")
                hint.set_text_color(UIColors.BORDER)
            else:
                hint.set_text("")

    def generate_grid(self):
        """
        Dessine la grille de la colonie sur une surface dédiée, pour éviter de surcharger la fonction draw.
        Le bruit de Perlin est intégré ici pour varier la couleur des cellules de terre entre dirt_color et dark_dirt_color.
        """
        self.grid_surface.fill((255, 255, 255))

        pygame.draw.rect(
            self.grid_surface,
            (66, 31, 17),
            (
                0,
                0,
                colony_width,
                colony_height - colony_underground_start,
            ),
        )

        # Génère la noise map une fois pour toute la grille (résolution cellule)
        noise_map = self.perlin.noise_map(self.grid.width, self.grid.height)

        for cell_x, cell_y, cell in self.grid:
            state = cell["state"]

            # Coordonnées pixel de la cellule
            pixel_x, pixel_y = self.grid.cell_to_pixel(cell_x, cell_y)

            # Choisir la couleur de terre selon le bruit de Perlin (0.0 → claire, 1.0 → foncée)
            cell_color = (
                dark_dirt_color if noise_map[cell_y][cell_x] > 0.5 else dirt_color
            )

            if state == "full":
                # Dessiner la cellule entière
                pygame.draw.rect(
                    self.grid_surface,
                    cell_color,
                    (pixel_x, pixel_y, self.grid.CELL_SIZE, self.grid.CELL_SIZE),
                )
            elif state == "partial":
                # Dessiner uniquement les pixels pleins du bitmap
                bitmap = cell["bitmap"]
                if bitmap:
                    for bmp_y in range(self.grid.CELL_SIZE):
                        for bmp_x in range(self.grid.CELL_SIZE):
                            if bitmap[bmp_y][bmp_x]:
                                pygame.draw.rect(
                                    self.grid_surface,
                                    cell_color,
                                    (pixel_x + bmp_x, pixel_y + bmp_y, 1, 1),
                                )

    def draw(self):
        """
        TODO
        """
        pygame.draw.rect(
            self.world, "#7dbefa", (0, 0, colony_width, colony_height * 0.12)
        )
        # TODO: entre 0.12 et 0.15, faire l'herbe et la végétation pour la transition entre extérieur et la partie
        #  terreuse de la colonie
        pygame.draw.rect(
            self.world,
            "#4cbd56",
            (0, colony_height * 0.12, colony_width, colony_height * 0.04),
        )

        self.world.blit(self.grid_surface, (0, colony_underground_start))

        if self.build_mode.enabled:
            self.build_mode.draw()

        for ant in self.ants:
            ant.draw()
        for room in self.rooms:
            room.draw()

        self.game.screen.blit(self.world, (self.camera_x, self.camera_y))
