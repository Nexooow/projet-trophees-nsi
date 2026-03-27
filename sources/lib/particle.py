import pygame

class Particle:

    def __init__ (self, size: tuple):
        self.surface = pygame.Surface(size, pygame.SRCALPHA) 
        self.color = pygame.Color()
        self.position = pygame.Vector2(0, 0)
        self.direction = pygame.Vector2(0, 0)
        self.speed = 1
        self.tilt = 0

    def update (self):
        self.position = self.direction * self.speed

    def draw (self, dest_surf):
        final_surf = pygame.transform.rotate(self.surface, self.tilt)
        dest_surf.blit(final_surf)
