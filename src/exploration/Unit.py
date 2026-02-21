import pygame
class Unit:
    def __init__(self, x, y, image, team,power=1,points=5,diagonal=False):
        self.x = x
        self.y = y
        self.screen_x=x*50
        self.screen_y=y*50
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
        self.frame_index=0
        self.frames=self.load_frames()
        self.image=self.frames[0][self.frame_index]
        self.static=self.frames[0][1]
        self.static_state=True
        self.time=pygame.time.get_ticks()
        self.destination=None
        self.speed=0.1
        self.target_screen_x,self.target_screen_y=None,None
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
        
        self.destination=(x,y)
        print(f"Coords in move to:{self.x,self.y,self.destination}")
    
        self.static_state=False
        self.target_screen_x,self.target_screen_y=x*50,y*50
        print(f"Coord in move to:{self.x,self.y}")
    
    def draw(self, screen):
        self.update()
        img = pygame.transform.flip(self.image, not self.orientation, False)
        screen.blit(img, (self.screen_x, self.screen_y))
    def is_static(self):
        if self.destination is None:
            self.static_state=True
            return
        if abs(self.screen_x-self.target_screen_x)<0.1 and abs(self.screen_y-self.target_screen_y)<0.1:
            self.screen_x = self.target_screen_x
            self.screen_y = self.target_screen_y
            self.x = self.destination[0]
            self.y = self.destination[1]
            self.static_state = True
            self.destination = None

    def update(self):
        if not self.static_state and self.destination is not None:
            self.screen_x += (self.target_screen_x - self.screen_x) * self.speed
            self.screen_y += (self.target_screen_y - self.screen_y) * self.speed

        if not self.static_state:
            animation_cooldown=150
            if pygame.time.get_ticks()-self.time>animation_cooldown:
                self.frame_index+=1
                self.time=pygame.time.get_ticks()
            if self.frame_index >= len(self.frames[0]):
                self.frame_index = 0
            self.image = self.frames[0][self.frame_index]