import typing

import pygame

from lib.ui import UIManager

from .EventManager import EventManager
from .SaveManager import SaveManager

# import pygame_gui
from .StateManager import StateManager
from .TimeManager import TimeManager


class GameManager:
    def __init__(self):
        self.running = True

        self.screen = pygame.display.set_mode(
            (0, 0),
            pygame.FULLSCREEN | pygame.SRCALPHA,
        )
        self.width, self.height = self.screen.get_size()
        self.clock = pygame.time.Clock()

        self.game_id: typing.Optional[str] = None

        self.ui = UIManager(self)
        self.time = TimeManager(self)
        self.save = SaveManager(self)
        self.state = StateManager(self)
        # self.events = EventManager(self)

    def is_game_started(self) -> bool:
        return self.game_id is not None

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

    def sauvegarder(self, save_id: typing.Optional[str] = None) -> str:
        """
        Sauvegarde l'état courant du jeu dans un fichier JSON.
        Retourne le save_id utilisé.
        """
        return self.save.sauvegarder(save_id)

    def restaurer(self, save_id: typing.Optional[str] = None) -> bool:
        """
        Restaure une partie depuis un fichier JSON.
        Si save_id est None, charge la sauvegarde la plus récente.
        Retourne True si la restauration a réussi.
        """
        success = self.save.restaurer(save_id)
        if success:
            # S'assurer qu'on est bien dans l'état colony après restauration
            if self.state.current_state != "colony":
                self.state.set_state("colony")
        return success

    def trigger_game_over(self, reason: str):
        pass  # TODO: gérer la fin du jeu
