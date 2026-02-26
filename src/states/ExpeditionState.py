from .State import State
import pygame
import math
from exploration.ExpeditionMap import ExpeditionMap
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
    def update(self,events):
        if self.state=="map":
            self.map_state(events)
        elif self.state=="node_menu":
            self.node_menu_state(events)
        elif self.state=="battle":
            self.battle_state(events)
    def draw(self):
        if self.state=="map":
            self.draw_map_state()
        elif self.state=="node_menu":
            self.draw_map_state()
            self.draw_node_menu()
        elif self.state=="battle":
            self.draw_battle_state()
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
        
        self.screen.fill((100,100,150)) # Faut trouver une image de bg, ptt un truc qui se genere aussi au fur et a mesure qu'on avance
        self.expedition_map.draw(self.screen,self.cam_x,self.cam_y) # TODO: Foutre une cam+zoom
        pygame.display.flip()
        
    def battle_state(self,events):
        pass
    def draw_battle_state(self):
        self.screen.fill((0,0,0))
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
        current_node=self.selected_node
        self.state="battle"
        grid=current_node.create_game()
        grid.game(current_node.difficulty,colony=[],auto_resolve=self.auto)
        if grid.battle_won:
            self.expedition_map.clear(current_node)
        self.state = "map"
        self.selected_node = None
    
