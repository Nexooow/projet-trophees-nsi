from core.UIManager import UIManager

class State:

    def __init__ (self, state_manager, name: str, flags: list):
        self.stateManager = state_manager
        self.game = state_manager.game
        self.ui: UIManager = state_manager.game.ui
        self.name = name
        self.flags = flags

    def enable (self):
        pass

    def disable (self):
        pass

    def update (self, events):
        pass

    def draw (self):
        pass