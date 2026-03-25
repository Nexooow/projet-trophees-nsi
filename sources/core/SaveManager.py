from __future__ import annotations

import json
import os
import time
import typing
import uuid

from colony.ants.Nurse import Nurse
from colony.ants.Scientist import Scientist
from colony.ants.Worker import Worker
from constants import CURRENT_SAVE_VERSION, SAVES_PATH
from exploration.ExpeditionMap import ExpeditionMap

if typing.TYPE_CHECKING:
    from core.GameManager import GameManager


class SaveManager:
    """
    Gestionnaire de sauvegarde et de chargement.
    """

    def __init__(self, game_manager: "GameManager"):
        self.game = game_manager
        if not os.path.exists(SAVES_PATH):
            os.makedirs(SAVES_PATH)

    def save_path(self, save_id: str) -> str:
        return os.path.join(SAVES_PATH, f"{save_id}.json")

    def list_saves(self) -> list:
        """
        Retourne la liste des sauvegardes disponibles
        """
        saves = []
        if not os.path.exists(SAVES_PATH):
            return []

        for file_name in os.listdir(SAVES_PATH):
            if not file_name.endswith(".json"):
                continue
            path = os.path.join(SAVES_PATH, file_name)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                meta = data.get("meta", {})
                saves.append(
                    {
                        "save_id": meta.get("save_id", file_name[:-5]),
                        "timestamp": meta.get("timestamp", 0.0),
                        "day": meta.get("day", 1),
                        "path": path,
                    }
                )
            except (json.JSONDecodeError, OSError):
                continue
        saves.sort(key=lambda s: s["timestamp"], reverse=True)
        return saves

    def has_save(self) -> bool:
        """Renvoie True s'il existe au moins une sauvegarde valide."""
        return len(self.list_saves()) > 0

    def latest_save(self) -> typing.Optional[dict]:
        """Retourne les métadonnées de la sauvegarde la plus récente, ou None."""
        saves = self.list_saves()
        return saves[0] if saves else None

    def sauvegarder(self, save_id: typing.Optional[str] = None) -> str:
        """
        Sérialise l'état complet du jeu dans un fichier JSON.
        Retourne le save_id utilisé.
        """
        if save_id is None:
            save_id = self.game.game_id or str(uuid.uuid4())

        self.game.game_id = save_id
        data = self.save_dict(save_id)
        path = self.save_path(save_id)

        # Écrire de manière atomique si possible (écriture simple ici)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)

        return save_id

    def save_dict(self, save_id: str) -> dict:
        """
        Retourne un dictionnaire contenant les données du jeu à sauvegarder.
        """
        game = self.game
        time_mgr = game.time

        colony = self.get_colony()
        colony_data: dict = {
            "food": colony.food,
            "science": colony.science,
            "food_capacity": colony.food_capacity,
            "camera_x": colony.camera_x,
            "camera_y": colony.camera_y,
            "pending_builds": colony.pending_builds,
        }

        colony_data["inventory"] = colony.inventory

        # Délégation aux sous-systèmes
        colony_data["grid"] = colony.grid.serialize()

        colony_data["rooms"] = {}
        for room in colony.rooms:
            # On suppose que toutes les salles ont une méthode serialize ou on gère le None
            if hasattr(room, "serialize"):
                colony_data["rooms"][room.name] = room.serialize()
            else:
                colony_data["rooms"][room.name] = None

        colony_data["ants"] = []
        for ant in colony.ants:
            colony_data["ants"].append(ant.serialize())

        colony_data["tasks"] = colony.tasks.serialize()

        # Expedition serialization
        expedition_data = None
        expedition_state = self.game.state.states_managers.get("expedition")
        if expedition_state and expedition_state.expedition_map:
            exp_map_data = expedition_state.expedition_map.serialize()
            if exp_map_data:
                # Ajout des données caméra qui sont dans l'état, pas dans la map
                exp_map_data["cam_x"] = expedition_state.cam_x
                exp_map_data["cam_y"] = expedition_state.cam_y
                expedition_data = exp_map_data

        return {
            "version": CURRENT_SAVE_VERSION,
            "meta": {
                "save_id": save_id,
                "timestamp": time.time(),
                "day": time_mgr.day,
            },
            "time": {
                "day": time_mgr.day,
                "time": time_mgr.time,
                "sub_frame_count": time_mgr.sub_frame_count,
            },
            "colony": colony_data,
            "expedition": expedition_data,
        }

    def get_colony(self):
        return self.game.state.states_managers["colony"]

    def restaurer(self, save_id: typing.Optional[str] = None) -> bool:
        """
        Charge une sauvegarde JSON et restaure l'état du jeu.
        Si save_id est None, charge la sauvegarde la plus récente.
        Retourne True si la restauration a réussi, False sinon.
        """
        if save_id is None:
            latest = self.latest_save()
            if latest is None:
                return False
            save_id = latest["save_id"]

        path = self.save_path(save_id)
        if not os.path.exists(path):
            return False

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            return False

        if data.get("version", 0) != CURRENT_SAVE_VERSION:
            # Migration si besoin dans le futur pour éviter problèmes de compatibilité
            pass

        self.game.game_id = save_id
        self.restore_from_dict(data)
        return True

    def restore_from_dict(self, data: dict):
        """
        Restaure l'état du jeu à partir d'un dictionnaire de données.
        """
        game = self.game

        time_data = data.get("time", {})
        game.time.day = time_data.get("day", 1)
        game.time.time = time_data.get("time", 60 * 12)
        game.time.sub_frame_count = time_data.get("sub_frame_count", 0)

        colony_data = data.get("colony", {})
        colony = self.get_colony()
        colony.food = colony_data.get("food", 0)
        colony.science = colony_data.get("science", 0)
        colony.food_capacity = colony_data.get("food_capacity", colony.food_capacity)
        colony.camera_x = colony_data.get("camera_x", colony.camera_x)
        colony.camera_y = colony_data.get("camera_y", colony.camera_y)
        colony.pending_builds = colony_data.get("pending_builds", [])
        colony.inventory = colony_data.get("inventory", {})

        # Grid
        grid_data = colony_data.get("grid")
        if grid_data:
            colony.grid.restore(grid_data)

        # Rooms
        rooms_data = colony_data.get("rooms", {})
        for room in colony.rooms:
            rdata = rooms_data.get(room.name)
            if rdata and hasattr(room, "restore"):
                room.restore(rdata)

        # Fourmis
        ants_data = colony_data.get("ants", [])
        colony.ants.clear()
        _ANT_CLASS_MAP = {"worker": Worker, "nurse": Nurse, "scientist": Scientist}

        for ant_data in ants_data:
            ant_type = ant_data.get("type", "worker")
            ant_class = _ANT_CLASS_MAP.get(ant_type, Worker)
            pos = tuple(ant_data.get("pos", [0, 0]))

            ant = ant_class(colony, ant_data.get("data", {"power": 1, "xp": 0}), pos)
            ant.restore_from_dict(ant_data)
            colony.ants.append(ant)

        # Tâches
        tasks_blob = colony_data.get("tasks")
        if tasks_blob:
            colony.tasks.restore(tasks_blob)

        # Expedition
        expedition_data = data.get("expedition")
        if expedition_data:
            expedition_state = self.game.state.states_managers.get("expedition")
            if expedition_state:
                if not expedition_state.expedition_map:
                    expedition_state.expedition_map = ExpeditionMap(
                        seed=expedition_data.get("seed")
                    )

                expedition_state.expedition_map.restore(expedition_data)

                # Restaurer la caméra
                expedition_state.cam_x = expedition_data.get(
                    "cam_x", getattr(expedition_state, "cam_x", 600)
                )
                expedition_state.cam_y = expedition_data.get(
                    "cam_y", getattr(expedition_state, "cam_y", 400)
                )

        # Re-render toute la grille (nécessaire après restore grid)
        for y in range(colony.grid.height):
            for x in range(colony.grid.width):
                colony.grid.dirty_cells.add((x, y))
