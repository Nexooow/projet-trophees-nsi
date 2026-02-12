import math

import pygame
import pygame_gui

from colony.TaskManager import TaskManager
from config.settings import colony_height, colony_underground_start, colony_width, colony_brush_size, colony_brush_color
from utils.grid import Grid

from .State import State


class ColonyState(State):
    def __init__(self, state_manager):
        super().__init__(state_manager, "colony", [])
        self.tasks = TaskManager(self)

        self.world = pygame.Surface(
            (colony_width, colony_height), pygame.SRCALPHA | pygame.HWSURFACE
        )
        self.camera_x = 0
        self.camera_y = 0
        
        self.build_mode = False

        self.grid = Grid(colony_underground_start, self.world.get_size())
        self.rooms = []

        self.ants = []
        # self.ennemies = []

        self.food = 0
        # self.science = 0
        
        self.selections = set()

    def draw_grid(self):
        """Dessine la grille en tenant compte des cellules 8x8 avec états et bitmaps"""
        for cell_x, cell_y, cell in self.grid:
            state = cell["state"]

            # Coordonnées pixel de la cellule
            pixel_x, pixel_y = self.grid.cell_to_pixel(cell_x, cell_y)
            pixel_y += colony_underground_start

            if state == "full":
                # Dessiner la cellule entière
                pygame.draw.rect(
                    self.world,
                    (82, 40, 23),
                    (pixel_x, pixel_y, self.grid.CELL_SIZE, self.grid.CELL_SIZE),
                )
            elif state == "partial":
                # Dessiner uniquement les pixels pleins du bitmap
                bitmap = cell["bitmap"]
                if bitmap:
                    for bmp_y in range(self.grid.CELL_SIZE):
                        for bmp_x in range(self.grid.CELL_SIZE):
                            if bmp_y < len(bitmap) and bmp_x < len(bitmap[bmp_y]):
                                if bitmap[bmp_y][bmp_x]:
                                    pygame.draw.rect(
                                        self.world,
                                        (82, 40, 23),
                                        (pixel_x + bmp_x, pixel_y + bmp_y, 1, 1),
                                    )

    def update(self, events):
        keys = pygame.key.get_pressed()
        screen_width, screen_height = self.game.screen.get_size()
        
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_b:
                    self.build_mode = not self.build_mode
                elif event.key == pygame.K_c and self.build_mode:
                    self.selections.clear()
                elif event.key == pygame.K_KP_ENTER and self.build_mode:
                    self.tasks.to_dig = list(self.selections)
                

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
            
        if self.build_mode and pygame.mouse.get_pressed()[2]:
            mouse_pos = pygame.mouse.get_pos()
            mouse_pos = (mouse_pos[0] - self.camera_x, mouse_pos[1] - self.camera_y)
            if (
                mouse_pos[0] >= 0
                and mouse_pos[0] < colony_width
                and mouse_pos[1] >= 0
                and mouse_pos[1] < colony_height
                and mouse_pos[1] > colony_underground_start+colony_brush_size
            ):
                brush_x = mouse_pos[0] - colony_brush_size // 2
                brush_y = mouse_pos[1] - colony_brush_size // 2
                self.selections.add((brush_x, brush_y))

    def draw(self):
        pygame.draw.rect(
            self.world, (66, 179, 213), (0, 0, colony_width, colony_height * 0.12)
        )
        # TODO: entre 0.12 et 0.15, faire l'herbe et la végétation pour la transition entre extérieur et la partie
        #  terreuse de la colonie
        pygame.draw.rect(
            self.world,
            (64, 125, 42),
            (0, colony_height * 0.12, colony_width, colony_height * 0.04),
        )
        pygame.draw.rect(
            self.world,
            (66, 31, 17),
            (0, colony_height * 0.15, colony_width, colony_height * 0.85),
        )
        self.draw_grid()
        # TODO: dessiner le bruit de perlin comme filtre semi-transparent au dessus de la grid

        # Dessiner l'indicateur de la brush
        mouse_pos = pygame.mouse.get_pos()
        mouse_world_pos = (mouse_pos[0] - self.camera_x, mouse_pos[1] - self.camera_y)
            
        if self.build_mode:
            for (x, y) in self.selections:
                pygame.draw.rect(self.world, colony_brush_color, (x, y, colony_brush_size, colony_brush_size))
            
        self.game.screen.blit(self.world, (self.camera_x, self.camera_y))
        
        if (
            self.build_mode
            and mouse_world_pos[0] >= 0
            and mouse_world_pos[0] < colony_width
            and mouse_world_pos[1] >= 0
            and mouse_world_pos[1] < colony_height
            and mouse_world_pos[1] > colony_underground_start+colony_brush_size
        ):
            brush_x = mouse_world_pos[0] - colony_brush_size // 2
            brush_y = mouse_world_pos[1] - colony_brush_size // 2

            # Dessiner le carré de la brush sur l'écran et non le monde
            screen_brush_x = brush_x + self.camera_x
            screen_brush_y = brush_y + self.camera_y

            pygame.draw.rect(self.game.screen, colony_brush_color, (screen_brush_x, screen_brush_y, colony_brush_size, colony_brush_size))