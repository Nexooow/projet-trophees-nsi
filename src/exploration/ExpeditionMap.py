import pygame
from .Node import Node
from random import randint
class ExpeditionMap:
    def __init__(self,seed=None):
        self.seed=seed or randint(0,10000)
        self.root_node=Node(
            node_id=0,
            parent=None,
            depth=0,
            seed=self.seed
        )
        self.root_node.is_discovered=True
        self.root_node.is_visible=True
        self.all_nodes=[self.root_node]
        self.current=self.root_node
    def get_visible_nodes(self):
        visible=[]
        def traverse(node):
            if node.is_visible:
                visible.append(node)
            for child in node.children:
                traverse(child)
        traverse(self.root_node)
        return visible
    def clear(self,node):
        print(node.is_cleared)
        if node.is_cleared:
            return
        node.is_cleared=True
        node.generate_child()
        for child in node.children:
            child.is_visible=True
            self.all_nodes.append(child)
    def get_node_at_pos(self,x,y,click_radius=30):
        for node in self.get_visible_nodes():
            if not node.is_discovered:
                continue
            node_x,node_y=node.position
            distance=((x-node_x)**2+(y-node_y)**2)**0.5
            
            if distance<=click_radius:
                return node
        return None
    def node_is_accessible(self,node):
        if not node.is_discovered:
            return False
        if node.parent is None:
            return True
        return node.parent.is_cleared
    def draw(self,screen,cam_x,cam_y):
        visible_nodes=self.get_visible_nodes()
        
        for node in visible_nodes:
            node.draw_links(screen,cam_x,cam_y)
        for node in visible_nodes:
            node.draw(screen,cam_x,cam_y) #Deux boucles pour que les nodes soient au-dessus des connections
        self.draw_info(screen,visible_nodes)
        
    def draw_info(self,screen,nodes):
        font=pygame.font.Font(None,24)
        cur_x,cur_y=self.current.position
        info_y=20
        text=[
            f"Current Node: {self.current.node_id}",
            f"Difficulty:{self.current.difficulty}",
            f"Status: {'Conquered' if self.current.is_cleared else 'Enemy territory'}",
            f"Donne acces a {len(self.current.children)} nodes"
            
        ]
        for i,line in enumerate(text):
            text=font.render(line,True,(255,255,255))
            screen.blit(text,(20,info_y+i*25))
            
            