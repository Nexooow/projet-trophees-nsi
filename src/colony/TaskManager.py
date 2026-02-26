from multiprocessing import RLock
import typing
import uuid
import datetime

from lib.file import File
from constants import TASK_ANT_TYPE, TASK_DEFAULT_PRIORITY

class Task:
    
    def __init__ (
        self,
        manager: "TaskManager",
        type: str,
        data: typing.Optional[dict] = None,
        on_start = None,
        on_complete = None,
        on_expired = None
    ):
        self.manager = manager
        self.id = uuid.uuid4()
        self.type = type
        self.data = data
        self.assigned_to: typing.Optional[uuid.UUID] = None
        self.priority = data["priority"] if data and "priority" in data else TASK_DEFAULT_PRIORITY[type]
        self.deadline = data["deadline"] if data and "deadline" in data else None
        self.on_start = on_start
        self.on_complete = on_complete
        self.on_expired = on_expired
        
    def is_assigned (self):
        return self.assigned_to is not None
        
    def start (self, assigned_to: uuid.UUID):
        self.assigned_to = assigned_to
        if self.on_start:
            self.on_start()
        
    def complete (self):
        if self.on_complete:
            self.on_complete()
            
    def expire (self):
        if self.on_expired:
            self.on_expired()

class TaskManager: 
    
    def __init__ (self, colony):
        self.colony = colony
        self.tasks: dict[uuid.UUID, Task] = {}
        self.files: dict[str, File] = {
            "worker": File(),
            "warrior": File(),
            "nurse": File(),
            "scientist": File(),
            "explorer": File()
        }
        
    def add_task (self, type, data = None, on_start = None, on_complete = None, on_expired = None):
        task = Task(
            self,
            type=type,
            data=data,
            on_start=on_start,
            on_complete=on_complete,
            on_expired=on_expired
        )
        ant_type = TASK_ANT_TYPE[type]
        self.tasks[task.id] = task
        self.files[ant_type].enfiler(task.id)
        
    def delete_task (self, task_id: uuid.UUID):
        if task_id in self.tasks:
            task_data = self.tasks[task_id]
            self.files[TASK_ANT_TYPE[task_data.type]].content.remove((task_id, task_data.priority))
            del self.tasks[task_id]
            
    def complete_task (self, task_id: uuid.UUID):
        self.tasks[task_id].complete()
        
    def find_available_ants (self, type: str):
        ants = []
        for ant in self.colony.ants:
            if ant.type == type and ant.is_available():
                ants.append(ant)
        return ants
        
    def update (self):
        for task in self.tasks.values():
            if task.deadline and task.deadline < datetime.datetime.now():
                task.expire()
        for file_name, file in self.files.items():
            available_ants = self.find_available_ants(file_name)
            for ant in available_ants:
                task_id = file.defiler()
                ant.start_task(task_id)
                