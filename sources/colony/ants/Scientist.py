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
        print("BOUGE")
        lab_pos = self.colony.get_room_entry("laboratory")
        print(lab_pos, self.colony.get_room("laboratory"))
        if lab_pos is not None:
            print("BOUGE POUR DE VRAI TR")
            self.move_to(*lab_pos)
             
        
    def update (self):
        super().update()
        print("appelé")
        if self.in_laboratory is not True:
            print("a")
            in_room = self.colony.in_room(self.pos, "laboratory")
            if not in_room and self.target_pos is None:
                print("b")
                self.goto_lab()
            elif in_room:
                print("c")
                self.in_laboratory = True


