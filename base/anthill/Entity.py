xp_per_levels = {
    i: i*100 for i in range(100)
}

class Entity:
    
    def __init__ (self):
        self.x = 0
        self.y = 0
        
        self.model = None
        self.orientation = 0 # angle d'orientation de la fourmi
        
        self.strength = 1
        self.alive = True
        self.health = 10*self.strength
        
        self.last_fed_at = 0
        self.last_slept_at = 0
        
        self.xp = 0
        self.level = 1
        
        self.agressive = False
        self.role = "worker"
        
    def add_xp (self, xp):
        new_xp = self.xp + xp
        self.xp = new_xp
        req_xp = xp_per_levels[self.level+1]
        if self.xp >= req_xp:
            self.level += 1
            self.xp = 0
            self.add_xp(req_xp-new_xp)
        
    def update (self, events):
        pass
        
    def draw (self):
        pass