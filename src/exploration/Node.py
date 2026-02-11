from random import randint
import math
from Griddy import *
class Node:
    def __init__(self, node_id, parent=None,depth=0,seed=None):
        #self.x = x
        #self.y = y
        self.node_id=node_id
        self.parent = parent
        self.depth=depth
        self.seed=seed
        self.position=self.calculate_position()
        self.difficulty=min(1+depth,5)
        self.is_cleared=False
        self.is_discovered=False
        self.is_visible=False
        self.grid=None
        self.seed=seed or randint(0,10000)
        self.children=[]
        self.num_children=self.child_count()
    def calculate_position(self):
        if self.parent is None:
            return (0,0)
        parent_x,parent_y=self.parent.position
        num_siblings=len(self.parent.children)
        angle=(num_siblings*120)%360
        rad=math.radians(angle)
        distance=150
        x=parent_x+distance*math.cos(rad)
        y=parent_y+distance*math.sin(rad)
        return (x,y)
    def child_count(self):
        return randint(1,3)
    def generate_child(self):
        if self.children or self.is_cleared is False:
            return
        for i in range(self.num_children):
            child=Node(
                node_id=f'{self.node_id}_child_{i}',
                parent_node=self,
                depth=self.depth+1,
                seed=self.seed+i*1000
            )
            self.children.append(child)
            child.is_discovered=True
    def create_game(self,expedition_members):
        return Game(self.difficulty,expedition_members)
    def draw(self,screen,node_radius=20):
        x,y=self.position
        if self.is_cleared:
            color=(0,255,0)
        elif self.is_discovered:
            color=(255,0,0)
        elif self.is_visible:
            color=(128,128,128)
        else:
            return
        pygame.draw.circle(screen, color, (int(x), int(y)), node_radius)
        pygame.draw.circle(screen, (255, 255, 255), (int(x), int(y)), node_radius, 2)
        font = pygame.font.Font(None, 16)
        text = font.render(str(self.difficulty), True, (255, 255, 255))
        screen.blit(text, (int(x) - 8, int(y) - 8))
    def draw_links(self,screen):
        if self.parent and self.is_visible and self.parent.is_visible:
            parent_x,parent_y=self.parent.position
            child_x,child_y=self.position
            color = (150, 150, 150) if self.is_discovered else (80, 80, 80)
            pygame.draw.line(
                screen,
                color,
                (int(parent_x), int(parent_y)),
                (int(child_x), int(child_y)),
                2
            )
    