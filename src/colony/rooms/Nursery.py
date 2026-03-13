from colony.Room import Room


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

    def update_self(self, events):
        pass

    
