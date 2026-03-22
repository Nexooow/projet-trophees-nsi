import pygame
from exploration.battle_controller import BattleController
from exploration.battle_model import BattleModel
from exploration.battle_renderer import BattleRenderer, Sidebar

from .State import State


class BattleState(State):
    """
    Gère les trois parties du mini-jeu, et se charge du déroulement(passage des tours, fin du jeu, etc.)
    """

    def __init__(
        self,
        manager,
        difficulty=1,
        colony=None,
        auto_resolve=False,
        world_pos=None,
        perlin=None,
    ):
        super().__init__(manager, "battle", [])
        self.manager = manager
        self.model = BattleModel(difficulty, colony, auto_resolve, world_pos, perlin)
        self.controller = BattleController(self.model)
        screen=self.manager.game.screen
        self.renderer = BattleRenderer(self.model, screen, Sidebar(250, screen.get_height()))

    def update(self, events):
        #How can we make it so that the overlap problem is fixed, when they move onto an enemy their turn ends but the enemy doesn't die?

        if self.model.battle_won is not None:
            self.state_manager.set_state("expedition")
            return
        active=self.model.active_unit
        if active is None:
            return
        print(f"Active unit: {active} with {active.points} points")
        self.controller.take_turn(events)
        print(f"After processing turn: Active unit: {active} with {active.points} points")
        self.controller.resolve()
        print(f"After turn: Active unit: {active} with {active.points} points")
        if active not in self.model.units:
            self.model.next_turn()
            return
        self.check_battle_end()
        if active in self.model.units and active.points<=0:
            self.model.next_turn()
    def check_battle_end(self):
        if not self.model.friendlies:
            self.model.battle_won = False
            self.manager.game.battle_won = False

        elif not self.model.enemies:
            self.model.battle_won = True
            self.manager.game.battle_won = True
    def draw(self):
        self.renderer.draw()
