from colony.Room import Room

from lib.file import File

QUEEN_MAX_HP = 100
QUEEN_LOW_FOOD_THRESHOLD = 20


class Queen(Room):
    """
    Pièce spéciale représentant la chambre de la reine.
    """

    def __init__(self, colony, data: dict):
        super().__init__(
            colony,
            "queen",
            {**data, "walkable": []},
        )

        self.max_hp: int = QUEEN_MAX_HP
        self.hp: int = QUEEN_MAX_HP
        
        self.born_queue = File() # file avec les futures naissances
        
    def update_self (self, events):
        pass