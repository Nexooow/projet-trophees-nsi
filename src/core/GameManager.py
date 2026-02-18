import pygame

from .EventManager import EventManager

# import pygame_gui
from .StateManager import StateManager
from .TimeManager import TimeManager
from lib.ui import UIManager

class GameManager:
    def __init__(self):
        self.running = True

        self.screen = pygame.display.set_mode(
            (0, 0),
            pygame.FULLSCREEN
            | pygame.SRCALPHA
            | pygame.HWSURFACE,  # plein écran, support de la transparence, accélération matérielle
        )
        self.width, self.height = self.screen.get_size()
        self.clock = pygame.time.Clock()
        
        self.ui = UIManager(self)
        self.state = StateManager(self)
        self.time = TimeManager(self)
        # self.events = EventManager(self)

    def is_running(self) -> bool:
        """
        Renvoie si le jeu est en cours d'exécution.
        """
        return self.running

    def update(self, events):
        """
        Met à jour le jeu et délègue les événements.
        """
        self.time.add_frame()
        self.ui.update(events)
        self.state.update(events)
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False

    def draw(self):
        self.screen.fill((255, 255, 255))
        self.state.draw()
        self.ui.draw()
