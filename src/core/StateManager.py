import typing

from states.ColonyState import ColonyState
from states.MapState import MapState
from states.ExpeditionState import ExpeditionState
from states.MenuState import MenuState
from states.State import State


class StateManager:
    """
    Gère les différents états du jeu.
    """

    def __init__(self, game):
        self.game = game

        self.states_managers: dict[str, State] = {
            "menu": MenuState(self),
            "colony": ColonyState(self),
            "map": MapState(self),
            "expedition": ExpeditionState(self)
            
        }
        self.current_state: str = "colony"

        self.get_current_state().enable()

    def is_current_state(self, state) -> bool:
        return state == self.current_state

    def get_current_state(self) -> State:
        return self.states_managers[self.current_state]

    def set_state(self, state: str):
        """
        Change l'état actuel du jeu.
        """
        old_state = self.get_current_state()
        if state in self.states_managers and state != old_state.name:
            old_state.disable()
            self.game.ui.clear()
            self.current_state = state
            self.get_current_state().enable()

    def update(self, events):
        self.get_current_state().update(events)

    def draw(self):
        self.get_current_state().draw()

    def is_flag_active(self, flag: str) -> bool:
        return flag in self.get_current_state().flags
