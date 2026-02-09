import pygame
import pygame_gui

from .State import State
from colony.TaskManager import TaskManager
from utils.grid import Grid

class ColonyState (State):

    def __init__ (self, state_manager):
        super().__init__(state_manager, "colony", [])
        self.tasks = TaskManager(self)

        self.grid = Grid(self.game.height * 0.15, self.game.screen.get_size())
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
                    pygame.draw.rect(self.game.screen, (82, 40, 23), (x + j, y + i, 1, 1))

    def draw_grid(self):
        start_height = self.game.height * 0.15
        for x, y, cell in self.grid:
            if cell["state"] == "full":
                pygame.draw.rect(self.game.screen, (82, 40, 23), (x * self.grid.cell_size, start_height + y * self.grid.cell_size, self.grid.cell_size, self.grid.cell_size))
            elif cell["state"] == "partial":
                pygame.draw.rect(self.game.screen, (150, 0, 0), (x * self.grid.cell_size, start_height + y * self.grid.cell_size, self.grid.cell_size, self.grid.cell_size))
                #self.draw_bitmap(cell["bitmap"], x, y)

    def update (self, events):
        pass
                
    def draw (self):
        pygame.draw.rect(self.game.screen, (66, 179, 213), (0, 0, self.game.width, self.game.height*0.12))
        # TODO: entre 0.12 et 0.15, faire l'herbe et la végétation pour la transition entre extérieur et la partie
        #  terreuse de la colonie
        pygame.draw.rect(self.game.screen, (64, 125, 42), (0, self.game.height*0.12, self.game.width, self.game.height*0.04))
        pygame.draw.rect(self.game.screen, (66, 31, 17), (0, self.game.height*0.15, self.game.width, self.game.height*0.85))
        self.draw_grid()