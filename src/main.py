import pygame

from core.GameManager import GameManager

pygame.init()

game = GameManager()

while game.is_running():
    game.update(pygame.event.get())
    game.draw()

    pygame.display.flip()
    game.clock.tick(60)

pygame.quit()
