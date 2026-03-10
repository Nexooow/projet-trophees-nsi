import pygame

from .battle_model import Bomb
from .Utilities import closest_enemy, reachable_tiles_nx, shortest_path


class BattleController:
    def __init__(self, model):
        self.model = model

    def handle_input(self, events):
        active = self.model.active_unit
        friendlies = self.model.friendlies
        units = self.model.units
        grid = self.model.grid
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                
            if active.team == "noir" and not self.model.auto_resolve:
                if event.type == pygame.KEYDOWN:
                    tiles = reachable_tiles_nx(active, grid, units)
                    if event.key == pygame.K_SPACE:
                        active.points = 0
                    elif event.key in [
                        pygame.K_LEFT,
                        pygame.K_RIGHT,
                        pygame.K_UP,
                        pygame.K_DOWN,
                    ]:
                        self.move_player(active, event.key, tiles, friendlies, grid)

    def move_player(self, active, key, tiles, friendlies, grid):
        dx, dy = 0, 0
        if key == pygame.K_LEFT:
            active.orientation=True
            dx = -1
            
        elif key == pygame.K_RIGHT:
            active.orientation=False
            dx = 1
        elif key == pygame.K_UP:
            dy = -1
        elif key == pygame.K_DOWN:
            dy = 1

        target = (active.x + dx, active.y + dy)
        if 0 <= target[0] < grid.width and 0 <= target[1] < grid.height and target in tiles and all((target != (f.x, f.y) for f in friendlies)):
            active.points -= grid.weights[target]
            active.move_to(*target)

    def ai_move(self):
        active = self.model.active_unit
        if not active.static_state:
            return
        if active.team != "noir" or self.model.auto_resolve:
            enemies = [u for u in self.model.units if u.team != active.team]
            if enemies:
                blocked = [
                    u.tile()
                    for u in self.model.units
                    if (u is not active) and (u not in enemies)
                ]
                target = closest_enemy(
                    active, enemies, self.model.grid, self.model.units
                )
                if target:
                    path = shortest_path(
                        active.tile(),
                        target.tile(),
                        self.model.grid.graph,
                        self.model.grid.width,
                        blocked,
                        diagonals=active.diagonal,
                        diagonal_edges=self.model.grid.diagonal_edges,
                    )
                    if path and active.points >= self.model.grid.weights[path[0]]:
                        active.points -= self.model.grid.weights[path[0]]
                        active.move_to(*path[0])
                    else:
                        active.points=0
    def process_bombs_and_attacks(self):
        active=self.model.active_unit
        enemies=[u for u in self.model.units if u.team!=active.team]
        if (active.x,active.y) in self.model.bomb_tiles:
            bomb=Bomb(active.x,active.y)
            dead_units=bomb.explode(self.model.units)
            active_died=active in dead_units
            for u in dead_units:
                self.model.remove_unit(u)
            self.model.bomb_tiles.remove((active.x, active.y))
            if active_died:
                return
        for enemy in enemies:
            if (enemy.x, enemy.y) == (active.x, active.y):
                self.model.remove_unit(enemy)
