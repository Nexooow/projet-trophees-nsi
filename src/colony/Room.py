import math
import typing

import pygame

from constants import COLONY_UNDERGROUND_START

if typing.TYPE_CHECKING:
    from core.GameManager import GameManager
    from states.ColonyState import ColonyState


class Room(pygame.sprite.Sprite):
    def __init__(self, colony: "ColonyState", name: str, config: dict):
        super().__init__()
        self.colony: "ColonyState" = colony
        self.game: "GameManager" = colony.game
        self.name = name

        self.x = config["x"] * 8
        self.y = config["y"] * 8 + COLONY_UNDERGROUND_START
        self.width = config["width"] * 8
        self.height = config["height"] * 8

        raw = config.get("entry_offset")
        if raw is not None:
            self.entry_offset: typing.Tuple[int, int] = (int(raw[0]), int(raw[1]))
        else:
            self.entry_offset = (self.width // 2, self.height // 2)

        for x in range(config["x"], config["x"] + config["width"]):
            for y in range(config["y"], config["y"] + config["height"]):
                if f"{x - self.x},{y - self.y}" in config["walkable"]:
                    self.colony.grid.set_cell_state(x, y, "occupied_walkable")
                else:
                    self.colony.grid.set_cell_state(x, y, "occupied")

        self.image = pygame.Surface((self.width, self.height))
        self.rect = self.image.get_rect(topleft=(self.x, self.y))
        pygame.draw.rect(self.image, (255, 0, 0), self.rect)

    def get_pos(self):
        return (self.x, self.y)

    def get_center(self):
        x = self.x + self.width // 2
        y = self.y + self.height // 2
        return (x, y)

    def get_entry(self) -> typing.Tuple[int, int]:
        """Retourne la position absolue (pixels) de l'entrée de la salle."""
        return (self.x + self.entry_offset[0], self.y + self.entry_offset[1])

    def get_passable_entry(self) -> typing.Optional[typing.Tuple[int, int]]:
        """
        Retourne les coordonnées pixel du centre de la cellule passable
        la plus proche de l'entrée de la salle, en cherchant en spirale
        autour du point d'entrée et en excluant les cellules appartenant
        à la salle elle-même.
        """
        grid = self.colony.grid
        entry_x, entry_y = self.get_entry()

        # Convertir l'entrée en coordonnées de cellule (hors offset start_y)
        cell_x = entry_x // grid.CELL_SIZE
        cell_y = (entry_y - grid.start_y) // grid.CELL_SIZE

        # Limites de la salle en coordonnées de cellule
        room_cell_x1 = self.x // grid.CELL_SIZE
        room_cell_y1 = (self.y - grid.start_y) // grid.CELL_SIZE
        room_cell_x2 = (self.x + self.width - 1) // grid.CELL_SIZE
        room_cell_y2 = (self.y + self.height - 1 - grid.start_y) // grid.CELL_SIZE

        # Cherche en spirale croissante la cellule passable la plus proche
        for radius in range(0, 20):
            candidates = []
            for dx in range(-radius, radius + 1):
                for dy in range(-radius, radius + 1):
                    if abs(dx) != radius and abs(dy) != radius:
                        continue
                    nx, ny = cell_x + dx, cell_y + dy
                    if not (0 <= nx < grid.width and 0 <= ny < grid.height):
                        continue
                    # Exclure les cellules appartenant à la salle
                    if (
                        room_cell_x1 <= nx <= room_cell_x2
                        and room_cell_y1 <= ny <= room_cell_y2
                    ):
                        continue
                    if grid.is_cell_passable(nx, ny):
                        dist = math.sqrt(dx * dx + dy * dy)
                        candidates.append((dist, nx, ny))
            if candidates:
                candidates.sort()
                _, best_x, best_y = candidates[0]
                pixel_x = best_x * grid.CELL_SIZE + grid.CELL_SIZE // 2
                pixel_y = best_y * grid.CELL_SIZE + grid.CELL_SIZE // 2 + grid.start_y
                return (pixel_x, pixel_y)

        return None

    def update(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                world_mouse_pos = (
                    event.pos[0] - self.colony.camera_x,
                    event.pos[1] - self.colony.camera_y,
                )
                if self.rect and self.rect.collidepoint(world_mouse_pos):
                    self.interact()
        self.update_self(events)

    def interact(self):
        raise NotImplementedError(
            f"méthode Room::interact non implémenté pour {self.__class__.__name__}"
        )

    def update_self(self, events):
        raise NotImplementedError(
            f"méthode Room::update_self non implémenté pour {self.__class__.__name__}"
        )

    def draw(self):
        if self.image:
            self.colony.world.blit(self.image, (self.x, self.y))
