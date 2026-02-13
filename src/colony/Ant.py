import pygame

from utils.file import File

IMAGES = {
    "worker": [pygame.image.load("./assets/ant.png"), [2]],
    "nurse": [pygame.image.load("./assets/ant.png"), [2]],
    "warrior": [pygame.image.load("./assets/ant.png"), [2]],
    "scientist": [pygame.image.load("./assets/ant.png"), [2]],
    "explorer": [pygame.image.load("./assets/ant.png"), [2]],
}

def convert_xp (xp: int):
    """
    Convertit l'expérience en niveaux
    """
    return (0, 0)

class Ant (pygame.sprite.Sprite):
    def __init__(self, colony, type: str, data: dict):
        
        super().__init__()
        self.colony = colony
        self.id = id(self)
        self.type = type
        self.data = data
        
        self.power = data["power"]
        
        (level, xp) = convert_xp(data["xp"] if "xp" in data else 0)
        self.level = level
        self.xp = xp
        
        self.direction = pygame.Vector2(0, 0)
    
        self.image_scale = 0.4
        self.size = 50*2
        self.is_static = False
        
        self.frames = self.load_frames()
        self.action = 0
        self.frame_index = 0
        self.image = self.frames[self.action][self.frame_index]
        self.static = self.frames[0][1]
        
        # TODO: gestion animations
        self.flip = data["flip"] if "flip" in data else False
        self.angle = 0
        self.rect=pygame.Rect((100,100,self.size*self.image_scale,self.size*self.image_scale))
        self.img_pos = (
            self.rect.x - (self.image_scale),
            self.rect.y - (self.image_scale),
        )
        self.update_time = pygame.time.get_ticks()
        
        self.path = File()
        self.next_cell = None
        
    def get_current_cell (self):
        return self.colony.grid.pixel_to_cell(self.x, self.y)
    
    def update(self):
        
        # Deplacement
        if self.next_cell is None and not self.path.est_vide():
            self.next_cell = self.path.defiler()
        
        (nx, ny) = self.next_cell
        (cx, cy) = self.get_current_cell()
        
        print(self.path, self.next_cell)
        vec = pygame.Vector2(x=-cx, y=-cy)
            
        
        # Animation
        if self.is_static:
            return
        self.image = self.frames[self.action][self.frame_index]
        animation_cooldown = 150
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.frame_index += 1
            self.update_time = pygame.time.get_ticks()
        if self.frame_index >= len(self.frames[self.action]):
            self.frame_index = 0

    def draw(self):
        img = pygame.transform.flip(self.image, self.flip, False)
        self.img_pos = (
            self.rect.x - (self.image_scale),
            self.rect.y - (self.image_scale),
        )
        self.colony.world.blit(img, self.img_pos)
        self.mask = pygame.mask.from_surface(img)

    def load_frames(self):
        frames = []
        spritesheet, animation_steps = IMAGES[self.type]
        for y, x in enumerate(animation_steps):
            temp = []
            for i in range(x):
                temp_img = spritesheet.subsurface(
                    i * self.size, y * self.size, self.size, self.size
                )
                temp_img = pygame.transform.scale(
                    temp_img,
                    (self.size * self.image_scale, self.size * self.image_scale),
                )
                temp += [temp_img]
            frames += [temp]
        return frames

    def move(self, destination):
        pass

    def set_path (self, path):
        for node in path:
            self.path.enfiler(node)
        if self.current_node is None:
            self.current_node = self.path.defiler()