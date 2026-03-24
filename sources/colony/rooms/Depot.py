from colony.Room import Room
from lib.ui import UIColors

PADDING = 6
GAP = 6
TITLE_HEIGHT = 36
TITLE_FONT_SIZE = 42


class Depot(Room):
    def __init__(self, colony, data):
        super().__init__(
            colony,
            "depot",
            {**data, "walkable": []},
        )
        self.level = 1
        self.capacity_bonus = 1000

    def upgrade(self):
        upgrade_cost = self.level * 2000
        if self.colony.food >= upgrade_cost:
            self.colony.food -= upgrade_cost
            self.level += 1
            self.colony.food_capacity += self.capacity_bonus
            self.interact()  # Refresh UI

    def update_self(self, events):
        pass

    def interact(self):
        sidebar = self.colony.sidebar
        assert sidebar is not None

        panel_w = sidebar.width
        panel_h = sidebar.height
        inner_w = panel_w - PADDING * 2

        y_title = PADDING
        y_inv = y_title + TITLE_HEIGHT + GAP

        ui = self.colony.ui
        root = (
            ui.panel(
                "depot_root",
                (0, 0, panel_w, panel_h),
            )
            .set_border(None, 0)
            .set_bg_color(UIColors.BG_DARK)
        )

        root.add_child(
            ui.label(
                "depot_title",
                "Dépôt",
                (PADDING, y_title, inner_w, TITLE_HEIGHT),
            )
            .set_font_size(TITLE_FONT_SIZE)
            .set_align("center", "center")
        )

        root.add_child(
            ui.label(
                "depot_stats",
                f"Niveau: {self.level} | Capacité: {self.colony.food}/{self.colony.food_capacity}",
                (PADDING, y_inv, inner_w, 20),
            )
            .set_font_size(24)
            .set_align("center", "center")
        )

        y_upgrade = y_inv + 30
        upgrade_cost = self.level * 2000
        root.add_child(
            ui.button(
                "depot_upgrade",
                f"Améliorer ({upgrade_cost} Nourriture)",
                (PADDING, y_upgrade, inner_w, 40),
            ).on("click", self.upgrade)
        )

        y_inv_panel = y_upgrade + 50
        root.add_child(
            ui.scrollable_panel(
                "depot_inventory",
                (
                    PADDING,
                    y_inv_panel,
                    panel_w - PADDING * 2,
                    panel_h - (y_inv_panel + PADDING),
                ),
            )  # TODO: ajouter les éléments de l'inventaire
        )

        sidebar.set_content(root)
        sidebar.show()
