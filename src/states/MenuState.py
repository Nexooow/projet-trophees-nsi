import pygame

from constants import UIColors

from .State import State


class MenuState(State):
    def __init__(self, state_manager):
        super().__init__(state_manager, "menu", ["pause"])

    def enable(self):
        w, h = self.game.width, self.game.height

        self.ui.label(
            "menu_title",
            "NOM JEU",
            (0, h // 6, w, 80),
        ).set_font("assets/fonts/m5x7.ttf", 96).set_text_color(UIColors.TEXT).set_align(
            "center", "center"
        )

        self.ui.label(
            "menu_subtitle",
            "Sous titre ici",
            (0, h // 6 + 90, w, 36),
        ).set_font("assets/fonts/monogram.ttf", 28).set_text_color(
            (180, 160, 130)
        ).set_align("center", "center")

        btn_w, btn_h = 260, 52
        btn_x = (w - btn_w) // 2
        spacing = btn_h + 16

        panel_padding = 32
        panel_h = spacing * 3 + panel_padding * 2 - 16
        panel_y = h // 2 - 20

        self.ui.panel(
            "menu_panel",
            (
                btn_x - panel_padding,
                panel_y - panel_padding,
                btn_w + panel_padding * 2,
                panel_h,
            ),
        ).set_z_index(0)

        self.ui.button(
            "btn_new_game",
            "Nouvelle partie",
            (btn_x, panel_y, btn_w, btn_h),
        ).on("click", self.on_new_game).set_z_index(1)

        self.ui.button(
            "btn_continue",
            "Continuer",
            (btn_x, panel_y + spacing, btn_w, btn_h),
        ).on("click", self.on_continue).set_z_index(1)

        self.ui.button(
            "btn_quit",
            "Quitter",
            (btn_x, panel_y + spacing * 2, btn_w, btn_h),
        ).set_colors(
            normal=(110, 40, 40),
            hover=(150, 55, 55),
            active=(180, 65, 65),
        ).on("click", self.on_quit).set_z_index(1)

        self.ui.label(
            "menu_version",
            "Trophees NSI  -  2026",
            (0, h - 36, w, 28),
        ).set_font("assets/fonts/monogram.ttf", 20).set_text_color(
            (100, 85, 70)
        ).set_align("center", "center")

    def disable(self):
        self.ui.clear()

    def update(self, events):
        self.ui.update(events)

    def draw(self):
        self.game.screen.fill("#28192f")

        # Ligne décorative sous le titre
        line_y = self.game.height // 6 + 135
        pygame.draw.line(
            self.game.screen,
            UIColors.BORDER,
            (self.game.width // 2 - 140, line_y),
            (self.game.width // 2 + 140, line_y),
            1,
        )

    def on_new_game(self):
        self.game.state.set_state("colony")

    def on_continue(self):
        # TODO: charger une sauvegarde existante
        self.game.state.set_state("colony")

    def on_quit(self):
        self.game.running = False
