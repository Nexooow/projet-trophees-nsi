"""
Tests pour les classes / fonctions utilitaires.
"""

from src.utils.grid import Grid

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
