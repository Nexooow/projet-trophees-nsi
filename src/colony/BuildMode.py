import pygame

from config.settings import (
    colony_brush_color,
    colony_brush_size,
    colony_height,
    colony_underground_start,
    colony_width,
)

class BuildMode:
    
    def __init__(self, colony_state):
        self.colony = colony_state
        self.enabled = False
        self.selections = set()

    def switch(self):
        self.enabled = not self.enabled

    def update(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:  # clear
                    self.selections.clear()
                elif event.key == pygame.K_KP_ENTER:
                    pass  # TODO

        if pygame.mouse.get_pressed()[2]:
            mouse_pos = pygame.mouse.get_pos()
            mouse_pos = (
                mouse_pos[0] - self.colony.camera_x,
                mouse_pos[1] - self.colony.camera_y,
            )
            if (
                mouse_pos[0] >= 0
                and mouse_pos[0] < colony_width
                and mouse_pos[1] >= 0
                and mouse_pos[1] < colony_height
                and mouse_pos[1] > colony_underground_start + colony_brush_size
            ):
                brush_x = mouse_pos[0] - colony_brush_size // 2
                brush_y = mouse_pos[1] - colony_brush_size // 2
                self.selections.add((brush_x, brush_y))

    def draw(self):
        mouse_pos = pygame.mouse.get_pos()
        mouse_world_pos = (
            mouse_pos[0] - self.colony.camera_x,
            mouse_pos[1] - self.colony.camera_y,
        )

        for x, y in self.selections:
            pygame.draw.rect(
                self.colony.world,
                colony_brush_color,
                (x, y, colony_brush_size, colony_brush_size),
            )

        if (
            mouse_world_pos[0] >= 0
            and mouse_world_pos[0] < colony_width
            and mouse_world_pos[1] >= 0
            and mouse_world_pos[1] < colony_height
            and mouse_world_pos[1] > colony_underground_start + colony_brush_size
        ):
            brush_x = mouse_world_pos[0] - colony_brush_size // 2
            brush_y = mouse_world_pos[1] - colony_brush_size // 2

            pygame.draw.rect(
                self.colony.world,
                colony_brush_color,
                (brush_x, brush_y, colony_brush_size, colony_brush_size),
            )
            
    def dig_selection (self):
        """
        Ajoute aux tâches les zones à creuser.
        """
        pass
