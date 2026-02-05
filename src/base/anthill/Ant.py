from .Entity import Entity

xp_per_levels = {
    i: i*100 for i in range(100)
}

class Ant (Entity):
    
    def __init__ (self):
        super().__init__()
        self.last_fed_at = 0
        self.last_slept_at = 0
        
        self.xp = 0
        self.age = 1
        self.role = "worker"
    
    def add_xp (self, xp):
        new_xp = self.xp + xp
        self.xp = new_xp
        req_xp = xp_per_levels[self.age+1]
        if self.xp >= req_xp:
            self.age += 1
            self.xp = 0
            self.add_xp(new_xp-req_xp)