"""
Tests pour les classes / fonctions utilitaires.
"""

from src.lib.grid import Grid
from src.lib.file import File

class TestUtils:
    
    def test_grid(self):
        grid = Grid((40, 40))
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
