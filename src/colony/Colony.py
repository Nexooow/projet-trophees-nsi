from Ant import Ant
class Colony:
    def __init__(self):
        self.ants=[]
        self.food=0
        self.materials=0
        self.population=0
        self.rooms=[]
    def get_room(self,name):
        for room in self.rooms:
            if room.name==name:
                return room
        return None
class Worker(Ant):
    def __init__(self,xp,level,pos_x,pos_y,power=1):
        super().__init__("worker",power,xp,level,pos_x,pos_y)
        self.digger=True
    def create_room(self,room):
        self.colony.rooms+=[]
class Soldier(Ant):
    def __init__(self,xp,level,pos_x,pos_y,power=1):
        super().__init__("soldier",power,xp,level,pos_x,pos_y)
        
class Scientist(Ant):
    def __init__(self,xp,level,pos_x,pos_y,power=1):
        super().__init__("scientist",power,xp,level,pos_x,pos_y)
        self.points_min=1.0
class Explorer(Ant):
    def __init__(self,xp,level,pos_x,pos_y,power=1):
        super().__init__("explorer",power,xp,level,pos_x,pos_y)
class Nurse(Ant):
    def __init__(self,xp,level,pos_x,pos_y,power=1):
        super().__init__("worker",power,xp,level,pos_x,pos_y)