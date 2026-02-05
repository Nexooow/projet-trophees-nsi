class TimeManager:
    
    def __init__ (self):
        self.time = 0
        self.paused = True
    
    def is_paused (self):
        return self.paused
        
    def set_pause (self, boolean=True):
        self.paused = boolean
        
    def get_time (self):
        return divmod(self.time, 60)
        
    def is_day(self) -> bool:
        return 8 < self.get_time()[0] < 20 
        