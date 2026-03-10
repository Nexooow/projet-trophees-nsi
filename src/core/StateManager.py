import typing

from states.ColonyState import ColonyState
from states.ExpeditionState import ExpeditionState
from states.MenuState import MenuState
from states.State import State
from states.BattleState import BattleState

class StateManager:
    """
    Gère les différents états du jeu.
    """

    def __init__(self, game):
        self.game = game

        self.states_managers: dict = {
            "menu": MenuState(self),
            "colony": ColonyState(self),
            "expedition": ExpeditionState(self),
            "battle": None,  # sera créé dynamiquement lors d'une bataille
        }
        self.last_state = None
        self.current_state: str = "menu"

        self.get_current_state().enable()

    def get_current_state(self) -> State:
        """
        Retourne l'état actuel du jeu.
        """
        return self.states_managers[self.current_state]

    def set_state(self, state: str):
        """
        Change l'état actuel du jeu.
        """
        old_state = self.get_current_state()
        if state in self.states_managers and state != old_state.name:
            old_state.disable()
            self.game.ui.clear()
            self.last_state = old_state.name
            self.current_state = state
            self.get_current_state().enable()
 
    def update(self, events):
        self.get_current_state().update(events)

    def draw(self):
        self.get_current_state().draw()

    def is_flag_active(self, flag: str) -> bool:
        return flag in self.get_current_state().flags
    def start_battle(self, difficulty, colony, auto):
        self.states_managers["battle"] = BattleState(self, difficulty, colony, auto)
        self.set_state("battle")