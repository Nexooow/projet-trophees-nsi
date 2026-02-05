import pygame

from Jeu import Jeu

# pygame setup
pygame.init()
clock = pygame.time.Clock()
running = True

jeu = Jeu()

while jeu.is_running():

    jeu.update(pygame.event.get())

    jeu.draw()
    
    pygame.display.flip()

    clock.tick(60)

pygame.quit()