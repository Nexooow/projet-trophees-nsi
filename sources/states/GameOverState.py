import os

from constants import SAVES_PATH, UIColors
from states.State import State


class GameOverState(State):
    def __init__(self, state_manager):
        super().__init__(state_manager, "game_over", ["pause"])
        self.game = state_manager.game
        self.stats = {}

    def set_stats(self, stats: dict):
        self.stats = stats

    def enable(self):
        super().enable()
        # Supprimer la sauvegarde si elle existe
        if self.game.game_id:
            save_path = os.sep.join([SAVES_PATH, f"{self.game.game_id}.json"])
            if os.path.exists(save_path):
                try:
                    os.remove(save_path)
                except Exception as e:
                    print(f"Erreur lors de la suppression de la sauvegarde : {e}")
            self.game.game_id = None

        self.build_ui()

    def disable(self):
        self.ui.clear()

    def update(self, events):
        self.ui.update(events)

    def draw(self):
        self.game.screen.fill(UIColors.BG)
        self.ui.draw()

    def build_ui(self):
        w, h = self.game.width, self.game.height

        panel_w = 500
        stats_count = len(self.stats) if self.stats else 1
        stats_h = stats_count * 40
        panel_h = 100 + stats_h + 80 

        x = (w - panel_w) // 2
        y = (h - panel_h) // 2

        panel = (
            self.ui.panel("game_over_panel", (x, y, panel_w, panel_h))
            .set_bg_color(UIColors.BG_DARK)
            .set_border(UIColors.BORDER, 2)
        )

        # Titre
        panel.add_child(
            self.ui.label("go_title", "GAME OVER", (0, 20, panel_w, 60))
            .set_font("assets/fonts/m5x7.ttf", 64)
            .set_text_color(UIColors.TEXT)
            .set_align("center", "center")
        )

        # Stats
        curr_y = 90
        if self.stats:
            for i, (k, v) in enumerate(self.stats.items()):
                panel.add_child(
                    self.ui.label(
                        f"go_stat_{i}", f"{k}: {v}", (20, curr_y, panel_w - 40, 30)
                    )
                    .set_font("assets/fonts/m5x7.ttf", 32)
                    .set_text_color(UIColors.TEXT_SECONDARY)
                    .set_align("center", "center")
                )
                curr_y += 40
        else:
            panel.add_child(
                self.ui.label(
                    "go_empty", "La colonie a péri...", (20, curr_y, panel_w - 40, 30)
                )
                .set_font("assets/fonts/m5x7.ttf", 32)
                .set_text_color(UIColors.TEXT_SECONDARY)
                .set_align("center", "center")
            )
            curr_y += 40

        # Bouton Retour
        btn_w = 200
        btn_h = 50
        btn_x = (panel_w - btn_w) // 2
        btn_y = panel_h - btn_h - 25

        panel.add_child(
            self.ui.button(
                "go_btn_menu", "Retour au Menu", (btn_x, btn_y, btn_w, btn_h)
            ).on("click", lambda: self.state_manager.set_state("menu"))
        )

        self.ui.add(panel)
