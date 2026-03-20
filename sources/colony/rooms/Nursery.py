from colony.ants.Nurse import Nurse
from colony.ants.Worker import Worker
from colony.Room import Room
from constants import UIColors

PADDING = 6
GAP = 6
TITLE_HEIGHT = 36
TITLE_FONT_SIZE = 42

TIMES = {"": 0}  # TODO: ajouter les temps selon les types de larves


class Nursery(Room):
    ENTRY_OFFSET_X_RATIO = 0.5
    ENTRY_OFFSET_Y_RATIO = 0.0

    def __init__(self, colony, data):
        width_px = data["width"] * 8
        height_px = data["height"] * 8
        entry_offset = (
            int(width_px * self.ENTRY_OFFSET_X_RATIO),
            int(height_px * self.ENTRY_OFFSET_Y_RATIO),
        )
        super().__init__(
            colony,
            "nursery",
            {**data, "walkable": [], "entry_offset": entry_offset},
        )

        self.larvaes = []

    def update_self(self, events):
        for type, start in self.larvaes:
            time_since_start = self.game.time.now() - start
            if time_since_start >= TIMES[type]:
                ANT_CLASS_MAP = {"nurse": Nurse, "worker": Worker}
                pass  # TODO: faire apparaitre la nouvelle fourmi

    def assign_larvae(self, larvae_type):
        self.larvaes.append((larvae_type, self.colony.game.time.now()))
        pass  # TODO

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
                "nursery_root",
                (0, 0, panel_w, panel_h),
            )
            .set_border(None, 0)
            .set_bg_color(UIColors.BG_DARK)
        )

        root.add_child(
            ui.label(
                "nursery_title",
                "Nurserie",
                (PADDING, y_title, inner_w, TITLE_HEIGHT),
            )
            .set_font_size(TITLE_FONT_SIZE)
            .set_align("center", "center")
        )

        sidebar.set_content(root)
        sidebar.show()
