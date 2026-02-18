import typing

from lib.file import File

assign_tasks = {
    "dig": "worker",
    "bring_food": "worker",
    "build": "worker",
    "fight": "warrior",
    "heal": "nurse",
    "research": "scientist",
    "explore": "explorer",
}


class TaskManager:
    """
    Classe qui gère les tâches de la colonie, comme la construction de nouvelles pièces, la recherche de nouvelles technologies, etc.
    Les tâches sont ensuite délégués aux fourmis qui les exécutent en fonction de leurs compétences et de leur disponibilité.
    """

    def __init__(self, colony):
        self.colony = colony
        self.assigned: dict[str, typing.Optional[str]] = {}
        self.tasks = {
            "worker": File(),
            "nurse": File(),
            "warrior": File(),
            "scientist": File(),
            "explorer": File(),
        }

    def add_task(self, task: dict) -> bool:
        """
        Ajoute une tâche à exécuter, qui sera ensuite prise en charge par les fourmis disponibles.
        Renvoie True si la tâche est éxécutée directement ou False si elle est ajoutée à la file d'attente.
        """
        assert "type" in task
        assert "id" in task
        ant_type = assign_tasks[task["type"]]
        if ant_type is None:
            return False
        self.tasks[ant_type].enfiler(task)
        self.handle_tasks()
        return True

    def mark_as_finished(self, task_id):
        del self.tasks[task_id]
        self.handle_tasks()

    def handle_tasks(self):
        """
        Gère les tâches en fonction de la disponibilité des fourmis.
        """
        pass
