"""
Tests pour les classes / fonctions utilitaires.
"""

import pygame

from sources.lib.file import File
from sources.lib.grid import Grid
from sources.lib.utils import distance, lerp, lerp_color, normalize_rect, parse_color


class TestUtils:
    def test_grid(self):
        grid = Grid((40, 40), 0)
        assert grid.width == 5
        assert grid.height == 5
        assert len(grid.grid) == 5 and len(grid.grid[0]) == 5
        for x in range(grid.width):
            for y in range(grid.height):
                assert grid.grid[y][x]["state"] == "full"
                if x == y:
                    grid.set_cell_state(x, y, "empty")

        # Test A*
        path_possible = grid.a_star((0, 0), (4, 4))
        assert path_possible == [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4)]

        path_impossible = grid.a_star((0, 4), (4, 0))
        assert path_impossible is None

    def test_file_basic(self):
        f = File()
        assert f.est_vide()
        f.enfiler("A")
        assert not f.est_vide()
        assert f.sommet() == "A"
        assert f.defiler() == "A"
        assert f.est_vide()

    def test_file_priority(self):
        f = File()
        f.enfiler("A", priority=1)
        f.enfiler("B", priority=3)
        f.enfiler("C", priority=2)

        assert f.defiler() == "B"
        assert f.defiler() == "C"
        assert f.defiler() == "A"
        assert f.est_vide()

    def test_file_init(self):
        f = File(["A", "B"])
        assert f.defiler() == "A"
        assert f.defiler() == "B"
        assert f.est_vide()

    def test_normalize_rect(self):
        # Initialise pygame pour éviter les erreurs avec Rect
        pygame.display.init()
        try:
            rect = normalize_rect((10, 20, 30, 40))
            assert isinstance(rect, pygame.Rect)
            assert rect.x == 10 and rect.y == 20 and rect.w == 30 and rect.h == 40

            rect2 = normalize_rect(rect)
            assert rect2 == rect
            assert rect2 is not rect  # Copie

            assert normalize_rect(None) == pygame.Rect(0, 0, 0, 0)
        finally:
            pygame.display.quit()

    def test_parse_color(self):
        pygame.display.init()
        try:
            assert parse_color(None) is None
            assert parse_color((255, 0, 0)) == (255, 0, 0)
            # pygame.Color convertit en tuple RGBA (4 éléments)
            assert parse_color("#FF0000") == (255, 0, 0, 255)
        finally:
            pygame.display.quit()

    def test_distance(self):
        assert distance((0, 0), (3, 4)) == 5.0
        assert distance((1, 1), (1, 1)) == 0.0

    def test_lerp(self):
        assert lerp(0, 10, 0.5) == 5.0
        assert lerp(10, 20, 0) == 10.0
        assert lerp(10, 20, 1) == 20.0

    def test_lerp_color(self):
        c1 = (0, 0, 0)
        c2 = (255, 255, 255)
        assert lerp_color(c1, c2, 0.5) == (127, 127, 127)
        assert lerp_color(c1, c2, 0) == (0, 0, 0)
        assert lerp_color(c1, c2, 1) == (255, 255, 255)
