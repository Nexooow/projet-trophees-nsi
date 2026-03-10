import typing

from colony.Ant import Ant
from colony.TaskManager import Task


class Nurse(Ant):
    
    def __init__(self, colony, data: dict, pos):
        super().__init__(colony, "nurse", data, pos)