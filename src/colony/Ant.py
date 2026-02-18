import pygame

from lib.file import File

IMAGES = {
    "worker": [pygame.image.load("./assets/ant.png"), [2]],
    "nurse": [pygame.image.load("./assets/ant.png"), [2]],
    "warrior": [pygame.image.load("./assets/ant.png"), [2]],
    "scientist": [pygame.image.load("./assets/ant.png"), [2]],
    "explorer": [pygame.image.load("./assets/ant.png"), [2]],
}


def convert_xp(xp: int):
    """
    Convertit l'expérience en niveaux
    """
    return (0, 0)


class Ant(pygame.sprite.Sprite):
    def __init__(self, colony, type: str, data: dict, pos):

        super().__init__()
        self.colony = colony
        self.id = id(self)
        self.type = type
        self.data = data

        self.power = data["power"]

        (level, xp) = convert_xp(data["xp"] if "xp" in data else 0)
        self.level = level
        self.xp = xp

        self.image_scale = 0.4
        self.size = 50 * 2
        self.frames = self.load_frames()
        self.action = 0
        self.frame_index = 0
        self.image = self.frames[self.action][self.frame_index]
        self.static = self.frames[0][1]
        self.update_time = pygame.time.get_ticks()

        self.flip = False
        self.angle = 0
        self.pos = pygame.Vector2(pos)
        self.rect = self.image.get_rect(center=pos)
        self.direction = pygame.Vector2(0, 0)

        # Système de déplacement
        self.speed = 2.0  # Vitesse en pixels par frame
        self.path = File()
        self.next_cell = None
        self.target_pos = None

    def get_current_cell(self):
        """Retourne la cellule actuelle de la fourmi"""
        return self.colony.grid.pixel_to_cell(int(self.pos.x), int(self.pos.y))

    def is_static(self):
        """Vérifie si la fourmi est immobile"""
        return self.next_cell is None and self.path.est_vide()

    def update(self):
        """Met à jour la position et l'animation de la fourmi"""

        # Pathfinding
        # Si pas de prochaine cellule et qu'il reste du chemin, charger la suivante
        if self.next_cell is None and not self.path.est_vide():
            self.next_cell = self.path.defiler()
            # Calculer la position cible en pixels (centre de la cellule)
            cell_x, cell_y = self.next_cell
            pixel_x, pixel_y = self.colony.grid.cell_to_pixel(cell_x, cell_y)
            # Ajouter le décalage pour atteindre le centre de la cellule
            self.target_pos = pygame.Vector2(
                pixel_x + self.colony.grid.CELL_SIZE / 2,
                pixel_y + self.colony.grid.CELL_SIZE / 2 + self.colony.grid.start_y,
            )

        # Si pas de cellule cible, la fourmi est immobile
        if self.next_cell is None:
            self.direction = pygame.Vector2(0, 0)
            return

        # === DÉPLACEMENT VERS LA CIBLE ===
        if self.target_pos is not None:
            # Calculer le vecteur vers la position cible
            direction_to_target = self.target_pos - self.pos
            distance_to_target = direction_to_target.length()

            # Si on est arrivé à la cible
            if distance_to_target < self.speed:
                # Placer exactement sur la cible
                self.pos = self.target_pos.copy()
                # Réinitialiser pour charger la prochaine cellule
                self.next_cell = None
                self.target_pos = None
                self.direction = pygame.Vector2(0, 0)
            else:
                # Normaliser la direction et appliquer la vitesse
                self.direction = direction_to_target.normalize()
                self.pos += self.direction * self.speed

                # Mettre à jour la direction du sprite
                self.flip = self.direction.x < 0  # Vx < 0 => vers la gauche

        if self.rect is not None:
            self.rect.center = (int(self.pos.x), int(self.pos.y))

        # Animation
        if not self.is_static():
            animation_cooldown = 150
            if pygame.time.get_ticks() - self.update_time > animation_cooldown:
                self.frame_index += 1
                self.update_time = pygame.time.get_ticks()
            if self.frame_index >= len(self.frames[self.action]):
                self.frame_index = 0
            self.image = self.frames[self.action][self.frame_index]

    def draw(self):
        """Dessine la fourmi à l'écran"""
        if self.image is None:
            return
        img = pygame.transform.flip(self.image, self.flip, False)
        # Centrer l'image sur la position
        draw_pos = (
            int(self.pos.x - img.get_width() / 2),
            int(self.pos.y - img.get_height() / 2),
        )
        self.colony.world.blit(img, draw_pos)
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

    def set_path(self, path):
        """Définit un nouveau chemin pour la fourmi"""
        # Vider le chemin actuel
        self.path = File()
        # Ajouter les nouvelles cellules
        for node in path:
            self.path.enfiler(node)
        # Réinitialiser l'état de déplacement
        self.next_cell = None
        self.target_pos = None

    def move_to(self, target_cell_x, target_cell_y):
        """Calcule et définit un chemin vers une cellule cible"""
        current_cell = self.get_current_cell()
        path = self.colony.grid.a_star(current_cell, (target_cell_x, target_cell_y))
        if path:
            self.set_path(path)
            return True
        return False

    def stop(self):
        """Arrête le mouvement de la fourmi"""
        self.path = File()
        self.next_cell = None
        self.target_pos = None
        self.direction = pygame.Vector2(0, 0)
