from src.core.GameManager import GameManager
import pygame
    
class TestGame:
    
    def start (self):
        pygame.init()
        game = GameManager()
        assert game.is_running()
        return game
        
    def test_default_state(self):
        game = self.start()
        assert game.state.current_state == "menu"
        game.update([])
        game.draw()
        assert game.is_running()
        
    def test_colony_state (self):
        game = self.start()
        game.state.set_state("colony")
        assert game.state.current_state == "colony"
        game.update([])
        game.draw()
        assert game.is_running()
        
    def test_expedition_state (self):
        game = self.start()
        game.state.set_state("expedition")
        assert game.state.current_state == "expedition"
        game.update([])
        game.draw()
        assert game.is_running()
    