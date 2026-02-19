from colony.Room import Room


class Nursery(Room):
    def __init__(self, colony, data):
        super().__init__(
            colony,
            "nursery",
            {**data, "walkable": []},
        )

    def update(self):
        pass
