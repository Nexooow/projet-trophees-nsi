from colony.Room import Room


class Queen(Room):
    def __init__(self, colony, data):
        super().__init__(
            colony,
            "queen",
            {**data, "walkable": []},
        )

    def update(self):
        pass
