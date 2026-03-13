from colony.Room import Room
from lib.ui import UIColors

PADDING = 6
GAP = 6
TITLE_HEIGHT = 36
TITLE_FONT_SIZE = 42

class Depot(Room):
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
            "depot",
            {**data, "walkable": [], "entry_offset": entry_offset},
        )

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
            ui.scrollable_panel(
                "depot_inventory",
                (PADDING, y_inv, panel_w-PADDING*2, panel_h-(TITLE_HEIGHT+y_title+PADDING*2))
            ) # TODO: ajouter les éléments de l'inventaire
        )

        sidebar.set_content(root)
        sidebar.show()