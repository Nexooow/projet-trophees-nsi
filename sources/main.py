import pygame

from core.GameManager import GameManager
from lib.utils import import_asset

pygame.init()
pygame.display.set_icon(import_asset("icon.png"))
pygame.display.set_caption("Rise of the anthill")
pygame.mixer.init()

game = GameManager()

while game.is_running():
    game.update(pygame.event.get())
    game.draw()

    pygame.display.flip()
    game.clock.tick(60)


pygame.quit()
