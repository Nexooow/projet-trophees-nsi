import heapq
import networkx as nx
import pygame
from random import randint, choice
pygame.init()
def xy_to_node(x,y,cols):
    return y*cols+x
def node_to_xy(node,cols):
    return (node%cols,node//cols)
def neighbors(x,y,width,height):
    for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)):
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
def shortest_path(start,target,graph,grid_width,blocked_positions=()):
    G=graph.copy()
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
def weight_to_color(weight):
    return {1:(50,180,50),2:(160,120,60),3:(50,100,180)}.get(weight,(100,100,100))
def closest_enemy(unit,enemies,grid,units):
    blocked=[(u.x,u.y) for u in units if u is not unit]
    closest=None
    dist=float("inf")
    for enemy in enemies:
        path=shortest_path(
            unit.tile(),
            enemy.tile(),
            grid.graph,grid.width,
            blocked
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
        self.weights={(x,y):randint(1,3) for x in range(self.width) for y in range(self.height)}
        for y in range(height):
            for x in range(width):
                i=xy_to_node(x,y,width)
                for nx,ny in neighbors(x,y,width,height):
                    edges.append((i,xy_to_node(nx,ny,width)),{"weight":self.weights[(nx,ny)]})
        self.graph=nx.DiGraph(edges)
    def draw(self,screen):
        for x in range(self.width):
            for y in range(self.height):
                w=self.weights[(x,y)]
                col=weight_to_color(w)
                r=pygame.Rect(x*self.tile,y*self.tile,self.tile,self.tile)
                pygame.draw.rect(screen,col,r)
                pygame.draw.rect(screen,(255,255,255),r,1)

class Unit:
    def __init__(self, x, y, image, team, points=5):
        self.x = x
        self.y = y
        self.team=team
        self.image = pygame.transform.scale(image, (50,50))
        self.points_max = points
        self.points = points
        self.orientation = False

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
screen = pygame.display.set_mode((1000, 700))
clock = pygame.time.Clock()
units=[
    Unit(choice(range(20)), choice(range(10,14)), img_fourmi)
    for _ in range(randint(1, 5))
]
turn_index=0
active=units[turn_index]
grid = Grid(20, 14)
running=True
while running:
    screen.fill(0,0,0)
    grid.draw(screen)
    for u in units:
        u.draw(screen)
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            running=False
    keys=pygame.key.get_pressed()
    
    if active.points > 0:
        enemies = [u for u in units if u.team != active.team]
        target = closest_enemy(active, enemies,grid,units)
        blocked = [u.tile() for u in units if u is not active]
        path = shortest_path(
            active.tile(),
            target.tile(),
            grid.graph,
            grid.width,
            blocked
        )
        if path:
            active.move_to(*path[0])
            active.points -= 1
    else:
        active.reset_turn()
        turn_index = (turn_index + 1) % len(units)
        active = units[turn_index]