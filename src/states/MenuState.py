import pygame
import pygame_gui

from .State import State

class MenuState (State):

    def __init__ (self, state_manager):
        super().__init__(state_manager, "menu", ["pause"])

    def enable (self):
        pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(0, 0, 100, 300),
            text="Create a new game",
            manager=self.game.ui,
        )

    def update (self, events):
        pass

    def draw (self):
        pygame.draw.rect(self.game.screen, (255, 0, 0), (0, 0, 100, 300))