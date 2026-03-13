import typing
import uuid

from constants import TASK_ANT_TYPE, TASK_DEFAULT_PRIORITY
from lib.file import File
from lib.utils import distance


class Task:
    def __init__(
        self,
        manager: "TaskManager",
        type: str,
        data: typing.Optional[dict] = None,
        on_start=None,
        on_complete=None,
        on_expired=None,
    ):
        self.manager = manager
        self.id = uuid.uuid4()
        self.type = type
        self.data = data
        self.assigned_to: typing.Optional[uuid.UUID] = None
        self.priority = (
            data["priority"]
            if data and "priority" in data
            else TASK_DEFAULT_PRIORITY[type]
        )
        self.deadline = (
            self.manager.colony.game.time.get_time(data["deadline"])
            if data and "deadline" in data
            else None
        )
        self.on_start = on_start
        self.on_complete = on_complete
        self.on_expired = on_expired

    def is_assigned(self):
        return self.assigned_to is not None

    def is_expired(self):
        return (
            self.deadline is not None
            and self.deadline <= self.manager.colony.game.time.get_time()
        )

    def start(self, assigned_to: uuid.UUID):
        self.assigned_to = assigned_to
        if self.on_start:
            self.on_start()

    def complete(self):
        if self.on_complete:
            self.on_complete()

    def expire(self):
        if self.on_expired:
            self.on_expired()


class TaskManager:
    def __init__(self, colony):
        self.colony = colony
        self.tasks: dict = {}
        self.files: dict = {
            "worker": File(),
            "warrior": File(),
            "nurse": File(),
            "scientist": File(),
            "explorer": File(),
        }

    def get_task(self, task_id: uuid.UUID):
        return self.tasks[task_id]

    def add_task(
        self, type, data=None, on_start=None, on_complete=None, on_expired=None
    ):
        task = Task(
            self,
            type=type,
            data=data,
            on_start=on_start,
            on_complete=on_complete,
            on_expired=on_expired,
        )
        ant_type = TASK_ANT_TYPE[type]
        self.tasks[task.id] = task
        self.files[ant_type].enfiler(task.id, task.priority)

    def delete_task(self, task_id: uuid.UUID):
        if task_id in self.tasks:
            task_data = self.tasks[task_id]
            # On retire la tâche de la file si elle y est encore
            file = self.files[TASK_ANT_TYPE[task_data.type]]
            for i, (tid, _) in enumerate(file.content):
                if tid == task_id:
                    file.content.pop(i)
                    break
            del self.tasks[task_id]

    def complete_task(self, task_id: uuid.UUID):
        self.tasks[task_id].complete()

    def find_available_ants(self, type: str, pos=None):
        ants = []
        for ant in self.colony.ants:
            if ant.type == type and ant.is_available():
                ants.append(ant)
        if pos is None:
            return ants
        return sorted(ants, key=lambda ant: distance(ant.pos, pos))

    def update(self):
        for task in list(self.tasks.values()):
            if task.is_expired():
                task.expire()

        for ant_type, file in self.files.items():
            # On récupère les fourmis disponibles pour ce type
            available_ants = self.find_available_ants(ant_type)
            if not available_ants:
                continue

            # On distribue les tâches en attente aux fourmis disponibles
            while not file.est_vide() and available_ants:
                task_id = file.defiler()
                if task_id not in self.tasks:
                    continue

                task = self.tasks[task_id]
                # Si la tâche est déjà assignée ou expirée, on passe à la suivante
                if task.is_assigned() or task.is_expired():
                    continue

                # On prend la première fourmi disponible
                ant = available_ants.pop(0)
                task.start(ant.id)
                ant.add_task(task)
