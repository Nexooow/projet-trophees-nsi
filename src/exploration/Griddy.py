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
from lib.perlin import Perlin
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

class Bomb:
    def __init__(self,x,y):
        self.x=x
        self.y=y
    def get_pos(self):
        return (self.x,self.y)
    def explode(self,units):
        for u in units:
            if abs(u.x-self.x)<=1 and abs(u.y-self.y)<=1:
                u.points=0
    #TODO:implementer systeme de destruction sur plusieurs tiles, soit par tile prédéterminée, soit par troupe (typa kamikaze)
GRID_W=20
GRID_H=14
TILE_SIZE=50
SIDEBAR_WIDTH=250
GRID_WIDTH=1000
HEIGHT=700
class Grid:
    def __init__(self,width,height,tile_size=50):
        self.width=width
        self.height=height
        self.tile=tile_size
        edges=[]
        perlin = Perlin(
                seed=42,
                scale=20,
                octaves=4,
                steps=4,
                normalize=True
                )
        noise_map=perlin.noise_map(self.width,self.height)
        #self.weights={(x,y):choice([1,2,3,4 ]) for x in range(self.width) for y in range(self.height)}
        self.weights={}
        for y in range(self.height):
            for x in range(self.width):
                value=noise_map[y][x]
                weight=int(value*3)+1
                self.weights[(x,y)]=weight
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
class Sidebar:
    def __init__(self,width,height):
        self.width=width
        self.height=height
    def draw(self,screen,units,active,colony):
        screen.fill((30, 30, 30))
        font = pygame.font.SysFont(None, 28)
        friendlies = len([u for u in units if u.team == "noir"])
        enemies = len([u for u in units if u.team == "rouge"])
        lines = [
            f"Active Team: {active.team}",
            f"Action Points: {active.points}",
            "",
            f"Friendlies: {friendlies}",
            f"Enemies: {enemies}",
            "",
            "Resources:"
        #TODO: Montrer les ressources que l'expédition a récup / celles qu'il y a au total
        ]
        y = 20
        for line in lines:
            text = font.render(line, True, (255,255,255))
            screen.blit(text, (20, y))
            y += 35
class Game:
    def __init__(self):
        self.battle_won=None
        self.sidebar=Sidebar(SIDEBAR_WIDTH,HEIGHT)
            
    def game(self,difficulty,colony):
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
        
        
        screen = pygame.display.set_mode((SIDEBAR_WIDTH+GRID_WIDTH, HEIGHT))
        game_surface = pygame.Surface((GRID_WIDTH, HEIGHT))
        ui_surface = pygame.Surface((SIDEBAR_WIDTH, HEIGHT))
        clock = pygame.time.Clock()
        img_fourmi=pygame.image.load("./assets/fonts/ant.png")
        img_scarab=pygame.image.load("./assets/fonts/ant.png")
        fourmis_nwar=colony.get_ants(ant_type="soldier") if type(colony) is not list else [] #Récup les fourmis de l'expedition (colony c pas une classe colony mais une classe ExplorerGroup)
        
        positions=list(product(range(20),range(4)))
        pos1=sample(positions,randint(1,6))
        ally_pos=list(product(range(20),range(10,14)))
        fourmis_nwar.append(AntPuppet(1)) # Pour des tests
        fourmis_nwar.append(AntPuppet(1))
        pos2=sample(ally_pos,randint(1,len(fourmis_nwar)))
        
        friendlies=[Unit(x,y,img_fourmi,"noir",ant.power) for ant in fourmis_nwar for x,y in pos2] if len(fourmis_nwar)>0 else []
        """
        units=[
            choices([Unit(x, y, img_fourmi, "rouge",power=difficulty),Unit(x,y,img_scarab,"rouge",power=difficulty,points=3,diagonal=True)],weights=(4,1),k=1)[0]
            for x,y in pos1
        ]
        """
        units=[Unit(0,0,img_fourmi,"rouge",power=difficulty)]
        units+=friendlies
    
        turn_index=0
        shuffle(units)
        active=units[turn_index]
        grid = Grid(20, 14)
        running=True
        
        while running:
            game_surface.fill((0,0,0))
            ui_surface.fill((30,30,30))
            grid.draw(game_surface)
            #screen.fill((0,0,0))
            #grid.draw(screen)
            for ressource in ressources_obj:
                ressource.draw(game_surface)
            friendlies=[u for u in units if u.team=='noir']
            
            for u in units:
                u.is_static()
                u.draw(game_surface)
            
            self.sidebar.draw(ui_surface,units,active,colony)
            screen.blit(game_surface,(0,0))
            screen.blit(ui_surface,(GRID_WIDTH,0))
            
            for event in pygame.event.get():
                if event.type==pygame.QUIT:
                    running=False
                    pygame.quit()
                    return
                print(active.team,active.points,active.tile())
                
                if active.points > 0 and (len(friendlies)>0 and len([u for u in units if u.team=="rouge"])>0) and active.static_state:
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
                            print(path)
                            if path:
                                active.points-=grid.weights[(active.x,active.y+1)]
                                active.move_to(*path[0])
                            
                    
                    if active.team=="noir":
                        if event.type==pygame.KEYDOWN:
                            tiles=reachable_tiles(active.x,active.y,active.points,grid)
                            if (active.x,active.y) in ressources_dispos.keys():
                                colony.add_to_stock(ressources_dispos[(active.x,active.y)])
                                ressources_dispos.pop((active.x,active.y))
                            if event.key==pygame.K_LEFT and active.x > 0 and all([(active.x-1,active.y)!=(u.x,u.y) for u in friendlies])   and (active.x-1,active.y) in tiles :
                                active.points -= grid.weights[(active.x-1,active.y)]
                                active.orientation = True
                                active.move_to(active.x - 1, active.y)
                                

                            elif event.key==pygame.K_RIGHT and active.x < grid.width - 1 and all([(active.x+1,active.y)!=(u.x,u.y) for u in friendlies]) and (active.x+1,active.y) in tiles:
                                active.points -= grid.weights[(active.x+1,active.y)]
                                active.orientation = False
                                active.move_to(active.x + 1, active.y)
                                
                                

                            elif event.key==pygame.K_UP and active.y > 0 and all([(active.x,active.y-1)!=(u.x,u.y) for u in friendlies]) and (active.x,active.y-1) in tiles:
                                active.points -= grid.weights[(active.x,active.y-1)]
                                active.move_to(active.x, active.y - 1)
                                

                            elif event.key==pygame.K_DOWN and active.y < grid.height - 1 and all([(active.x,active.y-1)!=(u.x,u.y) for u in friendlies]) and (active.x,active.y+1) in tiles:
                                active.points -= grid.weights[(active.x,active.y+1)]
                                active.move_to(active.x, active.y + 1)
                            elif event.key==pygame.K_SPACE:
                                active.points=0

                    print(active)
                    active.is_static()   
                    for enemy in enemies:
                        if (enemy.x,enemy.y)==(active.x,active.y):
                            units.remove(enemy)
                    
                    friendlies=[u for u in units if u.team=='noir']
                    print(len(friendlies),len([u for u in units if u.team=="rouge"]))
                    if len(friendlies)<1:
                        self.battle_won=False
                        running=False
                    if len([u for u in units if u.team=="rouge"])<1:
                        self.battle_won=True
                        running=False
                
                else:
                    active.reset_turn()
                    turn_index = (turn_index + 1) % len(units)
                    active = units[turn_index]
                
            pygame.display.flip()
