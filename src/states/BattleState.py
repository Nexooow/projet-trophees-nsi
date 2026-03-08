from .State import State
from exploration.battle_model import BattleModel
from exploration.battle_controller import BattleController
from exploration.battle_renderer import BattleRenderer
import pygame
from exploration.Griddy import Sidebar
class BattleState(State):
    def __init__(self, manager, difficulty=1, colony=None, auto_resolve=False):
        super().__init__(manager,"battle",[])
        self.manager = manager
        self.model = BattleModel(difficulty, colony, auto_resolve)
        self.controller = BattleController(self.model)
        screen = pygame.display.set_mode((self.model.grid.width*50 + 250, self.model.grid.height*50))
        self.renderer = BattleRenderer(self.model, screen, Sidebar(250,700))
    def update(self, events):
        if self.model.battle_won is not None:
            self.stateManager.set_state("expedition")
        if self.model.active_unit not in self.model.units:
            self.model.turn_index %= len(self.model.units)
            self.model.active_unit = self.model.units[self.model.turn_index]
        if self.model.active_unit.points<=0 and self.model.active_unit.static_state:
            self.model.next_turn()
        if self.model.active_unit.points > 0:
            self.controller.handle_input(events)
            self.controller.ai_move()
            self.controller.process_bombs_and_attacks()
        if len(self.model.friendlies) == 0:
            self.model.battle_won = False
            self.manager.game.battle_won = False
            print("Not cleared")
        if len(self.model.enemies) == 0:
            self.model.battle_won = True
            self.manager.game.battle_won = True
            print("Cleared")
        
        
    def draw(self):
        self.renderer.draw()