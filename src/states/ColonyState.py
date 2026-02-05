import pygame
import pygame_gui

from .State import State

class ColonyState (State):

    def __init__ (self, state_manager):
        super().__init__(state_manager, "colony", [])

    def update (self, events):
        pass

    def draw (self):
        pass