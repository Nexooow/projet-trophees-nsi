from src.core.GameManager import GameManager
import pygame

def test_start ():
    """
    Test si le jeu démarre
    """
    pygame.init()
    game = GameManager()
    
    assert game.is_running()
    
    game.update([])
    game.draw()
    
    pygame.quit()