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
        on_fail=None,
    ):
        self.manager = manager
        self.id = uuid.uuid4()
        self.type = type
        self.data = data
        self.assigned_to: typing.Optional[uuid.UUID] = None
        self.priority = (
            data["priority"]
            if data and "priority" in data
            else TASK_DEFAULT_PRIORITY.get(type, 1)
        )
        self.deadline = (
            self.manager.colony.game.time.get_time(data["deadline"])
            if data and "deadline" in data
            else None
        )
        self.on_start = on_start
        self.on_complete = on_complete
        self.on_expired = on_expired
        self.on_fail = on_fail

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
            self.on_complete(self.data)

    def expire(self):
        if self.on_expired:
            self.on_expired()

    def fail(self):
        if self.on_fail:
            self.on_fail(self.data)


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
        if task_id not in self.tasks:
            return None
        return self.tasks[task_id]

    def add_task(
        self,
        type,
        data=None,
        on_start=None,
        on_complete=None,
        on_expired=None,
        on_fail=None,
    ):
        task = Task(
            self,
            type=type,
            data=data,
            on_start=on_start,
            on_complete=on_complete,
            on_expired=on_expired,
            on_fail=on_fail,
        )
        ant_type = TASK_ANT_TYPE.get(type, "worker")
        self.tasks[task.id] = task
        self.files[ant_type].enfiler(task.id, task.priority)

    def delete_task(self, task_id: uuid.UUID):
        if task_id in self.tasks:
            task_data = self.tasks[task_id]
            # On retire la tâche de la file si elle y est encore
            file = self.files[TASK_ANT_TYPE.get(task_data.type, "worker")]
            for i, (tid, _) in enumerate(file.content):
                if tid == task_id:
                    file.content.pop(i)
                    break
            del self.tasks[task_id]

    def complete_task(self, task_id: uuid.UUID):
        self.tasks[task_id].complete()

    def fail_task(self, task_id: uuid.UUID):
        if task_id in self.tasks:
            self.tasks[task_id].fail()

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
            available_ants = self.find_available_ants(ant_type)
            if not available_ants:
                continue

            # On distribue les tâches en attente aux fourmis disponibles
            while not file.est_vide() and available_ants:
                task_id = file.sommet()
                if task_id not in self.tasks:
                    file.defiler()
                    continue

                task = self.tasks[task_id]

                if task.is_assigned() or task.is_expired():
                    file.defiler()
                    continue

                target_pos = None
                if task.data:
                    if task.type == "dig":
                        target_pos = task.data.get("dig_pos")
                    elif task.type == "build_room":
                        target_pos = task.data.get("pos")
                    elif task.type in ["bring_food_queen", "deliver_larva"]:
                        target_pos = task.data.get("pickup_pos")

                best_ant_idx = 0
                if target_pos:
                    min_dist = float("inf")
                    for i, ant in enumerate(available_ants):
                        dist = distance(ant.pos, target_pos)
                        if dist < min_dist:
                            min_dist = dist
                            best_ant_idx = i

                ant = available_ants.pop(best_ant_idx)
                file.defiler()

                task.start(ant.id)
                ant.add_task(task)

    def serialize(self) -> dict:
        """
        Sérialise le TaskManager : tâches et files.
        """
        tasks_out = {}
        for tid, task in self.tasks.items():
            tasks_out[str(tid)] = {
                "type": task.type,
                "data": task.data,
                "assigned_to": str(task.assigned_to) if task.assigned_to else None,
                "priority": task.priority,
                "deadline": task.deadline,
            }

        files_out = {}
        for ant_type, file in self.files.items():
            files_out[ant_type] = [str(item) for (item, _) in file.content]

        return {"tasks": tasks_out, "files": files_out}

    def restore(self, data: dict):
        """
        Restaure les tâches et les files.
        """
        self.tasks.clear()
        for key in self.files:
            self.files[key].content = []

        tasks_data = data.get("tasks", {})
        for tid_str, tdata in tasks_data.items():
            try:
                task_id = uuid.UUID(tid_str)
                task = Task(
                    self,
                    type=tdata["type"],
                    data=tdata["data"],
                )
                task.id = task_id
                task.priority = tdata.get("priority", task.priority)
                task.deadline = tdata.get("deadline", task.deadline)

                assigned_to_str = tdata.get("assigned_to")
                if assigned_to_str:
                    task.assigned_to = uuid.UUID(assigned_to_str)

                self.tasks[task_id] = task
            except Exception:
                continue

        files_data = data.get("files", {})
        for ant_type, items in files_data.items():
            if ant_type in self.files:
                for tid_str in items:
                    try:
                        tid = uuid.UUID(tid_str)
                        if tid in self.tasks:
                            task = self.tasks[tid]
                            self.files[ant_type].enfiler(tid, task.priority)
                    except Exception:
                        pass
