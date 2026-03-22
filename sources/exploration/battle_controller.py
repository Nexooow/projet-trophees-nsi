import pygame
from lib.pathfinding import closest_enemy, reachable_tiles_nx, shortest_path, neighbors

from .battle_model import Bomb


class BattleController:
    """
    Se charge, pour la Battle Grid: des inputs, des déplacements, et des morts des unités
    """

    def __init__(self, model):
        self.model = model
    
    def try_move(self, active, key, tiles):
        dx, dy = 0, 0
        if key == pygame.K_LEFT:
            active.orientation = True
            dx = -1

        elif key == pygame.K_RIGHT:
            active.orientation = False
            dx = 1
        elif key == pygame.K_UP:
            dy = -1
        elif key == pygame.K_DOWN:
            dy = 1
        grid=self.model.grid
        friendlies=[u for u in self.model.units if u.team==active.team]
        target = (active.x + dx, active.y + dy)
        if (
            0 <= target[0] < grid.width
            and 0 <= target[1] < grid.height
            and target in tiles
            and all((target != (f.x, f.y) for f in friendlies))
            and active.points>=grid.weights[target]
        ):
            active.points -= grid.weights[target]
            active.move_to(*target)
            return True
        else:
            return False
    def process_bombs_and_attacks(self):
        active = self.model.active_unit
        if (active.x, active.y) in self.model.bomb_tiles:
            bomb = Bomb(active.x, active.y)
            dead_units = bomb.explode(self.model.units)
            active_died = active in dead_units
            for u in dead_units:
                self.model.remove_unit(u)
            self.model.bomb_tiles.remove((active.x, active.y))
            if active_died:
                return

        enemies = [u for u in self.model.units if u.team != active.team]
        for enemy in enemies:
            if (enemy.x, enemy.y) == (active.x, active.y):
                self.model.remove_unit(enemy)
    def take_turn(self,events):
        active = self.model.active_unit

        if active.team == "noir" and not self.model.auto_resolve:
            return self.handle_player_turn(events)
        else:
            return self.handle_ai_turn()
    def handle_player_turn(self, events):
        active = self.model.active_unit
        grid = self.model.grid
        units = self.model.units
        
        tiles = reachable_tiles_nx(active, grid, units)
        enemies_present=any((u.team != active.team and (((u.x, u.y) == (active.x, active.y)) or (u.x, u.y) in neighbors(active.x,active.y,grid.width,grid.height))) for u in units)
        print(len(tiles))
        if len(tiles)<=1 and not enemies_present:
            active.points=0
            print("ça marche? v2")
            return True
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    active.points = 0
                    return True
                tiles = reachable_tiles_nx(active, grid, units)
                print(len(tiles))
                if len(tiles)<=1 and not enemies_present:
                    active.points=0
                    print("ça marche?")
                    return True
                moved = self.try_move(active, event.key, tiles)
                if moved:
                    return True
        
        return False
    def handle_ai_turn(self):
        active = self.model.active_unit

        if not active.static_state:
            return False

        enemies = [u for u in self.model.units if u.team != active.team]
        if not enemies:
            return False

        blocked = [u.tile() for u in self.model.units if u is not active and u.team==active.team]

        target = closest_enemy(active, enemies, self.model.grid, self.model.units)
        if not target:
            return False

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
            return True

        active.points = 0
        return True
    def resolve(self):
        self.resolve_bombs()
        self.resolve_combat()
    def resolve_bombs(self):
        
        active = self.model.active_unit
        pos = (active.x, active.y)

        if pos in self.model.bomb_tiles:
            bomb = Bomb(*pos)
            dead_units = bomb.explode(self.model.units)

            for u in dead_units:
                self.model.remove_unit(u)

            self.model.bomb_tiles.remove(pos)
    def resolve_combat(self):
        active = self.model.active_unit

        for enemy in self.model.units:
            if enemy.team != active.team:
                if (enemy.x, enemy.y) == (active.x, active.y):
                    self.fight(active, enemy)
    def fight(self, a, b):
        self.model.remove_unit(b)
    