import pygame
import pygame_gui

from base.anthill.Anthill import Anthill
from base.TimeManager import TimeManager

class Jeu:
    
    def __init__ (self):
        self.running = True
        
        self.mode = "main" # main / anthill / expedition 
        self.anthill = Anthill()
        self.time = TimeManager()
        
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.ui = pygame_gui.UIManager(self.screen.get_size(), enable_live_theme_updates=True)
        
    def is_running (self):
        return self.running
    
    def update (self, events):
        pass
    
    def draw (self):
        pass
    