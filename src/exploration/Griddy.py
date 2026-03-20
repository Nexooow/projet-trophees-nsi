import heapq
import math
from itertools import product
from random import choice, choices, randint, random, sample, shuffle

import networkx as netx
import pygame

from lib.perlin import Perlin
from lib.utils import import_asset

from .AntPuppet import AntPuppet
from .ExplorerGroup import *
from .Unit import *
from .Utilities import *

RESSOURCES_IMAGES = {"nom": import_asset("ant.png")}
RESSOURCES = ["nom"]
pygame.init()

class Sidebar:
    """
    Représente la barre latérale affichant les informations sur l'expédition en cours, les unités, les ressources, etc.
    """
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def draw(self, screen, units, active, colony,ressources):
        screen.fill((30, 30, 30))
        font = pygame.font.SysFont(None, 28)
        friendlies = len([u for u in units if u.team == "noir"])
        enemies = len([u for u in units if u.team == "rouge"])
        if colony is None:
            lines = [
                f"Active Team: {active.team}",
                f"Action Points: {active.points}",
                "",
                f"Friendlies: {friendlies}",
                f"Enemies: {enemies}",
                "",
                "Resources:",
                # TODO: Montrer les ressources que l'expédition a récup / celles qu'il y a au total
            ]
        else:
            lines=[

                f"Active Team: {active.team}",
                f"Action Points: {active.points}",
                "",
                f"Friendlies: {friendlies}",
                f"Enemies: {enemies}",
                "",
                f"Resources: {len(colony.ressources)}/{ressources}",
                # TODO: Montrer les ressources que l'expédition a récup / celles qu'il y a au total
            ]
        y = 20
        for line in lines:
            text = font.render(line, True, (255, 255, 255))
            screen.blit(text, (20, y))
            y += 35


