import math

import numpy as np
import pygame
from pygame.typing import ColorLike
import pygame_gui

from colony.Ant import Ant
from colony.ants.Worker import Worker
from colony.BuildMode import BuildMode
from colony.Room import Room
from colony.rooms.Depot import Depot
from colony.TaskManager import TaskManager
from config.settings import (
    colony_brush_color,
    colony_brush_size,
    colony_height,
    colony_underground_start,
    colony_width,
    dark_dirt_color,
    dirt_color,
)
from utils.grid import Grid

from .State import State


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

        self.grid_surface = pygame.Surface((colony_width, colony_height-colony_underground_start), pygame.SRCALPHA)
        self.grid = Grid(self.grid_surface.get_size())
        grid_x_center = self.grid.width // 2
        
        self.rooms = [
            Depot(self, {"x": grid_x_center, "y": 0, "width": 13, "height": 7})
        ]

        self.ants = [Worker(self, {"power": 1}, (100, 100))]
        # self.ennemies = []

        self.food = 0
        # self.science = 0
        
        self.generate_grid()

    def get_room_coords(self, room_name):
        """
        Renvoie les coordonnées d'une pièce
        """
        return 0  # TODO

    def update(self, events):
        keys = pygame.key.get_pressed()
        screen_width, screen_height = self.game.screen.get_size()

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_b:
                    self.build_mode.switch()

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
            
    def draw_ui (self):
        """
        Dessine l'interface utilisateur
        """
        pass
        
    def generate_grid (self):
        """
        Dessine la grille de la colonie sur une surface dédiée, pour éviter de surcharger la fonction draw.
        Avant, on dessinait la grille à chaque appel de draw, de plus, on observe maintenant un passage de 50fps à 60fps.
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

        for cell_x, cell_y, cell in self.grid:
            state = cell["state"]

            # Coordonnées pixel de la cellule
            pixel_x, pixel_y = self.grid.cell_to_pixel(cell_x, cell_y)

            if state == "full":
                # Dessiner la cellule entière
                pygame.draw.rect(
                    self.grid_surface,
                    dirt_color,
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
                                    dirt_color,
                                    (pixel_x + bmp_x, pixel_y + bmp_y, 1, 1),
                                )
                                
    def draw(self):
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
        # TODO: dessiner le bruit de perlin comme filtre semi-transparent au dessus de la grid

        if self.build_mode.enabled:
            self.build_mode.draw()

        for ant in self.ants:
            ant.draw()
        for room in self.rooms:
            room.draw()

        self.game.screen.blit(self.world, (self.camera_x, self.camera_y))
