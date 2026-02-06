import pygame
import pygame_gui

from .State import State

class MenuState (State):

    def __init__ (self, state_manager):
        super().__init__(state_manager, "menu", ["pause"])

    def enable (self):
        self.ui.create_button("main_create_game", "Start a new game", (400, 400, 500, 500), action=lambda:print("cc"))

    def update (self, events):
        pass

    def draw (self):
        pygame.draw.rect(self.game.screen, (255, 0, 0), (0, 0, 100, 300))