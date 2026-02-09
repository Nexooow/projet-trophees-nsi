import pygame

class Room (pygame.sprite.Sprite):

    def __init__ (self, game, name: str):
        super().__init__()
        self.game = game
        self.name = name