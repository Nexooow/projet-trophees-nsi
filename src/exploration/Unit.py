import pygame
class Unit:
    def __init__(self, x, y, image, team,power=1,points=5,diagonal=False):
        self.x = x
        self.y = y
        self.team=team
        self.image = image
        self.points_max = points
        self.points = points
        self.orientation = False
        self.diagonal=diagonal
        self.power=power
        self.alive=True
        self.size=100
        self.image_scale=0.5
        self.frames=self.load_frames()
        self.image=self.frames[0][self.frame_index]
        self.static=self.frames[0][1]
        self.time=pygame.time.get_ticks()
        self.destination=None
        self.speed=0.1
    def load_frames(self):
        frames = []
        spritesheet, animation_steps = self.image,[2]
        for y, x in enumerate(animation_steps):
            temp = []
            for i in range(x):
                temp_img = spritesheet.subsurface(
                    i * self.size, y * self.size, self.size, self.size
                )
                temp_img = pygame.transform.scale(
                    temp_img,
                    (self.size * self.image_scale, self.size * self.image_scale),
                )
                temp += [temp_img]
            frames += [temp]
        return frames
    def tile(self):
        return self.x, self.y
    def attack(self,target,units):
        target.alive=False
        units.remove(target)
        
    def reset_turn(self):
        self.points = self.points_max

    def move_to(self, x, y):
        self.is_static=False
        self.destination=(x,y)
        self.x+= (x-self.x)*self.speed
        self.y+= (y-self.y)*self.speed
    
    def draw(self, screen):
        self.update()
        img = pygame.transform.flip(self.image, not self.orientation, False)
        screen.blit(img, (self.x*50, self.y*50))
    def is_static(self):
        if (self.x,self.y)==self.destination:
            self.is_static=True
    def update(self):

        if not self.is_static:
            animation_cooldown=150
            if pygame.time.get_ticks()-self.time>animation_cooldown:
                self.frame_index+=1
                self.time=pygame.time.get_ticks()
            if self.frame_index >= len(self.frames[self.action]):
                self.frame_index = 0
            self.image = self.frames[self.action][self.frame_index]