import heapq
import math
from itertools import product
from random import choice, choices, randint, random, sample, shuffle

import networkx as netx
import pygame

from lib.perlin import Perlin
from lib.utils import import_asset

from .AntPuppet import AntPuppet
from .ExplorerGroup import *
from .Unit import *
from .Utilities import *

RESSOURCES_IMAGES = {"nom": import_asset("ant.png")}
RESSOURCES = ["nom"]
pygame.init()


class HoveringResource:
    def __init__(self, x, y, resource, tile_size=50):
        self.x = x
        self.y = y
        self.resource = resource
        self.tile_size = tile_size
        self.start_time = pygame.time.get_ticks()
        self.hover_height = 10
        self.hover_speed = 0.005

    def draw(self, screen):
        elapsed_time = (pygame.time.get_ticks() - self.start_time) * self.hover_speed
        offset = self.hover_height * math.sin(elapsed_time)
        screen_x = self.x * self.tile_size
        screen_y = self.y * self.tile_size + offset
        screen.blit(RESSOURCES_IMAGES[self.resource], (screen_x, screen_y))


class Bomb:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def get_pos(self):
        return (self.x, self.y)

    def explode(self, units):
        dead = []
        for u in units:
            if abs(u.x - self.x) <= 1 and abs(u.y - self.y) <= 1:
                dead.append(u)
        return dead

    # TODO:implementer systeme de destruction sur plusieurs tiles, soit par tile prédéterminée, soit par troupe (typa kamikaze)


# GRID_W=20
# GRID_H=14
TILE_SIZE = 50
SIDEBAR_WIDTH = 250
GRID_WIDTH = 1000
HEIGHT = 700


class Grid:
    def __init__(self, width, height, tile_size=50):
        self.width = width
        self.height = height
        self.tile = tile_size
        edges = []
        perlin = Perlin(seed=42, scale=20, octaves=4, steps=4, normalize=True)
        noise_map = perlin.noise_map(self.width, self.height)
        # self.weights={(x,y):choice([1,2,3,4 ]) for x in range(self.width) for y in range(self.height)}
        self.weights = {}
        for y in range(self.height):
            for x in range(self.width):
                value = noise_map[y][x]
                weight = int(value * 3) + 1
                self.weights[(x, y)] = weight
        for y in range(height):
            for x in range(width):
                i = x, y
                for nx, ny in neighbors(x, y, width, height):
                    edges.append((i, (nx, ny), {"weight": self.weights[(nx, ny)]}))
        self.graph = netx.DiGraph(edges)
        self.diagonal_edges = []
        for y in range(height):
            for x in range(width):
                i = x, y
                for dx, dy in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < width and 0 <= ny < height:
                        j = nx, ny
                        cost = self.weights[(nx, ny)] * 1.414
                        self.diagonal_edges.append((i, j, {"weight": cost}))

    def draw(self, screen, bomb_tiles=None):
        for x in range(self.width):
            for y in range(self.height):
                r = pygame.Rect(x * self.tile, y * self.tile, self.tile, self.tile)
                if bomb_tiles and (x, y) in bomb_tiles:
                    pygame.draw.rect(screen, (200, 50, 50), r)
                else:
                    w = self.weights[(x, y)]
                    col = weight_to_color(w)
                    pygame.draw.rect(screen, col, r)
                pygame.draw.rect(screen, (255, 255, 255), r, 1)

    def draw_reachable_tiles(self, unit, screen, units, color=(255, 255, 0)):
        tiles = reachable_tiles_nx(unit, self, units)
        for x, y in tiles.keys():
            tile = pygame.Rect(x * self.tile, y * self.tile, self.tile, self.tile)
            pygame.draw.rect(screen, color, tile, 2)


class Sidebar:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def draw(self, screen, units, active, colony):
        screen.fill((30, 30, 30))
        font = pygame.font.SysFont(None, 28)
        friendlies = len([u for u in units if u.team == "noir"])
        enemies = len([u for u in units if u.team == "rouge"])
        lines = [
            f"Active Team: {active.team}",
            f"Action Points: {active.points}",
            "",
            f"Friendlies: {friendlies}",
            f"Enemies: {enemies}",
            "",
            "Resources:",
            # TODO: Montrer les ressources que l'expédition a récup / celles qu'il y a au total
        ]
        y = 20
        for line in lines:
            text = font.render(line, True, (255, 255, 255))
            screen.blit(text, (20, y))
            y += 35


class Game:
    def __init__(self):
        self.battle_won = None
        self.sidebar = Sidebar(SIDEBAR_WIDTH, HEIGHT)

    def game(self, difficulty, colony, auto_resolve=False):
        base_w = 20
        base_h = 14
        GRID_W = base_w + difficulty * 2
        GRID_H = base_h + difficulty
        GRID_WIDTH = GRID_W * TILE_SIZE
        HEIGHT = GRID_H * TILE_SIZE
        positions_of_ressources = sample(
            list(product(range(GRID_W), range(int(GRID_H * 4 / 14)))), randint(1, 5)
        )

        ressources_dispos = {
            (x, y): choice(RESSOURCES) for x, y in positions_of_ressources
        }
        ressources_obj = [
            HoveringResource(x, y, resource)
            for (x, y), resource in ressources_dispos.items()
        ]
        bomb_rate = min(0.25, 0.02 * (1.4**difficulty))
        bomb_tiles = set()
        for x in range(GRID_W):
            for y in range(GRID_H):
                if random() < bomb_rate:
                    bomb_tiles.add((x, y))
        screen = pygame.display.set_mode((SIDEBAR_WIDTH + GRID_WIDTH, HEIGHT))
        game_surface = pygame.Surface((GRID_WIDTH, HEIGHT))
        ui_surface = pygame.Surface((SIDEBAR_WIDTH, HEIGHT))
        clock = pygame.time.Clock()
        img_fourmi = pygame.image.load("./assets/fonts/ant.png")
        img_scarab = pygame.image.load("./assets/fonts/ant.png")
        fourmis_nwar = (
            colony.get_ants(ant_type="soldier") if type(colony) is not list else []
        )  # Récup les fourmis de l'expedition (colony c pas une classe colony mais une classe ExplorerGroup)
        nb_enemies = 2 + difficulty * 2
        positions = list(product(range(GRID_W), range(int(GRID_H * 4 / 14))))
        pos1 = sample(positions, min(nb_enemies, len(positions)))
        ally_pos = list(
            product(range(GRID_W), range(int(GRID_H * 10 / 14), int(GRID_H)))
        )
        fourmis_nwar.append(AntPuppet(1))  # Pour des tests
        fourmis_nwar.append(AntPuppet(1))
        pos2 = sample(ally_pos, randint(1, len(fourmis_nwar)))
        protected_tiles = set(pos1 + pos2 + list(ressources_dispos.keys()))
        bomb_tiles = {tile for tile in bomb_tiles if tile not in protected_tiles}
        friendlies = (
            [
                Unit(x, y, img_fourmi, "noir", ant.power)
                for ant, (x, y) in zip(fourmis_nwar, pos2)
            ]
            if len(fourmis_nwar) > 0
            else []
        )

        units = [
            choices(
                [
                    Unit(x, y, img_fourmi, "rouge", power=difficulty),
                    Unit(
                        x,
                        y,
                        img_scarab,
                        "rouge",
                        power=difficulty,
                        points=3,
                        diagonal=True,
                    ),
                ],
                weights=(4, 1),
                k=1,
            )[0]
            for x, y in pos1
        ]

        # units=[Unit(0,0,img_fourmi,"rouge",power=difficulty)]
        units += friendlies

        turn_index = 0
        shuffle(units)
        active = units[turn_index]
        grid = Grid(GRID_W, GRID_H)
        running = True

        while running:
            game_surface.fill((0, 0, 0))
            ui_surface.fill((30, 30, 30))
            grid.draw(game_surface, bomb_tiles)
            # screen.fill((0,0,0))
            # grid.draw(screen)
            for ressource in ressources_obj:
                ressource.draw(game_surface)
            friendlies = [u for u in units if u.team == "noir"]
            grid.draw_reachable_tiles(active, game_surface, units)
            mouse = pygame.mouse.get_pos()
            for u in units:
                u.is_static()
                u.draw(game_surface)
                # TODO:Check overlap to display the possible movements
                if mouse_over(u):
                    if u is not active:
                        grid.draw_reachable_tiles(
                            u, game_surface, units, color=(255, 0, 0)
                        )

            self.sidebar.draw(ui_surface, units, active, colony)
            screen.blit(game_surface, (0, 0))
            screen.blit(ui_surface, (GRID_WIDTH, 0))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()
                    return
                print(active.team, active.points, active.tile())

                if (
                    active.points > 0
                    and (
                        len(friendlies) > 0
                        and len([u for u in units if u.team == "rouge"]) > 0
                    )
                    and active.static_state
                ):
                    enemies = [u for u in units if u.team != active.team]
                    if active.team != "noir" or auto_resolve:
                        target = closest_enemy(active, enemies, grid, units)
                        print(target)
                        if target is not None:
                            blocked = [
                                u.tile()
                                for u in units
                                if (u is not active) and (u not in enemies)
                            ]
                            path = shortest_path(
                                active.tile(),
                                target.tile(),
                                grid.graph,
                                grid.width,
                                blocked,
                                diagonals=active.diagonal,
                                diagonal_edges=grid.diagonal_edges,
                            )
                            print(path)
                            if path:
                                if active.points >= grid.weights[path[0]]:
                                    active.points -= grid.weights[path[0]]

                                    active.move_to(*path[0])
                                else:
                                    active.points = 0

                    if active.team == "noir" and not auto_resolve:
                        if event.type == pygame.KEYDOWN:
                            tiles = reachable_tiles_nx(active, grid, units)
                            if (active.x, active.y) in ressources_dispos.keys():
                                colony.add_to_stock(
                                    ressources_dispos[(active.x, active.y)]
                                )
                                ressources_dispos.pop((active.x, active.y))
                            if (
                                event.key == pygame.K_LEFT
                                and active.x > 0
                                and all(
                                    [
                                        (active.x - 1, active.y) != (u.x, u.y)
                                        for u in friendlies
                                    ]
                                )
                                and (active.x - 1, active.y) in tiles
                            ):
                                active.points -= grid.weights[(active.x - 1, active.y)]
                                active.orientation = True
                                active.move_to(active.x - 1, active.y)

                            elif (
                                event.key == pygame.K_RIGHT
                                and active.x < grid.width - 1
                                and all(
                                    [
                                        (active.x + 1, active.y) != (u.x, u.y)
                                        for u in friendlies
                                    ]
                                )
                                and (active.x + 1, active.y) in tiles
                            ):
                                active.points -= grid.weights[(active.x + 1, active.y)]
                                active.orientation = False
                                active.move_to(active.x + 1, active.y)

                            elif (
                                event.key == pygame.K_UP
                                and active.y > 0
                                and all(
                                    [
                                        (active.x, active.y - 1) != (u.x, u.y)
                                        for u in friendlies
                                    ]
                                )
                                and (active.x, active.y - 1) in tiles
                            ):
                                active.points -= grid.weights[(active.x, active.y - 1)]
                                active.move_to(active.x, active.y - 1)

                            elif (
                                event.key == pygame.K_DOWN
                                and active.y < grid.height - 1
                                and all(
                                    [
                                        (active.x, active.y + 1) != (u.x, u.y)
                                        for u in friendlies
                                    ]
                                )
                                and (active.x, active.y + 1) in tiles
                            ):
                                active.points -= grid.weights[(active.x, active.y + 1)]
                                active.move_to(active.x, active.y + 1)
                            elif event.key == pygame.K_SPACE:
                                active.points = 0

                    print(active)
                    active.is_static()
                    if (active.x, active.y) in bomb_tiles:
                        bomb = Bomb(active.x, active.y)
                        dead_units = bomb.explode(units)
                        for u in dead_units:
                            if u in units:
                                units.remove(u)
                        bomb_tiles.remove((active.x, active.y))
                    for enemy in enemies:
                        if (enemy.x, enemy.y) == (active.x, active.y):
                            units.remove(enemy)

                    friendlies = [u for u in units if u.team == "noir"]
                    print(len(friendlies), len([u for u in units if u.team == "rouge"]))
                    if len(friendlies) < 1:
                        self.battle_won = False
                        running = False
                    if len([u for u in units if u.team == "rouge"]) < 1:
                        self.battle_won = True
                        running = False
                if len(reachable_tiles_nx(active, grid, units)) <= 0:
                    active.points = 0
                elif active.points <= 0:
                    active.reset_turn()
                    turn_index = (turn_index + 1) % len(units)
                    active = units[turn_index]

            pygame.display.flip()
