class TimeManager:
    
    def __init__ (self, game):
        self.game = game
        self.paused = True
        self.time = 0
        self.sub_frame_count = 0
    
    def is_paused (self):
        """
        Renvoie si le temps est actuellement en pause ou non.
        """
        return self.paused
        
    def set_pause (self, boolean=True):
        """
        Met en pause ou reprend le temps.
        """
        self.paused = boolean
        
    def get_time (self):
        """
        Renvoie le temps actuel sous la forme d'un tuple (heures, minutes).
        """
        return divmod(self.time, 60)

    def set_time (self, time: int):
        """
        Définit le temps actuel en minutes.
        """
        self.time = time
        
    def is_day(self) -> bool:
        """
        Renvoie si c'est actuellement le jour ou la nuit.
        """
        return 8 < self.get_time()[0] < 20

    def update (self):
        """
        Met à jour le temps.
        """
        if not self.paused:
            self.sub_frame_count += 1
            if self.sub_frame_count >= 60:
                self.time += 1
                self.sub_frame_count = 0
        