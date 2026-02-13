import typing
from utils.file import File

assign_tasks = {
    "dig": "worker",
    "bring_food": "worker",
    "build": "worker",
    "fight": "soldier"
}

class TaskManager:
    """
    Classe qui gère les tâches de la colonie, comme la construction de nouvelles pièces, la recherche de nouvelles technologies, etc.
    Les tâches sont ensuite délégués aux fourmis qui les exécutent en fonction de leurs compétences et de leur disponibilité.
    """

    def __init__(self, colony):
        self.colony = colony
        self.assigned: dict[str, typing.Optional[str]] = {} 
        self.tasks = {}
        self.queue = File()

    def add_task(self, task: dict):
        """
        Ajoute une tâche à exécuter, qui sera ensuite prise en charge par les fourmis disponibles.
        """
        assert "type" in task
        assert "id" in task
        self.tasks[task["id"]] = task
        self.queue.enfiler(task["id"], priority=task["priority"] if "priority" in task else 0)
        self.handle_tasks()
    
    def mark_as_finished (self, task_id):
        del self.tasks[task_id]
        self.handle_tasks()
        
    def handle_tasks (self):
        """
        ...
        """
        task = self.tasks[self.queue.sommet()]
        
