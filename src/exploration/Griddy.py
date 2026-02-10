import heapq
import networkx as nx
import pygame
from random import randint, choice, shuffle,sample
from itertools import product
pygame.init()
def xy_to_node(x,y,cols):
    return y*cols+x
def node_to_xy(node,cols):
    return (node%cols,node//cols)
def neighbors(x,y,width,height,diagonal=False):
    dirs=[(1,0),(-1,0),(0,1),(0,-1)]
    if diagonal:
        dirs+=[(1,1),(-1,-1),(1,-1),(-1,1)]
    for dx,dy in dirs :
        nx,ny=x+dx,y+dy
        if 0<=nx<width and 0<=ny<height:
            yield nx,ny
"""
def reachable_tiles(start_x,start_y,max_cost,width,height):
    reachable={}
    queue=deque([(start_x,start_y,0)])
    visited=set()
    
    while queue:
        x,y,cost=queue.popleft()
        if cost>max_cost or (x,y) in visited:
            continue
        visited.add(x,y)
        reachable[(x,y)]=cost
        for nx,ny in neighbors(x,y,width,height):
            queue.append((nx,ny,cost+1))
    return reachable
"""
def reachable_tiles(x,y,points,grid):
    reachable={}
    pq=[(0,x,y)]

    while pq:
        cost,cx,cy=heapq.heappop(pq)

        if cost>points:
            continue

        if (cx,cy) in reachable and cost>=reachable[(cx,cy)]:
            continue

        reachable[(cx,cy)]=cost

        for nx_,ny_ in neighbors(cx,cy,grid.width,grid.height):
            tile_cost=grid.weights[(nx_,ny_)]
            heapq.heappush(pq,(cost+tile_cost,nx_,ny_))
    return reachable

def shortest_path(start,target,graph,grid_width,blocked_positions=(),diagonals=False,diagonal_edges=()):
    G=graph.copy()
    if diagonals:
        G.add_edges_from(diagonal_edges)
    for x,y in blocked_positions:
        try:
            G.remove_node(xy_to_node(x,y,grid_width))
        except nx.NetworkXError:
            pass
    try:
        path=nx.shortest_path(G,xy_to_node(*start,grid_width),xy_to_node(*target,grid_width),weight="weight")
    except nx.NetworkXNoPath:
        return []
    return [node_to_xy(node,grid_width) for node in path][1:]

terrains={"dirt":{"weight":1,"img":""},"mud":{"weight":2,"img":""},"water":{"weight":3,"img":""},"stone":{"weight":float("inf"),"img":""}}
def weight_to_color(weight):
    #return {1:(50,180,50),2:(160,120,60),3:(50,100,180),100:(128,128,128)}.get(weight,(100,100,100))
    return terrains[weight]["weight"] if weight in terrains else ""
def closest_enemy(unit,enemies,grid,units):
    blocked=[(u.x,u.y) for u in units if u is not unit]
    closest=None
    dist=float("inf")
    for enemy in enemies:
        path=shortest_path(
            unit.tile(),
            enemy.tile(),
            grid.graph,grid.width,
            blocked,
            diagonals=unit.diagonal,
            diagonal_edges=grid.diagonal_edges
        )
        if path and len(path)<dist:
            dist=len(path)
            closest=enemy
    return closest
class Grid:
    def __init__(self,width,height,tile_size=50):
        self.width=width
        self.height=height
        self.tile=tile_size
        edges=[]
        self.weights={(x,y):choice([1,2,3,100]) for x in range(self.width) for y in range(self.height)}
        for y in range(height):
            for x in range(width):
                i=xy_to_node(x,y,width)
                for nx,ny in neighbors(x,y,width,height):
                    edges.append((i,xy_to_node(nx,ny,width)),{"weight":self.weights[(nx,ny)]})
        self.graph=nx.DiGraph(edges)
        self.diagonal_edges = []
        for y in range(height):
            for x in range(width):
                i = xy_to_node(x, y, width)
                for dx, dy in ((1,1),(1,-1),(-1,1),(-1,-1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < width and 0 <= ny < height:
                        j = xy_to_node(nx, ny, width)
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

class Unit:
    def __init__(self, x, y, image, team,power=1,points=5,diagonal=False):
        self.x = x
        self.y = y
        self.team=team
        self.image = pygame.transform.scale(image, (50,50))
        self.points_max = points
        self.points = points
        self.orientation = False
        self.diagonal=diagonal
        self.power=power
    def tile(self):
        return self.x, self.y

    def reset_turn(self):
        self.points = self.points_max

    def move_to(self, x, y):
        self.x = x
        self.y = y

    def draw(self, screen):
        img = pygame.transform.flip(self.image, False, self.orientation)
        screen.blit(img, (self.x*50, self.y*50))
def Game(difficulty,colony):
    screen = pygame.display.set_mode((1000, 700))
    clock = pygame.time.Clock()
    img_fourmi=pygame.image.load("")
    img_scarab=pygame.image.load("")
    fourmis_nwar=colony.get_ants("soldier")
    friendlies=[Unit(choice(range(20)),choice(range(10,14)),img_fourmi,"noir",ant.power) for ant in fourmis_nwar]
    positions=list(product(range(20),range(4)))
    pos1=sample(positions,randint(1,6))
    ally_pos=list(product(range(20),range(4)))
    units=[
        choice([Unit(choice(range(20)), choice(range(4)), img_fourmi, "rouge",power=difficulty),Unit(choice(range(20)),choice(range(4)),img_scarab,"rouge",power=difficulty,points=3)],weights=(4,1),k=1)
        for _ in range(1,6)
    ]
    units.append(friendlies)
    turn_index=0
    shuffle(units)
    active=units[turn_index]
    grid = Grid(20, 14)
    running=True
    grid.draw(screen)
    while running:
        screen.fill(0,0,0)
        
        for u in units:
            u.draw(screen)
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                running=False
        keys=pygame.key.get_pressed()
        
        if active.points > 0:
            enemies = [u for u in units if u.team != active.team]
            if active.team!="noir":
                target = closest_enemy(active, enemies,grid,units)
                blocked = [u.tile() for u in units if u is not active]
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
                if keys[pygame.K_LEFT] and active.x > 0:
                    active.move_to(active.x - 1, active.y)
                    active.points -= 1
                    active.orientation = True

                elif keys[pygame.K_RIGHT] and active.x < grid.width - 1:
                    active.move_to(active.x + 1, active.y)
                    active.points -= 1
                    active.orientation = False

                elif keys[pygame.K_UP] and active.y > 0:
                    active.move_to(active.x, active.y - 1)
                    active.points -= 1

                elif keys[pygame.K_DOWN] and active.y < grid.height - 1:
                    active.move_to(active.x, active.y + 1)
                    active.points -= 1
        else:
            active.reset_turn()
            turn_index = (turn_index + 1) % len(units)
            active = units[turn_index]
Game()