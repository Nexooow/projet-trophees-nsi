import pygame
from .Utilities import weight_to_color,reachable_tiles_nx,mouse_over
RESSOURCES_IMAGES={
    "nom":pygame.image.load("./assets/fonts/ant.png")
}
RESSOURCES=["nom"]
class BattleRenderer:
    def __init__(self, model, screen, sidebar):
        self.model = model
        self.screen = screen
        self.sidebar = sidebar
        self.game_surface = pygame.Surface(
            (screen.get_width() - 250, screen.get_height())
        )
        self.ui_surface = pygame.Surface((250, screen.get_height()))

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

    def draw_resources(self):
        for res in self.model.resources_obj:
            offset = res.draw_offset()
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
