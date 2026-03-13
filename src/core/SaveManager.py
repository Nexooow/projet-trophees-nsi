from __future__ import annotations

import json
import os
import time
import typing
import uuid

from constants import SAVES_PATH

CURRENT_SAVE_VERSION = 1

CELL_STATES = {
    "empty": 0,
    "full_v1": 1,
    "full_v2": 2,
    "full_v3": 3,
    "full_v4": 4,
    "occupied": 10,
    "occupied_walkable": 11,
}


class SaveManager:
    """
    Gestionnaire des sauvegardes.
    """

    def __init__(self, game):
        self.game = game
        os.makedirs(SAVES_PATH, exist_ok=True)

    def save_path(self, save_id: str) -> str:
        return os.path.join(SAVES_PATH, f"{save_id}.json")

    def list_saves(self) -> list:
        """
        Retourne la liste des sauvegardes disponibles
        """
        saves = []
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
        colony_data: dict = {"food": colony.food}

        colony_data["inventory"] = colony.inventory
        colony_data["grid"] = self.serialize_grid(colony)
        colony_data["rooms"] = self.serialize_rooms(colony)
        colony_data["ants"] = self.serialize_ants(colony)

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
        }

    def get_colony(self):
        """Retourne l'état ColonyState actuel."""
        return self.game.state.states_managers["colony"]

    def serialize_grid(self, colony) -> list:
        """
        Sérialise la grille
        """
        grid = colony.grid
        rows = []
        for y in range(grid.height):
            row = []
            for x in range(grid.width):
                cell = grid.grid[y][x]
                state = cell["state"]
                variant = cell.get("variant", 0)
                bitmap = cell.get("bitmap")
                if state == "full" and variant == 0:
                    row.append(CELL_STATES["full_v1"])
                elif state == "full":
                    row.append(CELL_STATES[f"full_v{variant}"])
                elif state == "empty":
                    row.append(CELL_STATES["empty"])
                elif state == "occupied":
                    row.append(CELL_STATES["occupied"])
                elif state == "occupied_walkable":
                    row.append(CELL_STATES["occupied_wallkable"])
                elif state == "partial" and bitmap is not None:
                    # Compresser le bitmap en liste d'entiers (1 entier = 1 ligne de 8 bits)
                    compressed = [
                        int("".join("1" if px else "0" for px in row_bmp), 2)
                        for row_bmp in bitmap
                    ]
                    row.append([compressed, variant])
                else:
                    row.append(None)
            rows.append(row)
        return rows

    def serialize_rooms(self, colony) -> dict:
        """
        Sérialise les données des salles de la colonie.
        """
        rooms_data: dict = {}
        for room in colony.rooms:
            if room.name == "queen":
                rooms_data["queen"] = self.serialize_queen(room)
        return rooms_data

    def serialize_queen(self, queen) -> dict:
        """
        Sérialise les données de la reine.
        """
        # File de larves : liste des types en attente
        born_queue_list = [item for (item, _) in queen.born_queue.content]

        # Séparation améliorations avec niveaux / sans niveaux (débloquées)
        upgrade_levels = {}
        unlocked_upgrades = []
        for upg_id, level in queen.upgrade_levels.items():
            if level > 0:
                from constants import QUEEN_UPGRADES

                upg_data = QUEEN_UPGRADES.get(upg_id, {})
                if upg_data.get("levels"):
                    upgrade_levels[upg_id] = level
                else:
                    unlocked_upgrades.append(upg_id)

        return {
            "hp": queen.hp,
            "upgrade_levels": upgrade_levels,
            "unlocked_upgrades": unlocked_upgrades,
            "max_larvae": queen.max_larvae,
            "born_queue": born_queue_list,
            "larvae_timer": queen.larvae_timer,
        }

    def serialize_ants(self, colony) -> list:
        """
        Sérialise la liste des fourmis de la colonie.
        """
        ants_list = []
        for ant in colony.ants:
            ants_list.append(
                {
                    "type": ant.type,
                    "data": {"power": ant.power, "xp": ant.xp},
                    "pos": [ant.pos.x, ant.pos.y],
                }
            )
        return ants_list

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

        assert save_id is not None
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
        colony.inventory = colony_data.get("inventory", {})

        grid_data = colony_data.get("grid")
        if grid_data:
            self.restore_grid(colony, grid_data)

        rooms_data = colony_data.get("rooms", {})
        self.restore_rooms(colony, rooms_data)

        # Fourmis
        ants_data = colony_data.get("ants", [])
        self.restore_ants(colony, ants_data)

        # Re-render toute la grille
        for y in range(colony.grid.height):
            for x in range(colony.grid.width):
                colony.grid.dirty_cells.add((x, y))

    def restore_grid(self, colony, rows: list):
        """
        Restaure la grille à partir de la sauvegarde.
        """
        grid = colony.grid
        grid.cached_paths = {}

        INT_TO_STATE: dict = {}
        for key, code in CELL_STATES.items():
            if key.startswith("full_v"):
                variant = int(key[len("full_v") :])
                INT_TO_STATE[code] = ("full", variant)
            elif key == "empty":
                INT_TO_STATE[code] = ("empty", 0)
            elif key == "occupied":
                INT_TO_STATE[code] = ("occupied", 0)
            elif key == "occupied_wallkable":  # conserve la coquille du dict source
                INT_TO_STATE[code] = ("occupied_walkable", 0)

        for y, row in enumerate(rows):
            if y >= grid.height:
                break
            for x, cell_data in enumerate(row):
                if x >= grid.width:
                    break
                if isinstance(cell_data, int):
                    # État simple encodé comme un entier
                    state, variant = INT_TO_STATE.get(cell_data, ("full", 0))
                    bitmap = None
                elif isinstance(cell_data, list):
                    # Cellule partielle : [compressed_bitmap, variant]
                    compressed, variant = cell_data[0], cell_data[1]
                    state = "partial"
                    bitmap = []
                    for row_int in compressed:
                        brow = []
                        for bit in range(7, -1, -1):
                            brow.append(bool((row_int >> bit) & 1))
                        bitmap.append(brow)
                else:
                    state, variant, bitmap = "full", 0, None

                grid.grid[y][x]["state"] = state
                grid.grid[y][x]["bitmap"] = bitmap
                grid.grid[y][x]["variant"] = variant
                grid.dirty_cells.add((x, y))

    def restore_rooms(self, colony, rooms_data: dict):
        for room in colony.rooms:
            if room.name == "queen" and "queen" in rooms_data:
                self.restore_queen(room, rooms_data["queen"])

    def restore_queen(self, queen, data: dict):
        from constants import QUEEN_MAX_LARVAE, QUEEN_UPGRADES
        from lib.file import File

        queen.hp = data.get("hp", queen.max_hp)
        queen.max_larvae = data.get("max_larvae", QUEEN_MAX_LARVAE)
        queen.larvae_timer = data.get("larvae_timer", 0)

        # Reconstruire upgrade_levels
        upgrade_levels = {k: 0 for k in QUEEN_UPGRADES}
        for upg_id, lvl in data.get("upgrade_levels", {}).items():
            if upg_id in upgrade_levels:
                upgrade_levels[upg_id] = lvl
        for upg_id in data.get("unlocked_upgrades", []):
            if upg_id in upgrade_levels:
                upgrade_levels[upg_id] = 1  # débloquée = niveau 1
        queen.upgrade_levels = upgrade_levels

        # Reconstruire la file de larves
        queen.born_queue = File()
        for ant_type in data.get("born_queue", []):
            queen.born_queue.enfiler(ant_type)

    def restore_ants(self, colony, ants_data: list):
        from colony.ants.Nurse import Nurse
        from colony.ants.Worker import Worker

        _ANT_CLASS_MAP = {
            "worker": Worker,
            "nurse": Nurse,
        }

        colony.ants.clear()
        for ant_data in ants_data:
            ant_type = ant_data.get("type", "worker")
            ant_class = _ANT_CLASS_MAP.get(ant_type, Worker)
            pos = tuple(ant_data.get("pos", [0, 0]))
            ant = ant_class(colony, ant_data.get("data", {"power": 1, "xp": 0}), pos)
            colony.ants.append(ant)
