from colony.Room import Room
from lib.ui import UIColors

PADDING = 6
GAP = 6
TITLE_HEIGHT = 36
TITLE_FONT_SIZE = 42


class Laboratory(Room):
    ENTRY_OFFSET_X_RATIO = 0.0
    ENTRY_OFFSET_Y_RATIO = 0.5

    def __init__(self, colony, data):
        width_px = data["width"] * 8
        height_px = data["height"] * 8
        entry_offset = (
            int(width_px * self.ENTRY_OFFSET_X_RATIO),
            int(height_px * self.ENTRY_OFFSET_Y_RATIO),
        )
        super().__init__(
            colony,
            "laboratory",
            {**data, "walkable": [], "entry_offset": entry_offset},
        )
        self.scientists_assigned = 0
        self.research_progress = 0.0
        self.current_research = None

    def update_self(self, events):
        if self.scientists_assigned > 0:
            # Génère de la science si des scientifiques sont présents
            self.colony.science += 0.01 * self.scientists_assigned

    def interact(self):
        sidebar = self.colony.sidebar
        assert sidebar is not None

        panel_w = sidebar.width
        panel_h = sidebar.height
        inner_w = panel_w - PADDING * 2

        ui = self.colony.ui
        root = (
            ui.panel("lab_root", (0, 0, panel_w, panel_h))
            .set_border(None, 0)
            .set_bg_color(UIColors.BG_DARK)
        )

        root.add_child(
            ui.label(
                "lab_title", "Laboratoire", (PADDING, PADDING, inner_w, TITLE_HEIGHT)
            )
            .set_font_size(TITLE_FONT_SIZE)
            .set_align("center", "center")
        )

        root.add_child(
            ui.label(
                "lab_science",
                f"Science : {int(self.colony.science)}",
                (PADDING, PADDING + TITLE_HEIGHT + GAP, inner_w, 30),
            )
            .set_font_size(28)
            .set_align("center", "center")
        )

        y_research = PADDING + TITLE_HEIGHT + GAP + 40
        root.add_child(
            ui.label(
                "lab_tree_title",
                "Arbre Technologique",
                (PADDING, y_research, inner_w, 30),
            )
            .set_font_size(24)
            .set_align("center", "center")
        )

        root.add_child( # exemple, à modifier
            ui.button(
                "research_mining",
                "Vitesse de minage (+10%)",
                (PADDING, y_research + 40, inner_w, 40),
            )
        )

        sidebar.set_content(root)
        sidebar.show()
