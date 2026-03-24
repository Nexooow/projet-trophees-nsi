import math
import typing
from itertools import product
from random import choice, choices, randint, random, sample, shuffle

import networkx as netx
import pygame
from lib.pathfinding import neighbors
from lib.perlin import Perlin
from lib.utils import fill, import_asset

from .Unit import Unit

TILE_SIZE = 50
SIDEBAR_WIDTH = 50

img_fourmi = import_asset("ant.png")

img_scarab = import_asset("scarab.png")


class HoveringResource:
    def __init__(self, x, y, resource, tile_size=TILE_SIZE):
        self.x = x
        self.y = y
        self.resource = resource
        self.tile_size = tile_size
        self.start_time = pygame.time.get_ticks()
        self.hover_height = 5
        self.hover_speed = 0.005

    def draw_offset(self):
        elapsed_time = (pygame.time.get_ticks() - self.start_time) * self.hover_speed
        return self.hover_height * math.sin(elapsed_time)


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
    """
    Représente la grille de jeu, avec les poids de chaque case et les objets présents dessus.
    """

    def __init__(self, width, height, center_x, center_y, perlin):
        self.width = width
        self.height = height
        self.tile = TILE_SIZE
        self.weights = {}
        self.edges = []
        self.diagonal_edges = []
        self.perlin = perlin
        self.objects = {}
        self.biome = self.detect_biome(center_x, center_y)

        # perlin = Perlin( scale=20, octaves=4, steps=4, normalize=True)

        self.dominance = min(max(self.biome.values()), 0.7)
        self.dominant_weight = max(self.biome, key=lambda k: self.biome[k])

        scale = 10 + (1 - self.dominance) * 25
        persistence = 0.3 + (1 - self.dominance) * 0.5
        self.local_perlin = Perlin(
            scale=scale, octaves=2, persistence=persistence, steps=4, normalize=True
        )

        offset_x = center_x - width // 2
        offset_y = center_y - height // 2
        for y in range(height):
            for x in range(width):
                world_x = offset_x + x
                world_y = offset_y + y
                w = self.get_weight(world_x, world_y)
                self.weights[(x, y)] = w
        self.generate_objects(center_x, center_y)

        for y in range(height):
            for x in range(width):
                for nx, ny in neighbors(x, y, width, height):
                    self.edges.append(
                        ((x, y), (nx, ny), {"weight": self.weights[(nx, ny)]})
                    )
        for y in range(height):
            for x in range(width):
                for dx, dy in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < width and 0 <= ny < height:
                        self.diagonal_edges.append(
                            (
                                (x, y),
                                (nx, ny),
                                {"weight": self.weights[(nx, ny)] * 1.414},
                            )
                        )
        self.graph = netx.DiGraph(self.edges)

    def get_mask(self, x, y):
        # Bitmask à partir des voisins (1 pour le haut, 2 pour la droite, 4 pour le bas et 8 pour la gauche)
        w = self.weights[(x, y)]
        mask = 0
        if y > 0 and self.weights[(x, y - 1)] == w:
            mask |= 1
        if x < self.width - 1 and self.weights[(x + 1, y)] == w:
            mask |= 2
        if y < self.height - 1 and self.weights[(x, y + 1)] == w:
            mask |= 4
        if x > 0 and self.weights[(x - 1, y)] == w:
            mask |= 8
        return mask

    def detect_biome(self, center_x, center_y, radius=20):
        counts = {1: 0, 2: 0, 3: 0, 4: 0}
        for dy in range(-radius, radius):
            for dx in range(-radius, radius):
                n = self.perlin.noise(center_x + dx, center_y + dy)
                w = int(n * 3) + 1
                counts[w] += 1
        total = sum(counts.values())
        return {k: v / total for k, v in counts.items()}

    def generate_objects(self, center_x, center_y):
        for y in range(self.height):
            for x in range(self.width):
                world_x = center_x + x
                world_y = center_y + y
                w = self.weights[(x, y)]
                n = self.perlin.noise(world_x + 1000, world_y + 1000)
                if n > 0.65:
                    if self.perlin.noise(world_x + 2000, world_y + 2000):
                        self.objects[(x, y)] = "grass"
                else:
                    if self.biome[2] > 0.3:
                        if w >= 2 and n < 0.6:
                            self.objects[(x, y)] = "grass"
                    elif self.biome[3] > 0.3:
                        if w >= 3 and n > 0.5:
                            self.objects[(x, y)] = "rock"

                    elif self.biome[1] > 0.3:
                        if n > 0.75:
                            self.objects[(x, y)] = "rock"

                    elif self.biome[4] > 0.3:
                        if n > 0.7:
                            self.objects[(x, y)] = "grass"

    def get_weight(self, world_x, world_y):
        global_n = self.perlin.noise(world_x, world_y)
        local_n = self.local_perlin.noise(world_x, world_y)
        n = (global_n * 0.6) + (local_n * (0.4))
        bias = (
            (self.biome[2] - 0.25) * 0.25
            + (self.biome[3] - 0.25) * 0.35
            + (self.biome[1] - 0.25) * -0.2
            + (self.biome[4] - 0.25) * 0.15
        )
        n = min(max(n + bias, 0), 1)
        n += (random() - 0.5) * 0.05
        return int(n * 3) + 1


CELL_SIZE = 5


class BattleModel:
    """
    Gère les données d'une bataille, y compris la grille, les unités, les ressources et l'état de la bataille.
    """

    def __init__(self, difficulty, colony, auto_resolve, world_pos, perlin):
        self.difficulty = difficulty
        self.auto_resolve = auto_resolve or False
        self.battle_won: typing.Optional[bool] = None
        self.perlin = perlin
        cell_x = int(world_pos[0] // CELL_SIZE)
        cell_y = int(world_pos[1] // CELL_SIZE)
        """
        self.grid_w = 20 + difficulty * 2
        self.grid_h = 14 + difficulty
        """
        self.grid_w = 20
        self.grid_h = 14
        self.grid = Grid(self.grid_w, self.grid_h, cell_x, cell_y, perlin)

        self.units = []
        self.friendlies = []
        self.enemies = []

        self.bomb_tiles = set()
        self.resources_obj = []
        self.resources_dispos = {}
        self.collected_resources = 0

        self.turn_index = 0
        self.active_unit: typing.Optional[Unit] = None

        self.init_battle(colony)

    def init_battle(self, colony):
        img_fourmi_noir=import_asset("ant.png")
        positions_of_ressources = sample(
            list(product(range(self.grid_w), range(int(self.grid_h)))),
            randint(1, 5),
        )
        self.resources_dispos = {
            (x, y): choice(["nom"]) for x, y in positions_of_ressources
        }
        self.resources_obj = [
            HoveringResource(x, y, res) for (x, y), res in self.resources_dispos.items()
        ]

        bomb_rate = min(0.25, 0.02 * (1.4**self.difficulty))
        for x in range(self.grid_w):
            for y in range(self.grid_h):
                if random() < bomb_rate:
                    self.bomb_tiles.add((x, y))

        fourmis_nwar = (
            colony.get_ants(ant_type="soldier") if not isinstance(colony, list) else []
        )
        fourmis_nwar += [Unit(0, 0, img_fourmi, None) for _ in range(2)]  # test puppets
        ally_pos = list(
            product(range(self.grid_w), range(int(self.grid_h * 10 / 14), self.grid_h))
        )
        pos2 = sample(ally_pos, min(len(fourmis_nwar), len(ally_pos)))
        self.friendlies = [
            Unit(x, y, img_fourmi_noir, "noir") for ant, (x, y) in zip(fourmis_nwar, pos2)
        ]
        nb_enemies = 2 + self.difficulty * 2
        positions = list(product(range(self.grid_w), range(int(self.grid_h * 4 / 14))))
        pos1 = sample(positions, min(nb_enemies, len(positions)))
        img_fourmi_rouge = fill(img_fourmi, pygame.Color(255, 0, 0))
        self.enemies = [
            choices(
                [
                    Unit(x, y, img_fourmi, "rouge"),
                    Unit(x, y, img_scarab, "rouge", points=3, diagonal=True),
                ],
                weights=(4, 1),
                k=1,
            )[0]
            for x, y in pos1
        ]
        self.units = self.enemies + self.friendlies
        shuffle(self.units)
        self.active_unit = self.units[self.turn_index]

        protected_tiles = set(pos1 + pos2 + list(self.resources_dispos.keys()))
        self.bomb_tiles = {
            tile for tile in self.bomb_tiles if tile not in protected_tiles
        }

    def next_turn(self):
        if not self.units:
            self.active_unit = None
            return
        if self.active_unit in self.units:
            self.active_unit.reset_turn()
        self.turn_index %= len(self.units)
        self.active_unit = self.units[self.turn_index]

        self.turn_index = (self.turn_index + 1) % len(self.units)

    def remove_unit(self, unit):
        if unit not in self.units:
            return
        index = self.units.index(unit)
        self.units.remove(unit)
        if index < self.turn_index:
            self.turn_index -= 1

        if unit in self.friendlies:
            self.friendlies.remove(unit)
        if unit in self.enemies:
            self.enemies.remove(unit)

    def collect_resource(self, x, y):
        if (x, y) in self.resources_dispos:
            del self.resources_dispos[(x, y)]
            self.resources_obj = [r for r in self.resources_obj if (r.x, r.y) != (x, y)]
            self.collected_resources += 100
