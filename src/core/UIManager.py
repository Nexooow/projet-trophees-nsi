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
                for identifiant, element_data in self.elements.items():
                    if element_data["ui"] == event.ui_element:
                        element_data["exec"]()
            self._ui.process_events(event)
        
    def update (self, events, td):
        for event in events:
            self._ui.process_events(event)
        self._ui.update(td)
        
    def draw (self):
        self._ui.draw_ui(self.screen)

    def enable_element(self, identifiant):
        """Affiche un élément caché"""
        if identifiant in self.elements and identifiant not in self.enabled_elements:
            self.enabled_elements.append(identifiant)
            self.elements[identifiant]["ui"].show()

    def disable_element(self, identifiant):
        """Cache un élément sans le supprimer"""
        if identifiant in self.enabled_elements:
            self.enabled_elements.remove(identifiant)
            self.elements[identifiant]["ui"].hide()

    def delete_element(self, identifiant):
        """Supprime définitivement un élément"""
        if identifiant in self.elements:
            self.elements[identifiant]["ui"].kill()
            del self.elements[identifiant]
            if identifiant in self.enabled_elements:
                self.enabled_elements.remove(identifiant)

    def get_element(self, identifiant):
        """Récupère un élément par son identifiant"""
        return self.elements.get(identifiant, {}).get("ui")

    def element_exists(self, identifiant):
        """Vérifie si un élément existe"""
        return identifiant in self.elements

    def clear(self):
        """Supprime tous les éléments de l'interface"""
        for identifiant in list(self.elements.keys()):
            self.delete_element(identifiant)
        self.enabled_elements.clear()

    def create_element(
        self,
        identifiant,
        ui_element,
        action = None
    ):
        """
        Logique de création d'un élément d'interface
        """
        if identifiant not in self.elements:
            self.elements[identifiant] = {
                "ui": ui_element,
                "exec": action
            }
        elif self.elements[identifiant]["ui"] != ui_element:
            self.elements[identifiant]["ui"].kill()
            self.elements[identifiant] = {
                "ui": ui_element,
                "exec": action
            }
        
    def create_label(
        self,
        identifiant, text,
        rect,
    ):
        """
        Crée un label (affichage de texte)
        """
        self.create_element(
            identifiant,
            pygame_gui.elements.UILabel(relative_rect=rect, text=text, manager=self._ui)
        )

    def create_button(
        self,
        identifiant, text,
        rect,
        action = None
    ):
        """
        Crée un bouton
        """
        self.create_element(
            identifiant,
            pygame_gui.elements.UIButton(relative_rect=pygame.Rect(rect), text=text, manager=self._ui),
            action=action
        )

    def create_text_entry(
        self,
        identifiant,
        rect,
        placeholder="",
        initial_text=""
    ):
        """
        Crée un champ de saisie de texte
        """
        element = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect(rect),
            manager=self._ui,
            placeholder_text=placeholder
        )
        if initial_text:
            element.set_text(initial_text)
        self.create_element(identifiant, element)

    def create_text_box(
        self,
        identifiant,
        html_text,
        rect
    ):
        """
        Crée une zone de texte
        """
        self.create_element(
            identifiant,
            pygame_gui.elements.UITextBox(
                html_text=html_text,
                relative_rect=pygame.Rect(rect),
                manager=self._ui
            )
        )

    def create_dropdown(
        self,
        identifiant,
        options,
        rect,
        starting_option=None
    ):
        """
        Crée un menu déroulant
        """
        self.create_element(
            identifiant,
            pygame_gui.elements.UIDropDownMenu(
                options_list=options,
                starting_option=starting_option or options[0],
                relative_rect=pygame.Rect(rect),
                manager=self._ui
            )
        )

    def create_horizontal_slider(
        self,
        identifiant,
        rect,
        start_value,
        value_range,
        action=None
    ):
        """
        Crée un slider horizontal
        """
        self.create_element(
            identifiant,
            pygame_gui.elements.UIHorizontalSlider(
                relative_rect=pygame.Rect(rect),
                start_value=start_value,
                value_range=value_range,
                manager=self._ui
            ),
            action=action
        )

    def create_panel(
        self,
        identifiant,
        rect,
        starting_layer_height=1
    ):
        """
        Crée un panneau conteneur
        """
        self.create_element(
            identifiant,
            pygame_gui.elements.UIPanel(
                relative_rect=pygame.Rect(rect),
                starting_height=starting_layer_height,
                manager=self._ui
            )
        )

    def create_image(
        self,
        identifiant,
        image_surface,
        rect
    ):
        """
        Crée un élément image
        """
        self.create_element(
            identifiant,
            pygame_gui.elements.UIImage(
                relative_rect=pygame.Rect(rect),
                image_surface=image_surface,
                manager=self._ui
            )
        )

    def create_selection_list(
        self,
        identifiant,
        item_list,
        rect,
        allow_multi_select=False
    ):
        """
        Crée une liste de sélection
        """
        self.create_element(
            identifiant,
            pygame_gui.elements.UISelectionList(
                relative_rect=pygame.Rect(rect),
                item_list=item_list,
                manager=self._ui,
                allow_multi_select=allow_multi_select
            )
        )

    def get_text_entry_value(self, identifiant):
        """
        Récupère le texte d'un champ de saisie
        """
        element = self.get_element(identifiant)
        if element and isinstance(element, pygame_gui.elements.UITextEntryLine):
            return element.get_text()
        return None

    def get_dropdown_value(self, identifiant):
        """
        Récupère la valeur sélectionnée d'un dropdown
        """
        element = self.get_element(identifiant)
        if element and isinstance(element, pygame_gui.elements.UIDropDownMenu):
            return element.selected_option
        return None

    def get_slider_value(self, identifiant):
        """
        Récupère la valeur d'un slider
        """
        element = self.get_element(identifiant)
        if element and isinstance(element, pygame_gui.elements.UIHorizontalSlider):
            return element.get_current_value()
        return None

    def set_label_text(self, identifiant, new_text):
        """
        Modifie le texte d'un label
        """
        element = self.get_element(identifiant)
        if element and isinstance(element, pygame_gui.elements.UILabel):
            element.set_text(new_text)

    def set_button_text(self, identifiant, new_text):
        """
        Modifie le texte d'un bouton
        """
        element = self.get_element(identifiant)
        if element and isinstance(element, pygame_gui.elements.UIButton):
            element.set_text(new_text)
