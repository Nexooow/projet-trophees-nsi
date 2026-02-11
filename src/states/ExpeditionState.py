from .State import State
import pygame
import math
from src.exploration.ExpeditionMap import ExpeditionMap
class ExpeditionState(State):

    def __init__(self, state_manager, colony, difficulty=1):
        super().__init__(state_manager, "expedition", ["pause"])

        # TODO: implémenter le système d'expédition
        self.colony=colony
        self.difficulty=difficulty
        self.expedition_map=ExpeditionMap(seed=12345)
        self.cam_x=600
        self.cam_y=400
        self.camera_zoom=1.0
        self.screen=pygame.display.set_mode((1200,800))
        self.clock=pygame.time.Clock()
        self.state='map'
    def run(self):
        # C juste passager, faudra faire en sorte de separer 
        running=True
        while running:
            if self.state=="map":
                running=self.map_state()
            if self.state=="battle":
                running=self.battle_state()
        pygame.quit()
    def map_state(self):
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                return False
            if event.type==pygame.MOUSEBUTTONDOWN:
                clicked_node=self.expedition_map.get_node_at_pos(event.pos[0],event.pos[1])
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
                if event.type==pygame.K_z:
                    self.camera_zoom=min(self.camera_zoom+0.1,2.0)
                if event.type==pygame.K_w:
                    self.camera_zoom=min(self.camera_zoom-0.1,2.0)
                if event.type==pygame.K_UP:
                    self.cam_y-=50
                if event.type==pygame.K_DOWN:
                    self.cam_y+=50
                if event.type==pygame.K_LEFT:
                    self.cam_x-=50
                if event.type==pygame.K_RIGHT:
                    self.cam_x+=50
        self.screen.fill((20,20,30)) # Faut trouver une image de bg, ptt un truc qui se genere aussi au fur et a mesure qu'on avance
        pygame.draw.circle(self.screen, (255, 100, 100), (600, 400), 5)
        self.expedition_map.draw(self.screen,self.cam_x,self.cam_y)
        pygame.display.flip()
        self.clock.tick(60)
        return True
    def battle_state(self):
        current_node=self.expedition_map.current
        grid=current_node.create_game()

