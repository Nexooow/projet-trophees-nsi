class Entity:
    
    def __init__ (self):
        self.x = 0
        self.y = 0
        
        self.model = None
        self.orientation = 0 # angle d'orientation de la fourmi
        
        self.strength = 1
        self.alive = True
        self.health = 10*self.strength
        
        self.agressive = False
        
    def update (self, events):
        pass
        
    def draw (self):
        pass