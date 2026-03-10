import typing

from colony.Ant import Ant
from colony.TaskManager import Task

# Phases de la tâche deliver_larva
_PHASE_GO_PICKUP = "go_pickup"
_PHASE_GO_DELIVER = "go_deliver"
_PHASE_DONE = "done"


class Worker(Ant):
    def __init__(self, colony, data: dict, pos):
        super().__init__(colony, "worker", data, pos)

        # État interne pour deliver_larva
        self.delivery_phase: typing.Optional[str] = None
        self.delivery_ant_type: typing.Optional[str] = None
        self.delivery_pos: typing.Optional[typing.Tuple[int, int]] = None

    def execute_task(self, task: "Task"):
        """Aiguille vers le bon handler selon le type de tâche."""
        if task.type == "deliver_larva":
            self.start_deliver_larva(task)
        # TODO: ajouter d'autres tâches ici

    def start_deliver_larva(self, task: "Task"):
        """
        Démarre la tâche : mémorise les infos de livraison puis envoie
        l'ouvrière chercher la larve auprès de la reine.
        """
        data = task.data or {}
        self.delivery_ant_type = data.get("ant_type")
        pickup_pos = data.get("pickup_pos")
        deliver_pos = data.get("delivery_pos")

        if pickup_pos is None or deliver_pos is None or self.delivery_ant_type is None:
            self.finish_task()
            return

        self.delivery_pos = deliver_pos
        self.delivery_phase = _PHASE_GO_PICKUP

        pickup_cell = self.colony.grid.pixel_to_cell(
            int(pickup_pos[0]), int(pickup_pos[1]) - self.colony.grid.start_y
        )
        
        self.move_to(pickup_cell[0], pickup_cell[1])

    def update(self):
        """Met à jour le mouvement et gère les transitions de phase."""
        super().update()
        self.update_delivery()

    def update_delivery(self):
        """Vérifie si l'ouvrière a atteint sa destination et fait avancer la phase."""
        if self.delivery_phase is None:
            return

        # On attend que la fourmi soit immobile (chemin entièrement parcouru)
        if not self.is_static():
            return

        if self.delivery_phase == _PHASE_GO_PICKUP:
            # Arrivée à la salle de la reine → se diriger vers la nurserie
            self.delivery_phase = _PHASE_GO_DELIVER
            assert self.delivery_pos is not None
            delivery_cell = self.colony.grid.pixel_to_cell(
                int(self.delivery_pos[0]),
                int(self.delivery_pos[1]) - self.colony.grid.start_y,
            )
            self.move_to(delivery_cell[0], delivery_cell[1])

        elif self.delivery_phase == _PHASE_GO_DELIVER:
            # Arrivée à la nurserie
            self.delivery_phase = _PHASE_DONE
            self.hatch_larva()
            self.finish_task()

    def hatch_larva(self):
        """Instancie la fourmi issue de la larve livrée et l'ajoute à la colonie."""
        from colony.ants.Worker import Worker as WorkerAnt

        _ANT_CLASS_MAP: dict = {
            "worker": WorkerAnt,
            # Les autres types pourront être ajoutés ici
        }

        ant_type = self.delivery_ant_type or "worker"
        ant_class = _ANT_CLASS_MAP.get(ant_type, WorkerAnt)

        # TODO: gérer la naissance via la nursery
        pos = (int(self.pos.x), int(self.pos.y))
        ant = ant_class(self.colony, {"power": 1, "xp": 0}, pos)
        self.colony.ants.append(ant)

    def finish_task(self):
        """Réinitialise l'état interne et libère la fourmi."""
        if self.current_task_id is not None:
            self.colony.tasks.complete_task(self.current_task_id)
            del self.colony.tasks.tasks[self.current_task_id]
            self.current_task_id = None

        self.delivery_phase = None
        self.delivery_ant_type = None
        self.delivery_pos = None
