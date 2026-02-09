from utils.file import File

class TaskManager:
    """
    Classe qui gère les tâches de la colonie, comme la construction de nouvelles pièces, la recherche de nouvelles technologies, etc.
    Les tâches sont ensuite délégués aux fourmis qui les exécutent en fonction de leurs compétences et de leur disponibilité.
    """

    def __init__(self, colony):
        self.colony = colony
        self.tasks = File()

    def add_task(self, task: dict):
        """
        Ajoute une tâche à exécuter, qui sera ensuite prise en charge par les fourmis disponibles.
        """
        pass
