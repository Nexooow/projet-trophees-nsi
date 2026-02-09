import pygame
ROOMS={
    "name":[pygame.image.load("image_link"),pygame.image.load("being_built")]
}
class Room:
    def __init__(self, name, pos_x,pos_y):
        self.name = name
        self.ants = []
        self.pos_x=pos_x
        self.pos_y=pos_y
        self.being_built=False
        self.construction_time=3600
        self.building_time=0
    def add_ant(self, ant):
        self.ants.append(ant)
    def remove_ant(self, ant):
        if ant in self.ants:
            self.ants.remove(ant)
    def get_ants(self):
        return self.ants
    def update(self):
        if self.being_built:
            self.building_time+=1
    def draw(self, surface):
        if self.building_time>=self.construction_time:
            self.building_time=0
            self.being_built=False
            
        if not self.being_built:
            surface.blit(ROOMS[self.name][0],(self.pos_x,self.pos_y))
        else:
            surface.blit(ROOMS[self.name][1],(self.pos_x,self.pos_y))