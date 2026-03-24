import typing

from colony.Ant import Ant
from colony.ants.Nurse import Nurse
from colony.TaskManager import Task
from constants import COLONY_BRUSH_SIZE

# Phases de la tâche deliver_larva
_PHASE_GO_PICKUP = "go_pickup"
_PHASE_GO = "go"
_PHASE_GO_DELIVER = "go_deliver"
_PHASE_DIG = "dig"
_PHASE_DONE = "done"


class Worker(Ant):
    def __init__(self, colony, data: dict, pos):
        super().__init__(colony, "worker", data, pos)

        self.task_phase: typing.Optional[str] = None
        self.task_data: typing.Optional[str] = None
        self.task_pos: typing.Optional[typing.Tuple[int, int]] = None

        self.moving: bool = False

    def execute_task(self, task: "Task"):
        """Aiguille vers le bon handler selon le type de tâche."""
        if task.type == "deliver_larva":
            self.start_deliver_larva(task)
            print("début livraison")
        elif task.type == "bring_food_queen":
            self.start_feed_queen(task)
        elif task.type == "dig":
            self.start_dig(task)
        elif task.type == "build_room":
            self.start_build_room(task)

    def start_dig(self, task: "Task"):
        data = task.data or {}
        dig_pos = data.get("dig_pos")

        if dig_pos is None:
            self.finish_task()
            return

        self.task_pos = dig_pos
        self.task_phase = _PHASE_GO

        center_x = dig_pos[0] + COLONY_BRUSH_SIZE / 2
        center_y = dig_pos[1] + COLONY_BRUSH_SIZE / 2

        target_cell = self.colony.grid.pixel_to_cell(
            int(center_x), int(center_y) - self.colony.grid.start_y
        )

        # Pour creuser, on peut se déplacer sur la case cible si elle est accessible
        # Sinon, on cherche une case adjacente accessible
        if self.colony.grid.is_cell_passable(*target_cell):
            dest_cell = target_cell
        else:
            neighbors = self.colony.grid.get_neighbors(*target_cell)
            if not neighbors:
                self.finish_task()
                return
            # premier voisin le plus accessible
            dest_cell = neighbors[0]

        self.moving = True
        if not self.move_to(*dest_cell):
            self.finish_task()

    def start_build_room(self, task: "Task"):
        data = task.data or {}
        build_pos = data.get("pos")

        if build_pos is None:
            self.finish_task()
            return

        self.task_pos = build_pos
        self.task_phase = _PHASE_GO

        center_x = build_pos[0] + COLONY_BRUSH_SIZE / 2
        center_y = build_pos[1] + COLONY_BRUSH_SIZE / 2

        target_cell = self.colony.grid.pixel_to_cell(
            int(center_x), int(center_y) - self.colony.grid.start_y
        )

        # Pour construire, on peut se déplacer sur la case cible si elle est accessible
        # Sinon, on cherche une case adjacente accessible
        if self.colony.grid.is_cell_passable(*target_cell):
            dest_cell = target_cell
        else:
            neighbors = self.colony.grid.get_neighbors(*target_cell)
            if not neighbors:
                self.finish_task()
                return
            # premier voisin le plus accessible
            dest_cell = neighbors[0]

        self.moving = True
        if not self.move_to(*dest_cell):
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

        # Si la case cible n'est pas passable, chercher un voisin accessible
        if not self.colony.grid.is_cell_passable(*pickup_cell):
            neighbors = self.colony.grid.get_neighbors(*pickup_cell)
            if neighbors:
                dest_cell = neighbors[0]
            else:
                # Aucune destination possible -> annuler la tâche
                self.finish_task()
                return
        else:
            dest_cell = pickup_cell

        self.moving = True
        if not self.move_to(dest_cell[0], dest_cell[1]):
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

        # Si la cellule de prise n'est pas passable, chercher un voisin praticable
        if not self.colony.grid.is_cell_passable(*pickup_cell):
            neighbors = self.colony.grid.get_neighbors(*pickup_cell)
            if neighbors:
                dest_cell = neighbors[0]
            else:
                self.finish_task()
                return
        else:
            dest_cell = pickup_cell

        self.moving = True
        if not self.move_to(dest_cell[0], dest_cell[1]):
            self.finish_task()

    def update(self):
        """Met à jour le mouvement et gère les transitions de phase."""
        super().update()
        self.update_task()

    def update_task(self):
        """Vérifie si l'ouvrière a atteint sa destination et fait avancer la phase."""
        if self.task_phase is None:
            return

        if self.moving:
            if self.is_static():
                self.moving = False
            else:
                return

        # On attend que la fourmi soit immobile (chemin entièrement parcouru)
        if not self.is_static():
            return

        current_task = self.get_current_task()
        assert current_task is not None

        if self.task_phase == _PHASE_GO_PICKUP:
            if current_task.type == "bring_food_queen":
                if self.colony.food < 100:
                    return
                self.colony.food -= 100

            self.task_phase = _PHASE_GO_DELIVER
            assert self.task_pos is not None
            delivery_cell = self.colony.grid.pixel_to_cell(
                int(self.task_pos[0]),
                int(self.task_pos[1]) - self.colony.grid.start_y,
            )

            # Si la cellule de livraison est bloquée, choisir un voisin praticable
            if not self.colony.grid.is_cell_passable(*delivery_cell):
                neighbors = self.colony.grid.get_neighbors(*delivery_cell)
                if neighbors:
                    dest_cell = neighbors[0]
                else:
                    self.finish_task()
                    return
            else:
                dest_cell = delivery_cell

            self.moving = True

            if not self.move_to(dest_cell[0], dest_cell[1]):
                self.finish_task()
                return

        elif self.task_phase == _PHASE_GO_DELIVER:
            self.task_phase = _PHASE_DONE

            if current_task.type == "bring_food_queen":
                pass  # La nourriture est considérée livrée à l'arrivée
            elif current_task.type == "deliver_larva":
                nursery = self.colony.get_room("nursery")
                if nursery is not None and self.task_data is not None:
                    nursery.assign_larvae(self.task_data)

            self.finish_task()

        elif self.task_phase == _PHASE_GO:
            self.task_phase = _PHASE_DIG

            if current_task.type == "dig" and self.task_pos:
                self.colony.grid.supprimer_cellules(
                    self.task_pos[0],
                    self.task_pos[1],
                    COLONY_BRUSH_SIZE,
                )
                self.finish_task()
            elif current_task.type == "build_room" and self.task_pos:
                self.colony.grid.build_room(
                    self.task_pos[0],
                    self.task_pos[1],
                    COLONY_BRUSH_SIZE,
                    COLONY_BRUSH_SIZE,
                )
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
