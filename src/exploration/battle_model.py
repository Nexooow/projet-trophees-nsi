import pygame
from itertools import product
from random import choice,sample,randint,random
from .Unit import Unit
from .Utilities import neighbors
from lib.perlin import Perlin
TILE_SIZE=50
SIDEBAR_WIDTH=50
class HoveringResource:
    def __init__(self, x, y, resource, tile_size=TILE_SIZE):
        self.x = x
        self.y = y
        self.resource = resource
        self.tile_size = tile_size
        self.start_time = pygame.time.get_ticks()
        self.hover_height = 10
        self.hover_speed = 0.005

    def draw_offset(self):
        elapsed_time = (pygame.time.get_ticks() - self.start_time) * self.hover_speed
        return self.hover_height * pygame.math.sin(elapsed_time)
class Bomb:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def explode(self, units):
        dead = []
        for u in units:
            if abs(u.x - self.x) <= 1 and abs(u.y - self.y) <= 1:
                dead.append(u)
        return dead
class Grid:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.tile = TILE_SIZE
        self.weights = {}
        self.edges = []
        self.diagonal_edges = []

        perlin = Perlin(seed=42, scale=20, octaves=4, steps=4, normalize=True)
        noise_map = perlin.noise_map(width, height)
        for y in range(height):
            for x in range(width):
                w = int(noise_map[y][x] * 3) + 1
                self.weights[(x, y)] = w

        for y in range(height):
            for x in range(width):
                for nx, ny in neighbors(x, y, width, height):
                    self.edges.append(((x, y), (nx, ny), {"weight": self.weights[(nx, ny)]}))
        for y in range(height):
            for x in range(width):
                for dx, dy in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < width and 0 <= ny < height:
                        self.diagonal_edges.append(((x, y), (nx, ny), {"weight": self.weights[(nx, ny)] * 1.414}))

class BattleModel:
    def __init__(self, difficulty, colony, auto_resolve=False):
        self.difficulty = difficulty
        self.auto_resolve = auto_resolve
        self.battle_won = None

        self.grid_w = 20 + difficulty * 2
        self.grid_h = 14 + difficulty
        self.grid = Grid(self.grid_w, self.grid_h)

        self.units = []
        self.friendlies = []
        self.enemies = []

        self.bomb_tiles = set()
        self.resources_obj = []
        self.resources_dispos = {}

        self.turn_index = 0
        self.active_unit = None

        self.init_battle(colony)
    def init_battle(self,colony):
        positions_of_ressources = sample(
            list(product(range(self.grid_w), range(int(self.grid_h*4/14)))), randint(1,5)
        )
        self.resources_dispos = {(x, y): choice(["nom"]) for x, y in positions_of_ressources}
        self.resources_obj = [HoveringResource(x, y, res) for (x, y), res in self.resources_dispos.items()]
        
        bomb_rate = min(0.25, 0.02 * (1.4 ** self.difficulty))
        for x in range(self.grid_w):
            for y in range(self.grid_h):
                if random() < bomb_rate:
                    self.bomb_tiles.add((x, y))

        fourmis_nwar = colony.get_ants(ant_type="soldier") if not isinstance(colony, list) else []
        fourmis_nwar += [Unit(0,0,None,None) for _ in range(2)]  # test puppets
        ally_pos = list(product(range(self.grid_w), range(int(self.grid_h*10/14), self.grid_h)))
        pos2 = sample(ally_pos, min(len(fourmis_nwar), len(ally_pos)))
        self.friendlies = [Unit(x, y, ant.image, "noir", ant.power) for ant, (x, y) in zip(fourmis_nwar, pos2)]
        nb_enemies = 2 + self.difficulty * 2
        positions = list(product(range(self.grid_w), range(int(self.grid_h*4/14))))
        pos1 = sample(positions, min(nb_enemies, len(positions)))
        from .Unit import Unit
        self.enemies = [
            Unit(x, y, None, "rouge", power=self.difficulty) for x, y in pos1
        ]
        self.units = self.enemies + self.friendlies
        self.active_unit = self.units[self.turn_index]

        protected_tiles = set(pos1 + pos2 + list(self.resources_dispos.keys()))
        self.bomb_tiles = {tile for tile in self.bomb_tiles if tile not in protected_tiles}
    def next_turn(self):
        self.active_unit.reset_turn()
        self.turn_index = (self.turn_index + 1) % len(self.units)
        self.active_unit = self.units[self.turn_index]
    def remove_unit(self, unit):
        if unit in self.units:
            self.units.remove(unit)
        if unit in self.friendlies:
            self.friendlies.remove(unit)
        if unit in self.enemies:
            self.enemies.remove(unit)
