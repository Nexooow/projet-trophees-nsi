import pygame
import pygame_gui

from .State import State
from colony.TaskManager import TaskManager
from utils.grid import Grid

class ColonyState (State):

    def __init__ (self, state_manager):
        super().__init__(state_manager, "colony", [])
        self.tasks = TaskManager(self)
        self.width = 2048
        self.height = 1152
        self.world = pygame.Surface((self.width, self.height), pygame.SRCALPHA | pygame.HWSURFACE)
        self.camera_x = 0
        self.camera_y = 0

        self.grid = Grid(self.height*0.15, self.world.get_size())
        self.rooms = []

        self.ants = []
        # self.ennemies = []

        self.food = 0
        # self.science = 0

        self.selections = set()

    def draw_bitmap(self, bitmap, x, y):
        for i in range(len(bitmap)):
            for j in range(len(bitmap[i])):
                if bitmap[i][j]:
                    pygame.draw.rect(self.world, (82, 40, 23), (x + j, y + i, 1, 1))

    def draw_grid(self):
        start_height = self.height * 0.15
        for x, y, cell in self.grid:
            if cell["state"] == "full":
                pygame.draw.rect(self.world, (82, 40, 23), (x * self.grid.cell_size, start_height + y * self.grid.cell_size, self.grid.cell_size, self.grid.cell_size))
            elif cell["state"] == "partial":
                pygame.draw.rect(self.world, (150, 0, 0), (x * self.grid.cell_size, start_height + y * self.grid.cell_size, self.grid.cell_size, self.grid.cell_size))
                #self.draw_bitmap(cell["bitmap"], x, y)

    def update (self, events):
        keys = pygame.key.get_pressed()
        if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and self.camera_x > 0:
            self.camera_x = min(self.width, self.camera_x-10)
        elif keys[pygame.K_LEFT] or keys[pygame.K_q]:
            self.camera_x = max(0, self.camera_x+10)
        if keys[pygame.K_UP] or keys[pygame.K_z]:
            self.camera_y = max(0, self.camera_y+10)
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.camera_y = min(self.height, self.camera_y-10)
                
    def draw (self):
        pygame.draw.rect(self.world, (66, 179, 213), (0, 0, self.width, self.height*0.12))
        # TODO: entre 0.12 et 0.15, faire l'herbe et la végétation pour la transition entre extérieur et la partie
        #  terreuse de la colonie
        pygame.draw.rect(self.world, (64, 125, 42), (0, self.height*0.12, self.width, self.height*0.04))
        pygame.draw.rect(self.world, (66, 31, 17), (0, self.height*0.15, self.width, self.height*0.85))
        self.draw_grid()
        self.game.screen.blit(self.world, (self.camera_x, self.camera_y))