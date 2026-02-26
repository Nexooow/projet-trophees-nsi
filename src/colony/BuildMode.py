import pygame
import math
import typing

from lib.ui import Button, Label, UIColors
from constants import (
    COLONY_BRUSH_COLOR,
    COLONY_BRUSH_SIZE,
    COLONY_HEIGHT,
    COLONY_UNDERGROUND_START,
    COLONY_WIDTH,
    PRICE_PER_DIRTPIXEL,
)

if typing.TYPE_CHECKING:
    from states.ColonyState import ColonyState


class BuildMode:
    def __init__(self, colony_state: "ColonyState"):
        self.colony = colony_state
        self.ui = colony_state.ui
        self.enabled = False
        self.selections = set()
        self.builds = []
        
    def get_dug_pixels (self) -> int:
        """
        Retourne une approximation du nombre de pixels qui vont être creusés.
        Permet de calculer le coût en nourriture de la construction.
        """
        count = 0
        for x, y in self.selections:
            count += math.pi * (COLONY_BRUSH_SIZE / 2) ** 2
        return math.ceil(count)
        
    def get_price (self):
        """
        Retourne le coût approximatif en nourriture de la construction.
        """
        return self.get_dug_pixels() * PRICE_PER_DIRTPIXEL + 0 # TODO: remplacer 0 par le cout de la construction des salles
        
    def switch(self):
        assert self.colony.sidebar is not None
        sidebar = self.colony.sidebar
        
        self.enabled = not self.enabled
        btn = self.ui.get("colony_btn_build")
        if isinstance(btn, Button):
            if self.enabled:                
                btn.set_colors(
                    normal=UIColors.GREEN, hover=UIColors.DARK_GREEN
                )
            else:
                btn.set_colors(normal=UIColors.BTN_BG, hover=UIColors.BTN_BG_HOVER)
        
        if self.enabled:
            sidebar.set_content(
                self.ui.panel(
                    "colony_sidebar_build",
                    (4, 4, sidebar.width-4*2, sidebar.height-4*2)
                ).set_border(None, 0).add_children([
                    self.ui.label("colony_sidebar_build_title", "Construction", (4, 6, sidebar.width-8*2, 30)).set_font_size(36).set_align("center", "center"),
                    # TODO: prix galeries + salles
                    self.ui.button(
                        "colony_sidebar_build_cancel",
                        "Annuler", 
                        (4, sidebar.height-46-30-4, sidebar.width-8*2, 30)
                    ).set_font_size(24).set_align("center", "center").on("click", self.cancel_build),
                    self.ui.button(
                        "colony_sidebar_build_start",
                        "Démarrer la construction", 
                        (4, sidebar.height-46, sidebar.width-8*2, 30)
                    ).set_font_size(24).set_align("center", "center").on("click", self.start_build)
                ]).set_z_index(13) 
            )
            sidebar.show()
        else:
            sidebar.hide()
        
    def update(self, events):
        self.sync_ui()
        
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:  # clear
                    self.selections.clear()
                elif event.key == pygame.K_KP_ENTER:
                    pass  # TODO

        if pygame.mouse.get_pressed()[2]:
            mouse_pos = pygame.mouse.get_pos()
            mouse_pos = (
                mouse_pos[0] - self.colony.camera_x,
                mouse_pos[1] - self.colony.camera_y,
            )
            if (
                mouse_pos[0] >= 0
                and mouse_pos[0] < COLONY_WIDTH
                and mouse_pos[1] >= 0
                and mouse_pos[1] < COLONY_HEIGHT
                and mouse_pos[1] > COLONY_UNDERGROUND_START + COLONY_BRUSH_SIZE
            ):
                brush_x = mouse_pos[0] - COLONY_BRUSH_SIZE // 2
                brush_y = mouse_pos[1] - COLONY_BRUSH_SIZE // 2
                self.selections.add((brush_x, brush_y))
                
    def sync_ui (self):
        pass

    def draw(self):
        mouse_pos = pygame.mouse.get_pos()
        mouse_world_pos = (
            mouse_pos[0] - self.colony.camera_x,
            mouse_pos[1] - self.colony.camera_y,
        )

        radius = COLONY_BRUSH_SIZE / 2

        for x, y in self.selections:
            center_x = x + radius
            center_y = y + radius
            pygame.draw.circle(
                self.colony.world,
                COLONY_BRUSH_COLOR,
                (center_x, center_y),
                radius,
            )

        if (
            mouse_world_pos[0] >= 0
            and mouse_world_pos[0] < COLONY_WIDTH
            and mouse_world_pos[1] >= 0
            and mouse_world_pos[1] < COLONY_HEIGHT
            and mouse_world_pos[1] > COLONY_UNDERGROUND_START + COLONY_BRUSH_SIZE
        ):
            brush_x = mouse_world_pos[0]
            brush_y = mouse_world_pos[1]

            pygame.draw.circle(
                self.colony.world,
                COLONY_BRUSH_COLOR,
                (brush_x, brush_y),
                radius,
            )

    def start_build (self):
        """
        Commence la construction.
        """
        # TODO: ICI, lancer la construction, et ajouter les tâches
        self.selections.clear()
        self.switch()
        
    def cancel_build (self):
        """
        Annule la construction.
        """
        self.selections.clear()
        self.switch()
