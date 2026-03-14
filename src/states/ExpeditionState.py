from .State import State
import pygame
import math
from exploration.ExpeditionMap import ExpeditionMap
from .BattleState import BattleState
from lib.perlin import Perlin
from exploration.Utilities import weight_to_color
CELL_SIZE=5
CHUNK_SIZE=32
MAX_CHUNK_DIST=8
class ExpeditionState(State):

    def __init__(self, state_manager):
        super().__init__(state_manager, "expedition", ["pause"])

        # TODO: implémenter le système d'expédition
        self.expedition_map=ExpeditionMap(seed=12345)
        self.cam_x=600
        self.cam_y=400
        self.camera_zoom=1.0
        self.screen=self.game.screen
        
        self.cam_world=pygame.Surface((1000,700),pygame.SRCALPHA | pygame.HWSURFACE)              
        self.clock=pygame.time.Clock()
        self.state='map'
        self.selected_node=None
        self.menu_rects={}
        self.auto=False
        self.waiting_for_battle_result=False
        self.perlin=Perlin(
            scale=200,
            octaves=4,
            steps=4,
            normalize=True
            )
        self.screen_sizes=self.screen.get_width(),self.screen.get_height()
        self.pygame_surf=pygame.Surface(
            (self.screen_sizes[0],self.screen_sizes[1])
        )
        self.chunks={}
        self.noise=self.perlin.noise_map(CELL_SIZE,CELL_SIZE)
        
        self.base_colors = {
            1: (210,180,120),
            2: (80,160,80),
            3: (130,90,60),
            4: (120,120,120),
        }
        self.cells_color={
            col:[
                self.draw_cells(color,mask)
                for mask in range(16)
            ]
            for col,color in self.base_colors.items()
        }
    def update(self,events):
        if self.waiting_for_battle_result:
            battle_state=self.stateManager.states_managers.get("battle")
            if battle_state and battle_state.model.battle_won is not None:
                if battle_state.model.battle_won:
                    #On marque la node comme conquise
                    if self.selected_node:
                        self.expedition_map.clear(self.selected_node)
                        
                        self.selected_node = None
                self.waiting_for_battle_result=False
                #On retire le BattleState (pour préparer le suivant)CELL_SIZE
                self.stateManager.states_managers["battle"]=None
                self.state='map'
                return
        if self.state=="map":
            self.map_state(events)
        elif self.state=="node_menu":
            self.node_menu_state(events)
        
    def draw(self):
        if self.state=="map":
            self.draw_map_state()
        elif self.state=="node_menu":
            self.draw_map_state()
            self.draw_node_menu()
        
    def map_state(self,events):
        
        for event in events:
            if event.type==pygame.QUIT:
                self.stateManager.game.running=False
            if event.type==pygame.MOUSEBUTTONDOWN:
                world_x,world_y=event.pos[0]+self.cam_x,event.pos[1]+self.cam_y
                clicked_node=self.expedition_map.get_node_at_pos(world_x,world_y)
                
                if clicked_node:
                    if self.expedition_map.node_is_accessible(clicked_node):
                        self.selected_node=clicked_node
                        self.state="node_menu"
                    else:
                        font=pygame.font.Font(None,24)
                        text=font.render("Preceding node must be cleared first",True,(255,255,255))
                        text_rect=text.get_rect()
                        text_rect.center=(clicked_node.position-50,clicked_node.position+50)
                        self.screen.blit(text,text_rect)
        keys=pygame.key.get_pressed()
        speed=10
        if keys[pygame.K_z]:
            self.camera_zoom=min(self.camera_zoom+0.1,2.0)
        if keys[pygame.K_w]:
            self.camera_zoom=min(self.camera_zoom-0.1,2.0)
        if keys[pygame.K_UP]:
            self.cam_y-=speed
        if keys[pygame.K_DOWN]:
            self.cam_y+=speed
        if keys[pygame.K_LEFT]:
            self.cam_x-=speed
        if keys[pygame.K_RIGHT]:
            self.cam_x+=speed
    def draw_map_state(self):
        chunk_pixel = CHUNK_SIZE * CELL_SIZE
        start_cx = int(self.cam_x // chunk_pixel)
        start_cy = int(self.cam_y // chunk_pixel)
        end_cx = int((self.cam_x + self.screen_sizes[0]) // chunk_pixel) + 1
        end_cy = int((self.cam_y + self.screen_sizes[1]) // chunk_pixel) + 1
        for cx in range(start_cx, end_cx):
            for cy in range(start_cy, end_cy):
                chunk = self.get_chunk(cx, cy)
                screen_x = cx * chunk_pixel - self.cam_x
                screen_y = cy * chunk_pixel - self.cam_y
                self.screen.blit(chunk, (screen_x, screen_y))
        
        for (cx, cy) in list(self.chunks):
            if abs(cx - start_cx) > MAX_CHUNK_DIST or abs(cy - start_cy) > MAX_CHUNK_DIST:
                del self.chunks[(cx, cy)]
        #self.screen.fill((100,100,150)) # Faut trouver une image de bg, ptt un truc qui se genere aussi au fur et a mesure qu'on avance
        self.expedition_map.draw(self.screen,self.cam_x,self.cam_y) # TODO: Foutre une cam+zoom
        pygame.display.flip()
        
    
    def draw_node_menu(self):
        node=self.selected_node
        if not node:
            return
        menu_x=node.position[0]-self.cam_x+20
        menu_y=node.position[1]-self.cam_y+20
        width,height=180,100
        menu_rect=pygame.Rect(menu_x,menu_y,width,height)
        pygame.draw.rect(self.screen,(40,40,40),menu_rect)
        pygame.draw.rect(self.screen,(255,255,255),menu_rect,2)
        font=pygame.font.Font(None,24)
        manual_rect=pygame.Rect(menu_x+10,menu_y+20,160,30)
        auto_rect=pygame.Rect(menu_x+10,menu_y+60,160,30)
        pygame.draw.rect(self.screen, (70,70,70), manual_rect)
        pygame.draw.rect(self.screen, (70,70,70), auto_rect)
        self.screen.blit(font.render("Manual Battle", True, (255,255,255)), (manual_rect.x+10, manual_rect.y+5))
        self.screen.blit(font.render("Auto Resolve", True, (255,255,255)), (auto_rect.x+10, auto_rect.y+5))
        self.menu_rects={
            "manual":manual_rect,
            "auto":auto_rect
        }
    def node_menu_state(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.menu_rects["manual"].collidepoint(event.pos):
                    self.auto = False
                    self.start_battle()
                elif self.menu_rects["auto"].collidepoint(event.pos):
                    self.auto = True
                    self.start_battle()
                else:
                    self.state = "map"
                    self.selected_node = None
    def start_battle(self):
        current_node = self.selected_node

        self.stateManager.start_battle(
            current_node.difficulty,
            colony=[],
            auto=self.auto,
            world_pos=current_node.position
        )
        
        
        self.waiting_for_battle_result = True 
    
    def draw_cells(self,base_color,mask):
        surf=pygame.Surface((CELL_SIZE,CELL_SIZE))
        surf.fill(base_color)
        for x in range(CELL_SIZE):
            for y in range(CELL_SIZE):
                n=self.noise[x][y]
                shade=int((n-0.5)*40)
                color=(
                    max(min(base_color[0] + shade, 255), 0),
                    max(min(base_color[1] + shade, 255), 0),
                    max(min(base_color[2] + shade, 255), 0),
                )
                surf.set_at((x,y),color)
        edge_color=tuple(max(c-30,0) for c in base_color)
        if not (mask & 1):
            pygame.draw.rect(surf,edge_color,(0,0,CELL_SIZE,4))
        if not (mask & 2):
            pygame.draw.rect(surf,edge_color,(CELL_SIZE-4,0,4,CELL_SIZE))
        if not (mask & 4):
            pygame.draw.rect(surf,edge_color,(0,CELL_SIZE-4,CELL_SIZE,4))
        if not (mask & 8):
            pygame.draw.rect(surf,edge_color,(0,0,4,CELL_SIZE))
        return surf
    """
    def get_mask(self,x,y):
        #Bitmask à partir des voisins (1 pour le haut, 2 pour la droite, 4 pour le bas et 8 pour la gauche)
        w=self.weights[(x,y)]
        mask=0
        width,height=self.screen_sizes[0]//4,self.screen_sizes[1]//4
        if y>0 and self.weights[(x,y-1)]==w:
            mask|=1
        if x<width-1 and self.weights[(x+1,y)]==w:
            mask|=2
        if y<height-1 and self.weights[(x,y+1)]==w:
            mask|=4
        if x>0 and self.weights[(x-1,y)]==w:
            mask|=8
        return mask
    """
    def get_mask(self, x, y):
        w = self.get_weight(x, y)
        mask = 0
        if self.get_weight(x, y-1) == w:
            mask |= 1
        if self.get_weight(x+1, y) == w:
            mask |= 2
        if self.get_weight(x, y+1) == w:
            mask |= 4
        if self.get_weight(x-1, y) == w:
            mask |= 8

        return mask
        
    def get_weight(self,x,y):
        n=self.perlin.noise(x,y)
        return int(n*3)+1
    def generate_chunk(self,cx,cy):
        surf=pygame.Surface(
            (CHUNK_SIZE*CELL_SIZE,CHUNK_SIZE*CELL_SIZE)
        )
        weights={
            (x,y):self.get_weight(cx*CHUNK_SIZE+x,cy*CHUNK_SIZE+y)
            for x in range(-1,CHUNK_SIZE+1)
            for y in range(-1,CHUNK_SIZE+1)
        }
        for x in range(CHUNK_SIZE):
            for y in range(CHUNK_SIZE):
                w=weights[(x,y)]
                mask = 0
                if weights[(x, y-1)] == w: mask |= 1
                if weights[(x+1, y)] == w: mask |= 2
                if weights[(x, y+1)] == w: mask |= 4
                if weights[(x-1, y)] == w: mask |= 8
                surf.blit(
                    self.cells_color[w][mask],
                    (x*CELL_SIZE,y*CELL_SIZE)
                )
        return surf
    def get_chunk(self, cx, cy):

        if (cx, cy) not in self.chunks:
            self.chunks[(cx, cy)] = self.generate_chunk(cx, cy)

        return self.chunks[(cx, cy)]