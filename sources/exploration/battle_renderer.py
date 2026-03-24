import pygame
from lib.pathfinding import reachable_tiles_nx
from lib.perlin import Perlin
from lib.utils import import_asset, mouse_over, use_font

RESSOURCES_IMAGES = {"nom": import_asset("icons", "leaf.png")}
RESSOURCES = ["nom"]
IMG = {
    "grass": import_asset("icons", "grass.png"),
    "rock": import_asset("icons", "rock.png"),
    "bomb": import_asset("icons", "bomb.png"),
}
TILE_SIZE = 50


class Sidebar:
    """
    Barre latérale affichant les informations sur la bataille en cours
    (équipes, points d'action, ressources).
    """

    def __init__(self, width, height):
        self.width = width
        self.height = height

    def draw(self, screen, units, active, colony, ressources):
        screen.fill((30, 30, 30))
        font = use_font(28)
        friendlies = len([u for u in units if u.team == "noir"])
        enemies = len([u for u in units if u.team == "rouge"])
        if colony is None:
            lines = [
                f"Active Team: {active.team}",
                f"Action Points: {active.points}",
                "",
                f"Friendlies: {friendlies}",
                f"Enemies: {enemies}",
                "",
                "Resources:",
                # TODO: Montrer les ressources récupérées / disponibles
            ]
        else:
            lines = [
                f"Active Team: {active.team}",
                f"Action Points: {active.points}",
                "",
                f"Friendlies: {friendlies}",
                f"Enemies: {enemies}",
                "",
                f"Resources: {len(colony.ressources)}/{ressources}",
                # TODO: Montrer les ressources récupérées / disponibles
            ]
        y = 20
        for line in lines:
            text = font.render(line, True, (255, 255, 255))
            screen.blit(text, (20, y))
            y += 35


class BattleRenderer:
    def __init__(self, model, screen, sidebar):
        self.model = model
        self.screen = screen
        self.sidebar = sidebar
        self.perlin = Perlin(scale=8, octaves=2, normalize=True)
        self.game_surface = pygame.Surface(
            (screen.get_width() - 250, screen.get_height())
        )
        self.ui_surface = pygame.Surface(
            (250, screen.get_height()),
        )
        available_width = screen.get_width() - 250
        available_height = screen.get_height()
        
        self.base_colors = {
            1: (210, 180, 120),
            2: (80, 160, 80),
            3: (130, 90, 60),
            4: (120, 120, 120),
        }

        # Calcul de l'offset pour centrer la grille dans la zone de jeu
        grid = self.model.grid
        tile_w = available_width // grid.width
        tile_h = available_height // grid.height
        self.tile_size = min(tile_w, tile_h)
        self.model.grid.tile = self.tile_size
        for unit in self.model.units:
            unit.update_tile_size(self.tile_size)
        self.bomb_img = pygame.transform.scale(
            IMG["bomb"], (self.tile_size, self.tile_size)
        )
        grid_px_w = grid.width * self.tile_size
        grid_px_h = grid.height * self.tile_size
        self.grid_offset_x = max(0, (self.game_surface.get_width() - grid_px_w) // 2)
        self.grid_offset_y = max(0, (self.game_surface.get_height() - grid_px_h) // 2)

        # Pré-calcul de l'overlay des lignes de grille (semi-transparent, une seule fois)
        
        self.tiles = {
            weight: self.generate_autotiles(color)
            for weight, color in self.base_colors.items()
        }
        self.grid_overlay = pygame.Surface((grid_px_w, grid_px_h), pygame.SRCALPHA)
        for x in range(grid.width):
            for y in range(grid.height):
                rect = pygame.Rect(
                    x * self.tile_size,
                    y * self.tile_size,
                    self.tile_size,
                    self.tile_size,
                )
                pygame.draw.rect(self.grid_overlay, (255, 255, 255, 25), rect, 1)

    def make_autotile(self, base_color, mask):
        surf = pygame.Surface((self.tile_size, self.tile_size))
        surf.fill(base_color)
        noise = self.perlin.noise_map(self.tile_size, self.tile_size)
        for x in range(self.tile_size):
            for y in range(self.tile_size):
                n = noise[x][y]
                shade = int((n - 0.5) * 40)
                color = (
                    max(min(base_color[0] + shade, 255), 0),
                    max(min(base_color[1] + shade, 255), 0),
                    max(min(base_color[2] + shade, 255), 0),
                )
                surf.set_at((x, y), color)
        edge_color = tuple(max(c - 30, 0) for c in base_color)
        if not (mask & 1):
            pygame.draw.rect(surf, edge_color, (0, 0, self.tile_size, 4))
        if not (mask & 2):
            pygame.draw.rect(
                surf, edge_color, (self.tile_size - 4, 0, 4, self.tile_size)
            )
        if not (mask & 4):
            pygame.draw.rect(
                surf, edge_color, (0, self.tile_size - 4, self.tile_size, 4)
            )
        if not (mask & 8):
            pygame.draw.rect(surf, edge_color, (0, 0, 4, self.tile_size))
        return surf

    def generate_autotiles(self, base_color):
        return [self.make_autotile(base_color, mask) for mask in range(16)]

    def draw(self):
        self.game_surface.fill((0, 0, 0))
        self.ui_surface.fill((30, 30, 30))

        self.draw_grid()
        self.draw_useless_obj()
        self.draw_resources()
        self.draw_units()
        self.draw_sidebar()

        self.screen.blit(self.game_surface, (0, 0))
        self.screen.blit(self.ui_surface, (self.game_surface.get_width(), 0))
        pygame.display.flip()

    def draw_grid(self):
        grid = self.model.grid
        ox, oy = self.grid_offset_x, self.grid_offset_y

        for x in range(grid.width):
            for y in range(grid.height):
                rect = pygame.Rect(
                    x * grid.tile + ox,
                    y * grid.tile + oy,
                    grid.tile,
                    grid.tile,
                )
                weight = grid.weights[(x, y)]
                mask = grid.get_mask(x, y)
                tile_img = self.tiles[weight][mask]
                self.game_surface.blit(tile_img, rect)
                if (x, y) in self.model.bomb_tiles:
                    img = self.bomb_img
                    dest = img.get_rect(center=rect.center)
                    self.game_surface.blit(img, dest)

        # Overlay semi-transparent des lignes de grille (pré-calculé)
        self.game_surface.blit(self.grid_overlay, (ox, oy))

        # Mise en couleur des cases atteignables
        tiles = reachable_tiles_nx(self.model.active_unit, grid, self.model.units)
        for x, y in tiles.keys():
            pygame.draw.rect(
                self.game_surface,
                (255, 255, 0),
                pygame.Rect(
                    x * grid.tile + ox,
                    y * grid.tile + oy,
                    grid.tile,
                    grid.tile,
                ),
                2,
            )

    def draw_resources(self):
        ox, oy = self.grid_offset_x, self.grid_offset_y
        for res in self.model.resources_obj:
            img = pygame.transform.scale(
                RESSOURCES_IMAGES[res.resource],
                (self.tile_size // 2, self.tile_size // 2)
            )
            img_w, img_h = img.get_size()
            float_offset = res.draw_offset()
            # Centrage horizontal et vertical dans la cellule, avec l'effet de flottement
            draw_x = res.x * self.tile_size + (self.tile_size - img_w) // 2 + ox
            draw_y = (
                res.y * self.tile_size
                + (self.tile_size - img_h) // 2
                + float_offset
                + oy
            )
            self.game_surface.blit(img, (draw_x, draw_y))

    def draw_useless_obj(self):
        ox, oy = self.grid_offset_x, self.grid_offset_y
        for (x, y), obj in self.model.grid.objects.items():
            screen_x = x * self.tile_size + ox
            screen_y = y * self.tile_size + oy

            if obj == "tree":
                self.game_surface.blit(IMG["tree"], (screen_x, screen_y))
            elif obj == "rock":
                self.game_surface.blit(IMG["rock"], (screen_x, screen_y))

    def draw_units(self):
        ox, oy = self.grid_offset_x, self.grid_offset_y
        for unit in self.model.units:
            unit.is_static()
            unit.draw(self.game_surface, ox, oy, self.tile_size)
            if mouse_over(unit) and unit != self.model.active_unit:
                tiles = reachable_tiles_nx(unit, self.model.grid, self.model.units)
                for x, y in tiles.keys():
                    pygame.draw.rect(
                        self.game_surface,
                        (255, 0, 0),
                        pygame.Rect(
                            x * self.tile_size + ox,
                            y * self.tile_size + oy,
                            self.tile_size,
                            self.tile_size,
                        ),
                        2,
                    )

    def draw_sidebar(self):
        self.sidebar.draw(
            self.ui_surface,
            self.model.units,
            self.model.active_unit,
            None,
            len(self.model.resources_obj),
        )
