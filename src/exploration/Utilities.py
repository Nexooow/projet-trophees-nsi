import heapq
from random import randint
import networkx as nx
import pygame


def xy_to_node(x, y, cols):
    return y * cols + x


def node_to_xy(node, cols):
    return (node % cols, node // cols)


def neighbors(x, y, width, height, diagonal=False):
    dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    if diagonal:
        dirs += [(1, 1), (-1, -1), (1, -1), (-1, 1)]
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if 0 <= nx < width and 0 <= ny < height:
            yield nx, ny


def reachable_tiles(x, y, points, grid):

    reachable = {}
    pq = [(0, x, y)]

    while pq:
        cost, cx, cy = heapq.heappop(pq)

        if cost > points:
            continue

        if (cx, cy) in reachable and cost >= reachable[(cx, cy)]:
            continue

        reachable[(cx, cy)] = cost

        for nx_, ny_ in neighbors(cx, cy, grid.width, grid.height):
            tile_cost = grid.weights[(nx_, ny_)]
            heapq.heappush(pq, (cost + tile_cost, nx_, ny_))
    return reachable


def reachable_tiles_nx(unit, grid, units):
    G = grid.graph.copy()
    if unit.diagonal:
        G.add_edges_from(grid.diagonal_edges)
    blocked = [u.tile() for u in units if (u.team == unit.team) and (u is not unit)]
    for pos in blocked:
        if G.has_node(pos):
            G.remove_node(pos)
    lengths = nx.single_source_dijkstra_path_length(
        G, unit.tile(), cutoff=unit.points, weight="weight"
    )
    return lengths


def shortest_path(
    start,
    target,
    graph,
    grid_width,
    blocked_positions=(),
    diagonals=False,
    diagonal_edges=(),
):
    G = graph.copy()
    if diagonals:
        G.add_edges_from(diagonal_edges)
    print(G.nodes)
    print(blocked_positions)
    for x, y in blocked_positions:
        try:
            G.remove_node((x, y))
        except nx.NetworkXError:
            pass
    try:
        print(G.nodes)
        print(G)
        path = nx.shortest_path(
            G, (start[0], start[1]), (target[0], target[1]), weight="weight"
        )
    except nx.NetworkXNoPath:
        return []
    return path[1:]


terrains = {
    "dirt": {"weight": 1, "img": ""},
    "mud": {"weight": 2, "img": ""},
    "water": {"weight": 3, "img": ""},
    "stone": {"weight": float("inf"), "img": ""},
}


def weight_to_color(weight):
    return {
        1: (50, 180, 50),
        2: (160, 120, 60),
        3: (150, 100, 0),
        4: (128, 128, 128),
    }.get(weight, (100, 100, 100))
    # return terrains[weight]["weight"] if weight in terrains else ""


def closest_enemy(unit, enemies, grid, units):
    blocked = [(u.x, u.y) for u in units if u is not unit and u not in enemies]
    closest = None
    dist = float("inf")
    for enemy in enemies:
        path = shortest_path(
            unit.tile(),
            enemy.tile(),
            grid.graph,
            grid.width,
            blocked,
            diagonals=unit.diagonal,
            diagonal_edges=grid.diagonal_edges,
        )
        if path and len(path) < dist:
            dist = len(path)
            closest = enemy
    return closest


def mouse_over(unit):
    mouse = pygame.mouse.get_pos()
    if not unit.rect.collidepoint(mouse):
        return False
    return unit.mask.get_at((mouse[0] - unit.rect.x, mouse[1] - unit.rect.y))
def generate_tiles(base_color, tile_size):
    tiles = []
    for mask in range(16):
        surf = pygame.Surface((tile_size, tile_size))
        shade = mask * 5
        color = (
            min(base_color[0] + shade, 255),
            min(base_color[1] + shade, 255),
            min(base_color[2] + shade, 255),
        )
        surf.fill(color)
        tiles.append(surf)
    return tiles
