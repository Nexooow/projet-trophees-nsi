import typing

from colony.Ant import Ant
from colony.ants.Nurse import Nurse
from colony.TaskManager import Task

# Phases de la tâche deliver_larva
_PHASE_GO_PICKUP = "go_pickup"
_PHASE_GO = "go"
_PHASE_GO_DELIVER = "go_deliver"
_PHASE_DONE = "done"


class Worker(Ant):
    def __init__(self, colony, data: dict, pos):
        super().__init__(colony, "worker", data, pos)

        # État interne pour deliver_larva
        self.task_phase: typing.Optional[str] = None
        self.task_data: typing.Optional[str] = None
        self.task_pos: typing.Optional[typing.Tuple[int, int]] = None
        # True dès qu'un move_to a été lancé et que la fourmi n'est pas encore arrivée
        self.moving: bool = False

    def execute_task(self, task: "Task"):
        """Aiguille vers le bon handler selon le type de tâche."""
        if task.type == "deliver_larva":
            self.start_deliver_larva(task)
            print("début livraison")
        elif task.type == "bring_food_queen":
            self.start_feed_queen(task)
        elif task.type == "dig":
            pass

    def start_dig (self, task: "Task"):
        data = task.data or {}
        dig_pos = data.get("dig_pos")

        if dig_pos is None:
            self.finish_task()
            return
        
        self.task_pos = dig_pos
        self.task_phase = _PHASE_GO

        target_cell = self.colony.grid.pixel_to_cell(
            int(dig_pos[0]), int(dig_pos[1]) - self.colony.grid.start_y
        )

        self.moving = True
        if not self.move_to(*target_cell):
            self.finish_task()
            
        
        

    def start_feed_queen(self, task: "Task"):
        data = task.data or {}
        pickup_pos = data.get("pickup_pos")
        deliver_pos = data.get("delivery_pos")

        if pickup_pos is None or deliver_pos is None:
            self.finish_task()
            print("annulée")
            return

        self.task_pos = deliver_pos
        self.task_phase = _PHASE_GO_PICKUP

        pickup_cell = self.colony.grid.pixel_to_cell(
            int(pickup_pos[0]), int(pickup_pos[1]) - self.colony.grid.start_y
        )

        self.moving = True
        if not self.move_to(pickup_cell[0], pickup_cell[1]):
            self.finish_task()

    def start_deliver_larva(self, task: "Task"):
        """
        Démarre la tâche : mémorise les infos de livraison puis envoie
        l'ouvrière chercher la larve auprès de la reine.
        """
        data = task.data or {}
        self.task_data = data.get("ant_type")
        pickup_pos = data.get("pickup_pos")
        deliver_pos = data.get("delivery_pos")

        if pickup_pos is None or deliver_pos is None or self.task_data is None:
            self.finish_task()
            print("annulée")
            return

        self.task_pos = deliver_pos
        self.task_phase = _PHASE_GO_PICKUP

        pickup_cell = self.colony.grid.pixel_to_cell(
            int(pickup_pos[0]), int(pickup_pos[1]) - self.colony.grid.start_y
        )

        self.moving = True
        if not self.move_to(pickup_cell[0], pickup_cell[1]):
            self.finish_task()

    def update(self):
        """Met à jour le mouvement et gère les transitions de phase."""
        super().update()
        self.update_delivery()

    def update_delivery(self):
        """Vérifie si l'ouvrière a atteint sa destination et fait avancer la phase."""
        if self.task_phase is None:
            return

        if self.moving:
            if self.is_static():
                self.moving = False
            else:
                # La fourmi est toujours en mouvement
                return

        # On attend que la fourmi soit immobile (chemin entièrement parcouru)
        if not self.is_static():
            return

        current_task = self.get_current_task()
        assert current_task is not None

        if self.task_phase == _PHASE_GO_PICKUP:
            self.task_phase = _PHASE_GO_DELIVER
            assert self.task_pos is not None
            delivery_cell = self.colony.grid.pixel_to_cell(
                int(self.task_pos[0]),
                int(self.task_pos[1]) - self.colony.grid.start_y,
            )
            self.moving = True

            if current_task.type == "bring_food_queen":
                self.colony.food -= 200

            if not self.move_to(delivery_cell[0], delivery_cell[1]):
                self.finish_task()
                return

        elif self.task_phase == _PHASE_GO_DELIVER:
            self.task_phase = _PHASE_DONE

            if current_task.type == "bring_food_queen":
                pass  # La nourriture est considérée livrée à l'arrivée
            elif current_task.type == "deliver_larva":
                pass # TODO: faire apparaitre la nouvelle fourmi

            self.finish_task()

    def finish_task(self):
        """Réinitialise l'état interne et libère la fourmi."""
        if self.current_task_id is not None:
            self.colony.tasks.complete_task(self.current_task_id)
            del self.colony.tasks.tasks[self.current_task_id]
            self.current_task_id = None

        self.task_phase = None
        self.task_data = None
        self.task_pos = None
        self.moving = False
