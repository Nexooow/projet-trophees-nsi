from colony.Ant import Ant

class Worker (Ant):
    
    def __init__ (self, colony, data: dict):
        super().__init__(colony, "worker", data)