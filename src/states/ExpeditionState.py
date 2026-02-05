from .State import State

class ExpeditionState(State):

    def __init__(self, state_manager):
        super().__init__(state_manager, "expedition", ["pause"])

        # TODO: implémenter le système d'expédition