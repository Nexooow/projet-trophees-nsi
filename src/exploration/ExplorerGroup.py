from colony.Ant import Ant
class ExplorerGroup(Ant):
    def __init__(self, name, position, world):
        super().__init__(name, position, world)
        self.explorers=[]
        self.exploration_radius = len(self.explorers)
        self.stock = {}
    def add_explorer(self, explorer):
        self.explorers.append(explorer)
        self.exploration_radius = len(self.explorers) # Suffit pas d'avoir débloqué le précédent, pour explorer faut avoir autant d'explorateurs que la hauteur du graphe
    def add_to_stock(self, resource):
        if resource in self.stock:
            self.stock[resource] += 1
        else:
            self.stock[resource] = 1
    def get_ants(self, ant_type=None):
        if ant_type is None:
            return self.explorers
        return [explorer for explorer in self.explorers if explorer.id == ant_type]