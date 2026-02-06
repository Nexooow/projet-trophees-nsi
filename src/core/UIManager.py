import pygame
import pygame_gui


class UIManager:

    def __init__(self, game):
        self.game = game
        self.screen = game.screen
        
        self._ui = pygame_gui.UIManager(
            self.screen.get_size(),
            enable_live_theme_updates=True,
            # theme_path="config/ui_theme.json"
        )
        
        # TODO: helper ui pour créer des éléments d'interface plus facilement, par exemple un bouton qui prend en paramètre
        #  une fonction à appeler lors du clic, ou un champ de texte avec une validation intégrée, etc.
        
        self.elements: dict[str, any] = {}
        self.enabled_elements: list = [] # liste des identifiants des éléments affichés à l'écran
        
    def process_events (self, events):
        for event in events:
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                for id, element_data in self.elements.items():
                    if element_data["ui"] == event.ui_element:
                        element_data["exec"]()
            self._ui.process_events(event)
        
    def update (self, td):
        self._ui.update(td)
        
    def draw (self):
        self._ui.draw_ui(self.screen)

    def create_element(
        self,
        id,
        ui_element,
        action = None
    ):
        self.elements[id] = {
            "ui": ui_element,
            "exec": action
        }
        
    def create_label(
        self,
        id, text,
        rect,
    ):
        self.create_element(
            id,
            pygame_gui.elements.UILabel(relative_rect=rect, text=text, manager=self._ui)
        )

    def create_button(
        self,
        id, text,
        rect,
        action = None
    ):
        self.create_element(
            id,
            pygame_gui.elements.UIButton(relative_rect=pygame.Rect(rect), text=text, manager=self._ui),
            action=action
        )
