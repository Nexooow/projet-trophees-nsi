import pygame

from colony.BuildMode import BuildMode
from colony.rooms.Depot import Depot
from colony.rooms.Nursery import Nursery
from colony.rooms.Queen import Queen
from colony.TaskManager import TaskManager
from constants import (
    COLONY_BRUSH_SIZE,
    COLONY_GRASS_START,
    COLONY_HEIGHT,
    COLONY_UNDERGROUND_START,
    COLONY_WIDTH,
    DIRT_COLOR,
    GALERY_COLOR,
    UIColors,
)
from lib.grid import Grid
from lib.sidebar import Sidebar
from lib.ui import Label
from lib.utils import import_asset

from .State import State

_leaf_image = import_asset("icons", "leaf.png")


class ColonyState(State):
    def __init__(self, state_manager):
        super().__init__(state_manager, "colony", [])
        self.tasks = TaskManager(self)

        self.sidebar = None
        self.world = pygame.Surface(
            (COLONY_WIDTH, COLONY_HEIGHT), pygame.SRCALPHA | pygame.HWSURFACE
        )
        self.camera_x = -(COLONY_WIDTH - self.game.width) // 2
        self.camera_y = 0

        self.build_mode = BuildMode(self)

        self.grid_surface = pygame.Surface(
            (COLONY_WIDTH, COLONY_HEIGHT - COLONY_UNDERGROUND_START), pygame.SRCALPHA
        )
        self.grid = Grid(self.grid_surface.get_size(), COLONY_UNDERGROUND_START)
        grid_x_center = self.grid.width // 2

        self.rooms = [
            Depot(self, {"x": grid_x_center, "y": 0, "width": 13, "height": 8}),
            Queen(self, {"x": grid_x_center + 42, "y": 67, "width": 12, "height": 12}),
            Nursery(self, {"x": grid_x_center - 27, "y": 87, "width": 15, "height": 7}),
        ]

        self.ants = []
        # self.ennemies = []

        self.food = 200
        # self.science = 0

        light_dirt = pygame.Color(DIRT_COLOR)
        self.light_dirt_rgb = (light_dirt.r, light_dirt.g, light_dirt.b)
        light_gal = pygame.Color(GALERY_COLOR)
        self.light_gal_rgb = (light_gal.r, light_gal.g, light_gal.b)

        self.init_default_paths()
        self.render_dirty_cells()

        self.night_overlay = pygame.Surface(
            self.game.screen.get_size(), pygame.SRCALPHA
        )
        self.is_sleeping = False
        self.sleep_timer = 0

    def enable(self):
        self.sidebar = Sidebar(self.ui, (8, 8, 360, self.game.height - 16))
        w, h = self.game.width, self.game.height
        padding = 8

        info_w = 376
        info_h = 130
        info_x = w - (info_w + padding)
        info_y = padding

        self.ui.panel(
            "colony_info_panel",
            (info_x, info_y, info_w, info_h),
        ).set_z_index(10).add_child(
            self.ui.panel("colony_time_preview_panel", (2, 2, 100, info_h - 4))
            .set_bg_color((255, 0, 255))
            .set_border(None)
            .set_z_index(11)
        ).add_child(
            self.ui.label(
                "colony_time",
                self.game.time.format(),
                (104, 4, info_w - 108, 42),
            )
            .set_font("assets/fonts/m5x7.ttf", 32)
            .set_text_color(UIColors.TEXT)
            .set_align("center", "center")
            .set_z_index(11)
        )

        small_w = info_w // 2
        small_h = 32 + 12
        small_x = info_x + info_w - small_w
        small_y = info_y + info_h + padding

        self.ui.panel(
            "colony_food_panel",
            (small_x, small_y, small_w, small_h),
        ).set_z_index(10).add_child(
            self.ui.image(
                "colony_food_icon",
                _leaf_image,
                (padding, (small_h - 32) // 2, 32, 32),
            ).set_z_index(11)
        ).add_child(
            self.ui.label(
                "colony_food_count",
                f"{self.food}",
                (padding + 32 + 4, -2, small_w - 32 - 4 - padding * 2, small_h),
            )
            .set_font("assets/fonts/m5x7.ttf", 32 + 6)
            .set_text_color(UIColors.TEXT)
            .set_align("right", "center")
            .set_z_index(11)
        )

        self.ui.label(
            "colony_night_message",
            "",
            (0, h // 2 - 50, w, 100),
        ).set_font("assets/fonts/m5x7.ttf", 48).set_text_color(UIColors.TEXT).set_align(
            "center", "center"
        ).set_z_index(20)

        menu_btn_size = 48
        menu_icon_size = 32
        menu_padding = 8
        menu_spacing = 8

        # Position du premier bouton (mode construction)
        btn_x = w - menu_padding - menu_btn_size
        btn_y = h - menu_padding - menu_btn_size

        self.ui.button(
            "colony_btn_build",
            "",
            (btn_x, btn_y, menu_btn_size, menu_btn_size),
        ).on("click", lambda: self.build_mode.switch()).set_z_index(10).add_child(
            self.ui.image(
                "colony_btn_build_icon",
                _leaf_image,  # TODO: changer l'icone
                (
                    (menu_btn_size - menu_icon_size) // 2,
                    (menu_btn_size - menu_icon_size) // 2,
                    menu_icon_size,
                    menu_icon_size,
                ),
            )
        ).add_child(
            self.ui.label(
                "colony_btn_build_shortcut",
                "B",
                (0, 0, menu_btn_size - 2, menu_btn_size - 2),
            )
            .set_align("right", "bottom")
            .set_font("assets/fonts/m5x7.ttf", 16)
            .set_text_color(UIColors.TEXT)
        )

        btn_x -= menu_btn_size + menu_spacing
        self.ui.button(
            "colony_btn_expedition",
            "",
            (btn_x, btn_y, menu_btn_size, menu_btn_size),
        ).on("click", lambda: print("A faire, implémenter l'expédition")).set_z_index(
            10
        ).add_child(
            self.ui.image(
                "colony_btn_expedition_icon",
                _leaf_image,  # TODO: changer l'icone
                (
                    (menu_btn_size - menu_icon_size) // 2,
                    (menu_btn_size - menu_icon_size) // 2,
                    menu_icon_size,
                    menu_icon_size,
                ),
            )
        ).add_child(
            self.ui.label(
                "colony_btn_expedition_shortcut",
                "E",
                (0, 0, menu_btn_size - 2, menu_btn_size - 2),
            )
            .set_align("right", "bottom")
            .set_font("assets/fonts/m5x7.ttf", 16)
            .set_text_color(UIColors.TEXT)
        )

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

    def get_room_coords(self, room_name, center=False):
        room = self.get_room(room_name)
        if room:
            if center:
                return room.get_center()
            return room.get_pos()
        return None

    def update(self, events):
        keys = pygame.key.get_pressed()
        screen_width, screen_height = self.game.screen.get_size()

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_b:
                    self.build_mode.switch()

        if self.build_mode.enabled:
            self.build_mode.update(events)

        self.update_day_cycle()

        if self.is_sleeping:
            self.sync_ui()
            return

        # Calcul des limites de la caméra pour que le monde reste toujours visible
        min_camera_x = screen_width - COLONY_WIDTH
        min_camera_y = screen_height - COLONY_HEIGHT

        # Déplacements
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.camera_x = max(min_camera_x, self.camera_x - 5)
        elif keys[pygame.K_LEFT] or keys[pygame.K_q]:
            self.camera_x = min(0, self.camera_x + 5)
        if keys[pygame.K_UP] or keys[pygame.K_z]:
            self.camera_y = min(0, self.camera_y + 5)
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.camera_y = max(min_camera_y, self.camera_y - 5)

        self.tasks.update()

        for ant in self.ants:
            ant.update()
        for room in self.rooms:
            room.update()

        self.render_dirty_cells()
        self.sync_ui()

    def update_day_cycle(self):
        h, m = self.game.time.get_time()

        if self.is_sleeping:
            self.sleep_timer += 1
            if self.sleep_timer >= 180:  # 3 secondes à 60 FPS
                self.is_sleeping = False
                self.game.time.set_time(6 * 60)  # Réveil à 6h00
                self.game.time.day += 1
        elif h >= 22:  # Dormir à 22h00
            self.is_sleeping = True
            self.sleep_timer = 0

    def get_ambient_light_alpha(self):
        h, m = self.game.time.get_time()
        time_in_minutes = h * 60 + m
        # Lever du soleil : 6h00 -> 9h00 (360 -> 540)
        # Journée : 9h00 -> 19h00 (540 -> 1140)
        # Coucher du soleil : 19h00 -> 22h00 (1140 -> 1320)
        # Nuit : 22h00 -> 6h00 (1320 -> 1440 / 0 -> 360)
        max_darkness = 200
        if 360 <= time_in_minutes < 540:
            # Transition Nuit -> Jour (Dégressif)
            ratio = (time_in_minutes - 360) / (540 - 360)
            return int(max_darkness * (1 - ratio))
        elif 540 <= time_in_minutes < 1140:
            # Journée
            return 0
        elif 1140 <= time_in_minutes < 1320:
            # Transition Jour -> Nuit (Progressif)
            ratio = (time_in_minutes - 1140) / (1320 - 1140)
            return int(max_darkness * ratio)
        else:
            # Nuit
            return max_darkness

    def sync_ui(self):
        """Met à jour les valeurs dynamiques des éléments UI."""
        food_label = self.ui.get("colony_food_count")
        if isinstance(food_label, Label):
            food_label.set_text(f"{self.food}")
        time_label = self.ui.get("colony_time")
        if isinstance(time_label, Label):
            time_label.set_text(self.game.time.format())

        night_label = self.ui.get("colony_night_message")
        if isinstance(night_label, Label):
            if self.is_sleeping:
                night_label.set_text(f"Fin du jour {self.game.time.day}...")
            else:
                night_label.set_text("")

    def init_default_paths(self):
        for room_paths in [("depot", "queen"), ("nursery", "queen")]:
            (src, trgt) = room_paths
            a = self.get_room_coords(src, center=True)
            b = self.get_room_coords(trgt, center=True)

            if a is None or b is None:
                continue

            mid_x = (a[0] + b[0]) // 2
            mid_y = (a[1] + b[1]) // 2
            offset = 60
            control = (mid_x + offset, mid_y + offset)

            steps = 100
            for i in range(steps + 1):
                t = i / steps
                # courbe de bézier
                x = (1 - t) ** 2 * a[0] + 2 * (1 - t) * t * control[0] + t**2 * b[0]
                y = (1 - t) ** 2 * a[1] + 2 * (1 - t) * t * control[1] + t**2 * b[1]

                x = int(x) - COLONY_BRUSH_SIZE // 2
                y = int(y) - COLONY_BRUSH_SIZE // 2

                self.grid.supprimer_cellules(x, y, COLONY_BRUSH_SIZE)

    def is_solid_pixel(self, gx, gy):
        """Vérifie si un pixel est solide."""
        if not (0 <= gx < self.grid.pixel_width and 0 <= gy < self.grid.pixel_height):
            return True

        cx, cy = self.grid.pixel_to_cell(gx, gy)
        cell = self.grid.get_cell(cx, cy)
        if not cell:
            return True

        if cell["state"] == "full":
            return True
        elif cell["state"] == "empty":
            return False
        elif cell["state"] == "partial":
            px, py = gx % self.grid.CELL_SIZE, gy % self.grid.CELL_SIZE
            return cell["bitmap"][py][px]
        return True

    def render_dirty_cells(self):
        """
        Dessine uniquement les cellules marquées comme 'dirty'.
        """
        while self.grid.dirty_cells:
            cell_x, cell_y = self.grid.dirty_cells.pop()
            cell = self.grid.get_cell(cell_x, cell_y)
            if cell:
                self.render_cell(cell_x, cell_y, cell)

    def render_cell(self, cell_x, cell_y, cell):
        state = cell["state"]
        pixel_x, pixel_y = self.grid.cell_to_pixel(cell_x, cell_y)
        cell_size = self.grid.CELL_SIZE

        if state == "empty":
            pygame.draw.rect(
                self.grid_surface,
                self.light_gal_rgb,
                (pixel_x, pixel_y, cell_size, cell_size),
            )
        elif state == "full":
            pygame.draw.rect(
                self.grid_surface,
                self.light_dirt_rgb,
                (pixel_x, pixel_y, cell_size, cell_size),
            )
            # Variation visuelle aléatoire (cailloux/bruit)
            if cell.get("variant", 0) == 1:
                pygame.draw.rect(
                    self.grid_surface,
                    (
                        max(0, self.light_dirt_rgb[0] - 30),
                        max(0, self.light_dirt_rgb[1] - 30),
                        max(0, self.light_dirt_rgb[2] - 30),
                    ),
                    (pixel_x + 2, pixel_y + 2, 2, 2),
                )
            elif cell.get("variant", 0) == 2:
                pygame.draw.rect(
                    self.grid_surface,
                    (
                        min(255, self.light_dirt_rgb[0] + 25),
                        min(255, self.light_dirt_rgb[1] + 25),
                        min(255, self.light_dirt_rgb[2] + 25),
                    ),
                    (pixel_x + 5, pixel_y + 1, 2, 2),
                )
            elif cell.get("variant", 0) == 3:
                pygame.draw.rect(
                    self.grid_surface,
                    "#abafb9",
                    (pixel_x + 3, pixel_y + 3, 1, 1),
                )
            # "Autotiling" (https://excaliburjs.com/blog/Autotiling%20Technique/)
            neighbors = [
                (0, -1, (0, 0, cell_size, 1)),  # Haut
                (0, 1, (0, cell_size - 1, cell_size, 1)),  # Bas
                (-1, 0, (0, 0, 1, cell_size)),  # Gauche
                (1, 0, (cell_size - 1, 0, 1, cell_size)),  # Droite
            ]
            shadow_color = (
                max(0, self.light_dirt_rgb[0] - 40),
                max(0, self.light_dirt_rgb[1] - 40),
                max(0, self.light_dirt_rgb[2] - 40),
            )
            for dx, dy, rect in neighbors:
                nx, ny = cell_x + dx, cell_y + dy
                neighbor = self.grid.get_cell(nx, ny)
                draw_shadow = False
                if neighbor:
                    if neighbor["state"] == "empty":
                        draw_shadow = True
                    elif neighbor["state"] == "partial":
                        # vérifier si les pixels adjacents dans la cellule partielle sont vides
                        bitmap = neighbor["bitmap"]
                        if bitmap:
                            has_dirt_contact = False
                            if dy == -1:
                                has_dirt_contact = any(
                                    bitmap[7][x] for x in range(cell_size)
                                )
                            elif dy == 1:
                                has_dirt_contact = any(
                                    bitmap[0][x] for x in range(cell_size)
                                )
                            elif dx == -1:
                                has_dirt_contact = any(
                                    bitmap[y][7] for y in range(cell_size)
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
                        self.grid_surface,
                        shadow_color,
                        (
                            pixel_x + rect[0],
                            pixel_y + rect[1],
                            rect[2],
                            rect[3],
                        ),
                    )

        elif state == "partial":
            # Fond galerie
            pygame.draw.rect(
                self.grid_surface,
                self.light_gal_rgb,
                (pixel_x, pixel_y, cell_size, cell_size),
            )

            bitmap = cell["bitmap"]
            if bitmap:
                shadow_color = (
                    max(0, self.light_dirt_rgb[0] - 50),
                    max(0, self.light_dirt_rgb[1] - 50),
                    max(0, self.light_dirt_rgb[2] - 50),
                )
                highlight_color = (
                    min(255, self.light_dirt_rgb[0] + 30),
                    min(255, self.light_dirt_rgb[1] + 30),
                    min(255, self.light_dirt_rgb[2] + 30),
                )

                for py in range(cell_size):
                    for px in range(cell_size):
                        if bitmap[py][px]:
                            gx = pixel_x + px
                            gy = pixel_y + py

                            pygame.draw.rect(
                                self.grid_surface, self.light_dirt_rgb, (gx, gy, 1, 1)
                            )

                            # détecter les bords pour ajouter ombrage
                            if not self.is_solid_pixel(gx, gy - 1):
                                pygame.draw.rect(
                                    self.grid_surface, highlight_color, (gx, gy, 1, 1)
                                )
                            elif not self.is_solid_pixel(gx, gy + 1):
                                pygame.draw.rect(
                                    self.grid_surface, shadow_color, (gx, gy, 1, 1)
                                )

    def draw(self):
        """
        TODO
        """
        pygame.draw.rect(
            self.world, "#7dbefa", (0, 0, COLONY_WIDTH, COLONY_GRASS_START)
        )
        # TODO: entre 0.12 et 0.15, faire l'herbe et la végétation pour la transition entre extérieur et la partie
        #  terreuse de la colonie
        pygame.draw.rect(
            self.world,
            "#4cbd56",
            (
                0,
                COLONY_GRASS_START,
                COLONY_WIDTH,
                COLONY_HEIGHT - COLONY_UNDERGROUND_START - COLONY_GRASS_START,
            ),
        )

        self.world.blit(self.grid_surface, (0, COLONY_UNDERGROUND_START))

        if self.build_mode.enabled:
            self.build_mode.draw()

        for ant in self.ants:
            ant.draw()
        for room in self.rooms:
            room.draw()

        self.game.screen.blit(self.world, (self.camera_x, self.camera_y))

        darkness = self.get_ambient_light_alpha()
        if darkness > 0:
            self.night_overlay.fill((0, 0, 50, darkness))
            self.game.screen.blit(self.night_overlay, (0, 0))
