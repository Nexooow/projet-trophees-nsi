
class Unit:
    def __init__(self, x, y, image, team,power=1,points=5,diagonal=False):
        self.x = x
        self.y = y
        self.team=team
        self.image = pygame.transform.scale(image, (50,50))
        self.points_max = points
        self.points = points
        self.orientation = False
        self.diagonal=diagonal
        self.power=power
        self.alive=True
    def tile(self):
        return self.x, self.y
    def attack(self,target,units):
        target.alive=False
        units.remove(target)
        
    def reset_turn(self):
        self.points = self.points_max

    def move_to(self, x, y):
        self.x = x
        self.y = y
    
    def draw(self, screen):
        img = pygame.transform.flip(self.image, False, self.orientation)
        screen.blit(img, (self.x*50, self.y*50))