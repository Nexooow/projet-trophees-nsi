import pygame

from constants import COLONY_UNDERGROUND_START


class Room(pygame.sprite.Sprite):
    def __init__(self, colony, name: str, config: dict):
        super().__init__()
        self.colony = colony
        self.name = name

        self.x = config["x"] * 8
        self.y = config["y"] * 8 + COLONY_UNDERGROUND_START
        self.width = config["width"] * 8
        self.height = config["height"] * 8

        for x in range(config["x"], config["x"] + config["width"]):
            for y in range(config["y"], config["y"] + config["height"]):
                if f"{x},{y}" in config["walkable"]:
                    self.colony.grid.set_cell_state(x, y, "occupied_walkable")
                else:
                    self.colony.grid.set_cell_state(x, y, "occupied")

        self.image = pygame.Surface((self.width, self.height))
        self.rect = self.image.get_rect()
        pygame.draw.rect(self.image, (255, 0, 0), self.rect)

    def get_pos(self):
        return (self.x, self.y)

    def get_center(self):
        x = self.x + self.width // 2
        y = self.y + self.height // 2
        return (x, y)

    def update(self, events):
        # TODO: gestion collision avec souris
        if hasattr(self, "update_self"):
            self.update_self(events)
            
    def update_self(self, events):
        raise NotImplementedError(f"méthode Room::update_self non implémenté pour {self.__class__.__name__}")

    def draw(self):
        self.colony.world.blit(self.image, (self.x, self.y))
