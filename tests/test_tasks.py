import uuid
from unittest.mock import MagicMock

import pytest

from sources.colony.TaskManager import Task, TaskManager
from sources.lib.file import File


class TestTasks:
    @pytest.fixture
    def mock_colony(self):
        colony = MagicMock()
        colony.game.time.get_time.return_value = 1000
        return colony

    def test_task_initialization(self, mock_colony):
        manager = TaskManager(mock_colony)
        task_type = "build"
        data = {"priority": 5}

        task = Task(manager, task_type, data)

        assert task.type == task_type
        assert task.priority == 5
        assert task.assigned_to is None
        assert isinstance(task.id, uuid.UUID)

    def test_task_lifecycle_callbacks(self, mock_colony):
        manager = TaskManager(mock_colony)
        on_start = MagicMock()
        on_complete = MagicMock()

        task = Task(manager, "test", on_start=on_start, on_complete=on_complete)
        ant_id = uuid.uuid4()

        task.start(ant_id)
        assert task.assigned_to == ant_id
        on_start.assert_called_once()

        task.complete()
        on_complete.assert_called_once()

    def test_task_expiration(self, mock_colony):
        manager = TaskManager(mock_colony)

        # La deadline est calculée à l'initialisation de Task:
        # self.deadline = self.manager.colony.game.time.get_time(data["deadline"])
        # On simule que l'appel renvoie 100 (la deadline absolue en minutes)
        mock_colony.game.time.get_time.return_value = 100
        task = Task(manager, "test", data={"deadline": 50})

        # Ensuite, is_expired() appelle self.manager.colony.game.time.get_time() (sans argument)
        # On simule un temps actuel de 120, ce qui est après la deadline de 100.
        mock_colony.game.time.get_time.return_value = 120
        assert task.is_expired() is True

        # On simule un temps actuel de 80, ce qui est avant la deadline de 100.
        mock_colony.game.time.get_time.return_value = 80
        assert task.is_expired() is False

    def test_task_manager_add_and_delete(self, mock_colony):
        tm = TaskManager(mock_colony)

        # On utilise une constante simulée car TASK_ANT_TYPE n'est pas importé ici
        # mais TaskManager l'utilise. On assume que 'build' mappe vers 'worker' par défaut.
        tm.add_task("build", data={"priority": 10})

        assert len(tm.tasks) == 1
        task_id = list(tm.tasks.keys())[0]

        tm.delete_task(task_id)
        assert len(tm.tasks) == 0
        assert tm.files["worker"].est_vide()

    def test_task_assignment_flow(self, mock_colony):
        tm = TaskManager(mock_colony)

        # Mock une fourmi
        ant = MagicMock()
        ant.id = uuid.uuid4()
        ant.type = "worker"
        ant.is_available.return_value = True

        mock_colony.ants = [ant]

        # Ajouter une tâche
        tm.add_task("build")
        task_id = list(tm.tasks.keys())[0]
        task = tm.tasks[task_id]

        # Update pour assigner la tâche
        tm.update()

        assert task.is_assigned()
        assert task.assigned_to == ant.id
        ant.add_task.assert_called_once_with(task)
        assert tm.files["worker"].est_vide()
