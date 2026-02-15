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
    def update(self,events):
        if self.state=="map":
            self.map_state(events)
        elif self.state=="battle":
            self.battle_state(events)
    def draw(self):
        if self.state=="map":
            self.draw_map_state()
        elif self.state=="battle":
            self.draw_battle_state()
    def map_state(self,events):
        """
        for event in events:
            if event.type==pygame.QUIT:
                self.stateManager.game.running=False
        
            if event.type==pygame.MOUSEBUTTONDOWN:
                world_x,world_y=event.pos[0]+self.cam_x,event.pos[1]+self.cam_y
                clicked_node=self.expedition_map.get_node_at_pos(world_x,world_y)
                
                if clicked_node:
                    if self.expedition_map.node_is_accessible(clicked_node):
                        self.expedition_map.current=clicked_node
                        self.state="battle"
                    else:
                        font=pygame.font.Font(None,24)
                        text=font.render("Preceding node must be cleared first",True,(255,255,255))
                        text_rect=text.get_rect()
                        text_rect.center=(clicked_node.position-50,clicked_node.position+50)
                        self.screen.blit(text,text_rect)
            if event.type==pygame.KEYDOWN:
                if event.key==pygame.K_z:
                    self.camera_zoom=min(self.camera_zoom+0.1,2.0)
                if event.key==pygame.K_w:
                    self.camera_zoom=min(self.camera_zoom-0.1,2.0)
                if event.key==pygame.K_UP:
                    self.cam_y-=50
                if event.key==pygame.K_DOWN:
                    self.cam_y+=50
                if event.key==pygame.K_LEFT:
                    self.cam_x-=50
                if event.key==pygame.K_RIGHT:
                    self.cam_x+=50
        """
        for event in events:
            if event.type==pygame.QUIT:
                self.stateManager.game.running=False
            if event.type==pygame.MOUSEBUTTONDOWN:
                world_x,world_y=event.pos[0]+self.cam_x,event.pos[1]+self.cam_y
                clicked_node=self.expedition_map.get_node_at_pos(world_x,world_y)
                
                if clicked_node:
                    if self.expedition_map.node_is_accessible(clicked_node):
                        self.expedition_map.current=clicked_node
                        self.state="battle"
                    else:
                        font=pygame.font.Font(None,24)
                        text=font.render("Preceding node must be cleared first",True,(255,255,255))
                        text_rect=text.get_rect()
                        text_rect.center=(clicked_node.position-50,clicked_node.position+50)
                        self.screen.blit(text,text_rect)
        keys=pygame.key.get_pressed()
        speed=10
        if keys[pygame.K_UP]:
            self.cam_y-=speed
        if keys[pygame.K_DOWN]:
            self.cam_y+=speed
        if keys[pygame.K_LEFT]:
            self.cam_x-=speed
        if keys[pygame.K_RIGHT]:
            self.cam_x+=speed
    def draw_map_state(self):
        
        self.screen.fill((20,20,30)) # Faut trouver une image de bg, ptt un truc qui se genere aussi au fur et a mesure qu'on avance
        self.expedition_map.draw(self.screen,self.cam_x,self.cam_y) # TODO: Foutre une cam+zoom
        pygame.display.flip()
        
    def battle_state(self,events):
        for event in events:
            if event.type==pygame.QUIT:
                self.stateManager.game.running=False
            
            current_node=self.expedition_map.current
            grid=current_node.create_game()
            if event.type==pygame.KEYDOWN:
                self.state="map"
    def draw_battle_state(self):
        self.screen.fill((0,0,0))

