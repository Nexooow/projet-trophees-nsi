import pygame
from exploration.battle_controller import BattleController
from exploration.battle_model import BattleModel, Bomb
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
        super().__init__(manager, "battle", ["pause"])
        self.manager = manager
        self.model = BattleModel(difficulty, colony, auto_resolve, world_pos, perlin)
        self.controller = BattleController(self.model)
        screen = self.manager.game.screen
        self.renderer = BattleRenderer(
            self.model, screen, Sidebar(250, screen.get_height())
        )

    def update(self, events):
        if self.model.battle_won is not None:
            if self.model.battle_won:
                colony_state = self.state_manager.states_managers["colony"]
                colony_state.food += self.model.collected_resources * 100
            self.state_manager.set_state("expedition")
            return
        active = self.model.active_unit
        if active is None:
            return
        if 'match' in active.items.keys():
            if active.items["match"]>=1:
                for event in events:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        for bomb_pos in self.model.bomb_tiles:
                            
                            ox, oy = self.renderer.grid_offset_x, self.renderer.grid_offset_y
                            print(f"clicked_at:{event.pos}")
                            bomb_screen = (bomb_pos[0] * self.renderer.tile_size + ox, bomb_pos[1] * self.renderer.tile_size + oy)
                            print(f"bomb_pos:{bomb_screen}")
                            distance = ((event.pos[0] - bomb_screen[0]) ** 2 + (event.pos[1] - bomb_screen[1]) ** 2) ** 0.5
                            print(distance)
                            if distance <= self.renderer.tile_size :
                                print("distance is good")
                                bomb = Bomb(*bomb_pos)
                                dead_units = bomb.explode(self.model.units)

                                for u in dead_units:
                                    self.model.remove_unit(u)

                                self.model.bomb_tiles.remove(bomb_pos)
                                active.items["match"]-=1
                                break
        self.controller.take_turn(events)
        self.controller.resolve()
        if active not in self.model.units:
            self.model.next_turn()
            return
        self.check_battle_end()
        if active in self.model.units and active.points <= 0:
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
