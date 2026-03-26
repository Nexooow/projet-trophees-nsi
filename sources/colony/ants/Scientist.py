import typing

from colony.Ant import Ant
from colony.TaskManager import Task


class Scientist(Ant):
    def __init__(self, colony, data: dict, pos):
        super().__init__(colony, "scientist", data, pos)
        self.in_laboratory: bool = False
        self.goto_lab()

    def goto_lab(self):
        """
        Se rend au laboratoire.
        """
        lab_pos = self.colony.get_room_entry("laboratory")
        if lab_pos is not None:
            self.move_to(*lab_pos)

    def update(self):
        super().update()
        if self.in_laboratory is not True:
            in_room = self.colony.in_room(self.pos, "laboratory")
            if not in_room and self.target_pos is None:
                self.goto_lab()
            elif in_room:
                self.in_laboratory = True

    def serialize(self):
        data = super().serialize()
        data["in_laboratory"] = self.in_laboratory
        return data

    def restore(self, data):
        super().restore(data)
        self.in_laboratory = data.get("in_laboratory", False)
