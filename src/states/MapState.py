from .State import State

class MapState(State):

    def __init__(self, state_manager):
        super().__init__(state_manager, "map", ["pause"])

        # TODO: implémenter le système de carte