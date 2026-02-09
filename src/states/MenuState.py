import pygame
import pygame_gui

from .State import State

class MenuState (State):

    def __init__ (self, state_manager):
        super().__init__(state_manager, "menu", ["pause"])

    def enable (self):
        # Récupération de la taille de l'écran
        screen_width, screen_height = self.game.screen.get_size()

        # Dimensions des boutons
        button_width = 400
        button_height = 60
        button_spacing = 20

        # Position centrée horizontalement
        x = (screen_width - button_width) // 2

        # Position de départ verticale (centrée)
        total_height = (button_height * 4) + (button_spacing * 3)
        start_y = (screen_height - total_height) // 2

        # Titre du menu
        title_rect = pygame.Rect(
            (screen_width - 600) // 2,
            start_y - 150,
            600,
            100
        )
        self.ui.create_label(
            "menu_title",
            "<font size=6><b>Menu Principal</b></font>",
            title_rect
        )

        # Bouton Créer une partie
        self.ui.create_button(
            "menu_new_game",
            "Créer une partie",
            (x, start_y, button_width, button_height),
            action=lambda: print("Créer une partie")
        )

        # Bouton Charger une partie
        self.ui.create_button(
            "menu_load_game",
            "Charger une partie",
            (x, start_y + button_height + button_spacing, button_width, button_height),
            action=lambda: print("Charger une partie")
        )

        # Bouton Paramètres
        self.ui.create_button(
            "menu_settings",
            "Paramètres",
            (x, start_y + (button_height + button_spacing) * 2, button_width, button_height),
            action=lambda: print("Paramètres")
        )

        # Bouton Quitter
        self.ui.create_button(
            "menu_quit",
            "Quitter",
            (x, start_y + (button_height + button_spacing) * 3, button_width, button_height),
            action=lambda: print("Quitter")
        )

    def update (self, events):
        pass

    def draw (self):
        # Fond d'écran du menu
        self.game.screen.fill((30, 30, 40))