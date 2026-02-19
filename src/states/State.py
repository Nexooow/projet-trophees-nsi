from lib.ui import UIManager
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.GameManager import GameManager
    from core.StateManager import StateManager
    from lib.ui import UIManager

class State:
    def __init__(self, state_manager: "StateManager", name: str, flags: list):
        self.stateManager: "StateManager" = state_manager
        self.game: "GameManager" = state_manager.game
        self.ui: "UIManager" = state_manager.game.ui
        self.name = name
        self.flags = flags

    def enable(self):
        pass

    def disable(self):
        pass

    def update(self, events):
        pass

    def draw(self):
        pass
