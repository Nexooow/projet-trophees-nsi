import typing

from states.BattleState import BattleState
from states.ColonyState import ColonyState
from states.ExpeditionState import ExpeditionState
from states.GameOverState import GameOverState
from states.MenuState import MenuState
from states.State import State
from states.ExpeditionMenuState import ExpeditionMenuState

class StateManager:
    """
    Gère les différents états du jeu.
    """

    def __init__(self, game):
        self.game = game
        # Flags dynamiques gérées au niveau du StateManager (ex: 'pause')
        # Ces flags peuvent être définis/retirés via `set_flag` et sont prises
        # en compte par `is_flag_active`.
        self.active_flags = set()

        self.states_managers: dict = {
            "menu": MenuState(self),
            "colony": ColonyState(self),
            "expedition": ExpeditionState(self),
            "expedition_menu": ExpeditionMenuState(self),
            "battle": None,  # sera créé dynamiquement lors d'une bataille
            "game_over": GameOverState(self),
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
        """
        Retourne True si le flag est actif soit au niveau de l'état courant
        (déclaré dans state.flags), soit via un flag dynamique défini sur le
        StateManager (self.active_flags).
        """
        # Flags définis dynamiquement (ex: 'pause' via UI)
        if flag in getattr(self, "active_flags", set()):
            return True

        # Flags statiques définis par l'état courant
        current = self.get_current_state()
        return flag in getattr(current, "flags", [])

    def set_flag(self, flag: str, value: bool):
        """
        Définit ou retire un flag dynamique global au StateManager, ex: 'pause'.
        value=True -> active, value=False -> désactive.
        """
        if not hasattr(self, "active_flags"):
            self.active_flags = set()
        if value:
            self.active_flags.add(flag)
        else:
            self.active_flags.discard(flag)

    def start_battle(self, difficulty, colony, auto, world_pos, perlin):
        self.states_managers["battle"] = BattleState(
            self, difficulty, colony, auto, world_pos, perlin
        )
        self.set_state("battle")

    def trigger_game_over(self, stats: dict):
        self.states_managers["game_over"].set_stats(stats)
        self.set_state("game_over")

    def get_state(self, name: str):
        return self.states_managers.get(name)