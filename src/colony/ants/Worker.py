from colony.Ant import Ant
from colony.TaskManager import Task

class Worker(Ant):
    def __init__(self, colony, data: dict, pos):
        super().__init__(colony, "worker", data, pos)
        
    def execute_task(self, task: "Task"):
        pass