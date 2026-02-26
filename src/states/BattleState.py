from .State import State
from exploration.battle_model import BattleModel
from exploration.battle_controller import BattleController
from exploration.battle_renderer import BattleRenderer
import pygame
class BattleState(State):
    def __init__(self, manager, difficulty=1, colony=None, auto_resolve=False):
        super().__init__("battle")
        self.manager = manager
        self.model = BattleModel(difficulty, colony, auto_resolve)
        self.controller = BattleController(self.model)
        screen = pygame.display.set_mode((self.model.grid.width*50 + 250, self.model.grid.height*50))
        self.renderer = BattleRenderer(self.model, screen, manager.game.sidebar)
    def update(self, events):
        if self.model.active_unit.points > 0:
            self.controller.handle_input(events)
            self.controller.ai_move()
            self.controller.process_bombs_and_attacks()
        if self.model.active_unit.points<=0 or self.model.active_unit.static_state:
            self.model.next_turn()
        if len(self.model.friendlies) == 0:
            self.model.battle_won = False
            self.manager.game.battle_won = False
        elif len(self.model.enemies) == 0:
            self.model.battle_won = True
            self.manager.game.battle_won = True
    def draw(self):
        self.renderer.draw()