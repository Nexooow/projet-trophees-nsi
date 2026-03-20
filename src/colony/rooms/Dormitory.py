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

    ENTRY_OFFSET_X_RATIO = 0.5
    ENTRY_OFFSET_Y_RATIO = 1.0

    def __init__(self, colony, data):
        width_px = data["width"] * 8
        height_px = data["height"] * 8
        entry_offset = (
            int(width_px * self.ENTRY_OFFSET_X_RATIO),
            int(height_px * self.ENTRY_OFFSET_Y_RATIO),
        )
        super().__init__(
            colony,
            "dormitory",
            {**data, "walkable": [], "entry_offset": entry_offset},
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

    ENTRY_OFFSET_X_RATIO = 0.5
    ENTRY_OFFSET_Y_RATIO = 1.0

    def __init__(self, colony, data):
        width_px = data["width"] * 8
        height_px = data["height"] * 8
        entry_offset = (
            int(width_px * self.ENTRY_OFFSET_X_RATIO),
            int(height_px * self.ENTRY_OFFSET_Y_RATIO),
        )
        super().__init__(
            colony,
            "waste_yard",
            {**data, "walkable": [], "entry_offset": entry_offset},
        )

    def update_self(self, events):
        pass # TODO: voir ce que cela fait

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

        root.add_child(
            ui.label(
                "waste_status",
                f"Hygiène globale : {max(0, 100 - int(self.colony.disease))}%",
                (PADDING, PADDING + TITLE_HEIGHT + GAP, inner_w, 40),
            )
            .set_font_size(28)
            .set_align("center", "center")
        )

        sidebar.set_content(root)
        sidebar.show()
