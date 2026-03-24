from colony.Room import Room
from lib.ui import UIColors

PADDING = 6
GAP = 6
TITLE_HEIGHT = 36
TITLE_FONT_SIZE = 42


class Dormitory(Room):
    """
    Salle permettant aux fourmis de récupérer leur énergie plus rapidement.
    """

    def __init__(self, colony, data):
        super().__init__(
            colony,
            "dormitory",
            {**data, "walkable": []},
        )
        self.level = 1

    def update_self(self, events):
        pass

    def interact(self):
        sidebar = self.colony.sidebar
        assert sidebar is not None

        panel_w = sidebar.width
        panel_h = sidebar.height
        inner_w = panel_w - PADDING * 2

        ui = self.colony.ui
        root = (
            ui.panel("dormitory_root", (0, 0, panel_w, panel_h))
            .set_border(None, 0)
            .set_bg_color(UIColors.BG_DARK)
        )

        root.add_child(
            ui.label("dorm_title", "Dortoir", (PADDING, PADDING, inner_w, TITLE_HEIGHT))
            .set_font_size(TITLE_FONT_SIZE)
            .set_align("center", "center")
        )

        root.add_child(
            ui.label(
                "dorm_desc",
                "Les fourmis s'y reposent pour regagner de l'énergie.",
                (PADDING, PADDING + TITLE_HEIGHT + GAP, inner_w, 60),
            )
            .set_font_size(24)
            .set_align("center", "center")
        )

        sidebar.set_content(root)
        sidebar.show()


class WasteYard(Room):
    """
    Salle où les déchets sont entreposés pour limiter la propagation des maladies.
    """

    def __init__(self, colony, data):
        super().__init__(
            colony,
            "waste_yard",
            {**data, "walkable": []},
        )

    def update_self(self, events):
        pass

    def interact(self):
        sidebar = self.colony.sidebar
        assert sidebar is not None

        panel_w = sidebar.width
        panel_h = sidebar.height
        inner_w = panel_w - PADDING * 2

        ui = self.colony.ui
        root = (
            ui.panel("waste_root", (0, 0, panel_w, panel_h))
            .set_border(None, 0)
            .set_bg_color(UIColors.BG_DARK)
        )

        root.add_child(
            ui.label(
                "waste_title", "Dépotoir", (PADDING, PADDING, inner_w, TITLE_HEIGHT)
            )
            .set_font_size(TITLE_FONT_SIZE)
            .set_align("center", "center")
        )

        sidebar.set_content(root)
        sidebar.show()
