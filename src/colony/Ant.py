import pygame

IMAGES = {
    "worker": [pygame.image.load(""), []],
    "nurse": [pygame.image.load(""), []],
    "warrior": [pygame.image.load(""), []],
    "scientist": [pygame.image.load(""), []],
    "explorer": [pygame.image.load(""), []],
}


class Ant:
    def __init__(self, id, power, level, xp, x, y, flip=False):
        self.colony = None
        self.power = power
        self.level = level
        self.xp = xp
        self.id = id
        self.size = 50
        self.image_scale = 1
        self.animation_list = self.load_frames()
        self.action = 0
        self.frame_index = 0
        self.image = self.animation_list[self.action][self.frame_index]
        self.static = self.animation_list[0][1]
        self.flip = flip
        self.angle = 0
        self.rect = pygame.Rect(
            (x, y, self.size * self.image_scale, self.size * self.image_scale)
        )
        self.img_pos = (
            self.rect.x - (self.image_scale),
            self.rect.y - (self.image_scale),
        )

    def update(self):
        self.image = self.animation_list[self.action][self.frame_index]
        animation_cooldown = 50
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.frame_index += 1
            self.update_time = pygame.time.get_ticks()
        if self.frame_index >= len(self.animation_list[self.action]):
            self.frame_index = 0

    def draw(self, surface):
        img = pygame.transform.flip(self.image, self.flip, False)
        self.img_pos = (
            self.rect.x - (self.image_scale),
            self.rect.y - (self.image_scale),
        )
        surface.blit(img, self.img_pos)
        self.mask = pygame.mask.from_surface(img)

    def load_frames(self):
        frames = []
        spritesheet, animation_steps = IMAGES[self.id]
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
