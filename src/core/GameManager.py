import pygame
# import pygame_gui

from .StateManager import StateManager
from .TimeManager import TimeManager
from .EventManager import EventManager
from .UIManager import UIManager
from utils.saves import Save

class GameManager:

    def __init__ (self):
        self.running = True

        self.screen = pygame.display.set_mode(
            (0, 0),
            pygame.FULLSCREEN | pygame.SRCALPHA | pygame.HWSURFACE, # plein écran, support de la transparence, accélération matérielle
        )
        self.width, self.height = self.screen.get_size()
        self.clock = pygame.time.Clock()

        self.ui = UIManager(self)
        self.state = StateManager(self)
        self.time = TimeManager(self)
        self.events = EventManager(self)

    def is_running (self) -> bool:
        """
        Renvoie si le jeu est en cours d'exécution.
        """
        return self.running

    def update (self, events):
        """
        Met à jour le jeu et délègue les événements.
        """
        time_delta = self.clock.tick(60) / 1000.0
        self.time.add_frame()
        self.state.update(events)
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
        self.ui.update(events, time_delta)

    def draw (self):
        self.screen.fill((255, 255, 255))
        self.state.draw()
        # TODO: dessiner les effets ici, fade-in, fade-out ...
        self.ui.draw()