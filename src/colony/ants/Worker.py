from colony.Ant import Ant


class Worker(Ant):
    def __init__(self, colony, data: dict, pos):
        super().__init__(colony, "worker", data, pos)
