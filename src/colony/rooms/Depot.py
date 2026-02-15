from colony.Room import Room


class Depot(Room):
    def __init__(self, colony, data):
        super().__init__(
            colony,
            "depot",
            {**data, "walkable": []},
        )

    def update(self):
        pass
