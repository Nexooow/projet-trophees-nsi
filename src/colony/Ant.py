import pygame
from Path_search import a_star_search,converting_to_grid
import math
IMAGES={
    "worker":[pygame.image.load(''),[]],
    "nurse":[pygame.image.load(""),[]],
    "warrior":[pygame.image.load(""),[]],
    "scientist":[pygame.image.load(""),[]],
    "explorer":[pygame.image.load(''),[]]
}
class Ant:
    def __init__(self,id,power,level,xp,pos_x,pos_y,flip=False):
        
        self.colony=None
        self.power=power
        self.level=level
        self.xp=xp
        self.id=id
        self.size=50
        self.image_scale=1
        self.animation_list=self.load_frames()
        self.action = 0
        self.frame_index = 0
        self.image = self.animation_list[self.action][self.frame_index]
        self.static=self.animation_list[0][1]
        self.flip=flip
        self.angle=0
        self.rect=pygame.Rect((pos_x,pos_y,self.size*self.image_scale,self.size*self.image_scale))
        self.img_pos=(self.rect.x,self.rect.y )
        self.speed=1.0
    def update(self):
        self.image = self.animation_list[self.action][self.frame_index]
        animation_cooldown=50
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.frame_index += 1
            self.update_time = pygame.time.get_ticks()
        if self.frame_index >= len(self.animation_list[self.action]):
            self.frame_index=0
    def draw(self,surface):
        img = pygame.transform.flip(self.image, self.flip, False)
        self.img_pos = (self.rect.x - (self.image_scale),
                        self.rect.y - (self.image_scale))
        surface.blit(img, self.img_pos)
        self.mask = pygame.mask.from_surface(img)
    def load_frames(self):
        frames=[]
        spritesheet,animation_steps=IMAGES[self.id][0],IMAGES[self.id][1]
        for y,x in enumerate(animation_steps):
            temp=[]
            for i in range(x):
                temp_img=spritesheet.subsurface(i*self.size,y*self.size,self.size,self.size)
                temp_img=pygame.transform.scale(temp_img,(self.size*self.image_scale,self.size*self.image_scale))
                temp+=[temp_img]
            frames+=[temp]
        return frames
    def move(self,surface,destination):
        
        grid_posx,grid_posy=pixel_to_grid(self.pos_x,self.pos_y)
        destination_grid=pixel_to_grid(destination[0],destination[1])
        next=a_star_search(converting_to_grid(surface),(grid_posx,grid_posy),destination_grid)[1]
        next_pixelx,next_pixely=grid_to_pixel(next[0],next[1])
        dx,dy=next_pixelx - self.pos_x,next_pixely-self.pos_y
        dist=math.hypot(dx,dy)
        if dist<self.speed:
            self.pos_x,self.pos_y=next_pixelx,next_pixely
            return
        self.flip=True if dx>0 else False
        dir_x,dir_y=dx/dist,dy/dist
        self.pos_x+=dir_x*self.speed
        self.pos_y+=dir_y*self.speed
        self.orientation=math.degrees(math.atan2(-dir_y,dir_x))
CELL_SIZE=8
def pixel_to_grid(px,py):
    return px//CELL_SIZE,py//CELL_SIZE
def grid_to_pixel(gx,gy):
    return gx*CELL_SIZE+CELL_SIZE//2,gy*CELL_SIZE+CELL_SIZE//2

