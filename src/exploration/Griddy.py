import heapq
import networkx as netx
import pygame
from random import randint, choice, shuffle,sample,choices
from itertools import product
from .Utilities import *
from .Unit import *
from .ExplorerGroup import *
import math
from .AntPuppet import AntPuppet
RESSOURCES_IMAGES={
    "nom":pygame.image.load("./assets/fonts/ant.png")
}
RESSOURCES=["nom"]
pygame.init()
class HoveringResource:
    def __init__(self,x,y,resource,tile_size=50):
        self.x=x
        self.y=y
        self.resource=resource
        self.tile_size=tile_size
        self.start_time=pygame.time.get_ticks()
        self.hover_height=10
        self.hover_speed=0.005
    def draw(self,screen):
        elapsed_time=(pygame.time.get_ticks()-self.start_time)*self.hover_speed
        offset=self.hover_height*math.sin(elapsed_time)
        screen_x=self.x*self.tile_size
        screen_y=self.y*self.tile_size+offset
        screen.blit(RESSOURCES_IMAGES[self.resource],(screen_x,screen_y))
class Grid:
    def __init__(self,width,height,tile_size=50):
        self.width=width
        self.height=height
        self.tile=tile_size
        edges=[]
        self.weights={(x,y):choice([1,2,3,100]) for x in range(self.width) for y in range(self.height)}
        for y in range(height):
            for x in range(width):
                i=x,y
                for nx,ny in neighbors(x,y,width,height):
                    edges.append((i,(nx,ny),{"weight":self.weights[(nx,ny)]}))
        self.graph=netx.DiGraph(edges)
        self.diagonal_edges = []
        for y in range(height):
            for x in range(width):
                i = x,y
                for dx, dy in ((1,1),(1,-1),(-1,1),(-1,-1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < width and 0 <= ny < height:
                        j = nx,ny
                        cost = self.weights[(nx, ny)] * 1.414
                        self.diagonal_edges.append((i, j, {"weight": cost}))
    def draw(self,screen):
        for x in range(self.width):
            for y in range(self.height):
                w=self.weights[(x,y)]
                col=weight_to_color(w)
                r=pygame.Rect(x*self.tile,y*self.tile,self.tile,self.tile)
                pygame.draw.rect(screen,col,r)
                pygame.draw.rect(screen,(255,255,255),r,1)

def Game(difficulty,colony):
    positions_of_ressources=sample(list(product(range(20),range(4))),randint(1,5))
    
    ressources_dispos={
        (x,y):
        choice(
            RESSOURCES
        )
        for x,y in positions_of_ressources
    }
    ressources_obj=[
        HoveringResource(x,y,resource)
        for (x,y),resource in ressources_dispos.items() 
    ]
    screen = pygame.display.set_mode((1000, 700))
    clock = pygame.time.Clock()
    img_fourmi=pygame.image.load("./assets/fonts/ant.png")
    img_scarab=pygame.image.load("./assets/fonts/ant.png")
    fourmis_nwar=colony.get_ants(ant_type="soldier") if type(colony) is not list else [] #Récup les fourmis de l'expedition (colony c pas une classe colony mais une classe ExplorerGroup)
    
    positions=list(product(range(20),range(4)))
    pos1=sample(positions,randint(1,6))
    ally_pos=list(product(range(20),range(10,14)))
    fourmis_nwar.append(AntPuppet(1)) # Pour des tests
    
    pos2=sample(ally_pos,randint(1,len(fourmis_nwar)))
    
    friendlies=[Unit(x,y,img_fourmi,"noir",ant.power) for ant in fourmis_nwar for x,y in pos2] if len(fourmis_nwar)>0 else []

    units=[
        choices([Unit(x, y, img_fourmi, "rouge",power=difficulty),Unit(x,y,img_scarab,"rouge",power=difficulty,points=3,diagonal=True)],weights=(4,1),k=1)[0]
        for x,y in pos1
    ]
    
    units+=friendlies
   
    turn_index=0
    shuffle(units)
    active=units[turn_index]
    grid = Grid(20, 14)
    running=True
    
    while running:
        screen.fill((0,0,0))
        grid.draw(screen)
        for ressource in ressources_obj:
            ressource.draw(screen)
        for u in units:
            u.draw(screen)
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                running=False
                pygame.quit()
                return
            print(active.team,active.points,active.tile())
            
            if active.points > 0:
                enemies = [u for u in units if u.team != active.team]
                if active.team!="noir":
                    
                    target = closest_enemy(active, enemies,grid,units)
                    print(target)
                    if target is not None:
                        blocked = [u.tile() for u in units if (u is not active) and (u  not in enemies)]
                        path = shortest_path(
                            active.tile(),
                            target.tile(),
                            grid.graph,
                            grid.width,
                            blocked,
                            diagonals=active.diagonal,
                            diagonal_edges=grid.diagonal_edges
                        )
                        if path:
                            active.move_to(*path[0])
                            active.points -= 1
                
                if active.team=="noir":
                    if event.type==pygame.KEYDOWN:
                        if (active.x,active.y) in ressources_dispos.keys():
                            colony.add_to_stock(ressources_dispos[(active.x,active.y)])
                            ressources_dispos.pop((active.x,active.y))
                        if event.key==pygame.K_LEFT and active.x > 0 and all([(active.x-1,active.y)!=(u.x,u.y) for u in friendlies]) and :
                            active.move_to(active.x - 1, active.y)
                            active.points -= 1
                            active.orientation = True

                        elif event.key==pygame.K_RIGHT and active.x < grid.width - 1 and all([(active.x+1,active.y)!=(u.x,u.y) for u in friendlies]):
                            active.move_to(active.x + 1, active.y)
                            active.points -= 1
                            active.orientation = False

                        elif event.key==pygame.K_UP and active.y > 0 and all([(active.x,active.y-1)!=(u.x,u.y) for u in friendlies]):
                            active.move_to(active.x, active.y - 1)
                            active.points -= 1

                        elif event.key==pygame.K_DOWN and active.y < grid.height - 1 and all([(active.x,active.y-1)!=(u.x,u.y) for u in friendlies]):
                            active.move_to(active.x, active.y + 1)
                            active.points -= 1
                for enemy in enemies:
                    if (enemy.x,enemy.y)==(active.x,active.y):
                        units.remove(enemy)
            else:
                active.reset_turn()
                turn_index = (turn_index + 1) % len(units)
                active = units[turn_index]
        pygame.display.flip()
