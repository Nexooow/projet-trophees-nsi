import pygame
from .Utilities import weight_to_color,reachable_tiles_nx,mouse_over
from lib.utils import import_asset
from random import randint
from lib.perlin import Perlin
RESSOURCES_IMAGES={
    "nom":import_asset("fonts", "ant.png")
}
RESSOURCES=["nom"]
class BattleRenderer:
    def __init__(self, model, screen, sidebar):
        self.model = model
        self.screen = screen
        self.sidebar = sidebar
        self.perlin = Perlin(seed=123, scale=8, octaves=2, normalize=True)
        self.game_surface = pygame.Surface(
            (screen.get_width() - 250, screen.get_height())
        )
        self.ui_surface = pygame.Surface((250, screen.get_height()))
        self.tile_size=self.model.grid.tile
        self.base_colors = {
            1: (210,180,120),
            2: (80,160,80),
            3: (130,90,60),
            4: (120,120,120),
        }
        self.tiles={
            weight:self.generate_autotiles(color)
            for weight,color in self.base_colors.items()
        }
    def make_autotile(self,base_color,mask):
        surf=pygame.Surface((self.tile_size,self.tile_size))
        surf.fill(base_color)
        noise=self.perlin.noise_map(self.tile_size,self.tile_size)
        for x in range(self.tile_size):
            for y in range(self.tile_size):
                n=noise[x][y]
                shade=int((n-0.5)*40)
                color=(
                    max(min(base_color[0] + shade, 255), 0),
                    max(min(base_color[1] + shade, 255), 0),
                    max(min(base_color[2] + shade, 255), 0),
                )
                surf.set_at((x,y),color)
        edge_color=tuple(max(c-30,0) for c in base_color)
        if not (mask & 1):
            pygame.draw.rect(surf,edge_color,(0,0,self.tile_size,4))
        if not (mask & 2):
            pygame.draw.rect(surf,edge_color,(self.tile_size-4,0,4,self.tile_size))
        if not (mask & 4):
            pygame.draw.rect(surf,edge_color,(0,self.tile_size-4,self.tile_size,4))
        if not (mask & 8):
            pygame.draw.rect(surf,edge_color,(0,0,4,self.tile_size))
        return surf
    def generate_autotiles(self,base_color):
        return [self.make_autotile(base_color, mask) for mask in range(16)]
    def draw(self):
        self.game_surface.fill((0, 0, 0))
        self.ui_surface.fill((30, 30, 30))

        self.draw_grid()
        self.draw_resources()
        self.draw_units()
        self.draw_sidebar()

        self.screen.blit(self.game_surface, (0, 0))
        self.screen.blit(self.ui_surface, (self.game_surface.get_width(), 0))
        pygame.display.flip()
    """
    def draw_grid(self):
        grid = self.model.grid
        for x in range(grid.width):
            for y in range(grid.height):
                rect = pygame.Rect(x * grid.tile, y * grid.tile, grid.tile, grid.tile)
                color = weight_to_color(grid.weights[(x, y)])
                pygame.draw.rect(self.game_surface, color, rect)
                if (x, y) in self.model.bomb_tiles:
                    pygame.draw.rect(self.game_surface, (200, 50, 50), rect)
                pygame.draw.rect(self.game_surface, (255, 255, 255), rect, 1)
        # Mise en couleur des tiles atteignables
        tiles = reachable_tiles_nx(self.model.active_unit, grid, self.model.units)
        for x, y in tiles.keys():
            pygame.draw.rect(
                self.game_surface,
                (255, 255, 0),
                pygame.Rect(x * grid.tile, y * grid.tile, grid.tile, grid.tile),
                2,
            )
    """
    def draw_grid(self):
        grid = self.model.grid
        for x in range(grid.width):
            for y in range(grid.height):
                rect = pygame.Rect(x * grid.tile, y * grid.tile, grid.tile, grid.tile)
                weight=grid.weights[(x,y)]
                mask=grid.get_mask(x,y)
                tile_img=self.tiles[weight][mask]
                self.game_surface.blit(tile_img,rect)
                if (x, y) in self.model.bomb_tiles:
                    pygame.draw.rect(self.game_surface, (200, 50, 50), rect)
                pygame.draw.rect(self.game_surface, (255, 255, 255), rect, 1)
        # Mise en couleur des tiles atteignables
        tiles = reachable_tiles_nx(self.model.active_unit, grid, self.model.units)
        for x, y in tiles.keys():
            pygame.draw.rect(
                self.game_surface,
                (255, 255, 0),
                pygame.Rect(x * grid.tile, y * grid.tile, grid.tile, grid.tile),
                2,
            )
    def draw_resources(self):
        for res in self.model.resources_obj:
            offset = res.draw_offset()
            self.game_surface.blit(RESSOURCES_IMAGES[res.resource], (res.x * 50, res.y * 50 + offset))
            self.game_surface.blit(RESSOURCES_IMAGES[res.resource], (res.x * 50, res.y * 50 + offset))

    def draw_units(self):
        mouse = pygame.mouse.get_pos()
        for unit in self.model.units:
            unit.is_static()
            unit.draw(self.game_surface)
            if mouse_over(unit) and unit != self.model.active_unit:
                tiles = reachable_tiles_nx(unit, self.model.grid, self.model.units)
                for x, y in tiles.keys():
                    pygame.draw.rect(
                        self.game_surface,
                        (255, 0, 0),
                        pygame.Rect(x * 50, y * 50, 50, 50),
                        2,
                    )

    def draw_sidebar(self):
        self.sidebar.draw(
            self.ui_surface, self.model.units, self.model.active_unit, None
        )
