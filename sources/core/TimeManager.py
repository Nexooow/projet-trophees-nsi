ACCEL = 1  # variable utilisée pour des tests/debug pour accéler le temps


class TimeManager:
    def __init__(self, game):
        self.game = game
        self.paused = False

        self.year = 1
        self.season = 1
        self.day = 1

        self.time = 60 * 12
        self.time_since_start = 0
        self.sub_frame_count = 0

    def now(self):
        return self.time_since_start

    def is_paused(self):
        """
        Renvoie si le temps est actuellement en pause ou non.
        L'état de pause est géré globalement via StateManager (flag 'pause').
        On garde une rétrocompatibilité locale si le state manager n'est pas disponible.
        """
        try:
            return self.game.state.is_flag_active("pause")
        except Exception:
            return self.paused

    def set_pause(self, paused: bool):
        """
        Définit si le temps est en pause ou non.
        Utilise StateManager.set_flag('pause', paused) pour propager le flag globalement.
        En cas d'échec, on met à jour l'attribut local pour compatibilité.
        """
        try:
            self.game.state.set_flag("pause", paused)
        except Exception:
            self.paused = paused

    def get_time(self, offset=0):
        """
        Renvoie le temps actuel sous la forme d'un tuple (heures, minutes).
        """
        return divmod(self.time + offset, 60)

    def format(self):
        t = self.get_time()
        return f"{t[0]:02d}:{t[1]:02d} | Jour {self.day}"

    def set_time(self, time: int):
        """
        Définit le temps actuel en minutes.
        """
        self.time = time

    def every(self, hours=None, minutes=None):
        """
        Renvoie si le temps actuel est divisible par l'intervalle spécifié.
        Vérifie également si le jeu est en pause pour éviter les répétitions infinies.
        """
        if hours is not None and minutes is not None:
            return self.time % (hours * 60 + minutes) == 0 and not self.is_paused()
        elif hours is not None:
            return self.time % (hours * 60) == 0 and not self.is_paused()
        elif minutes is not None:
            return self.time % minutes == 0 and not self.is_paused()
        else:
            return False

    def time_until(self, hour, minute):
        """
        Renvoie le temps restant en minutes jusqu'à l'heure et la minute spécifiées.
        """
        current_hour, current_minute = self.get_time()
        target_time = hour * 60 + minute
        current_time = current_hour * 60 + current_minute
        return max(0, target_time - current_time)

    def is_day(self) -> bool:
        """
        Renvoie si c'est actuellement le jour ou la nuit.
        """
        return 8 < self.get_time()[0] < 20
    
    def handle_calendar(self):
        if self.day == 30:
            self.season += 1
            if self.season > 4:
                self.year += 1
        

    def add_frame(self):
        """
        Met à jour le temps.
        Sauvegarde automatiquement la partie toutes les heures en jeu.
        """
        if not self.is_paused():
            add = 1 * ACCEL
            self.time_since_start += add
            self.sub_frame_count += add
            if self.sub_frame_count >= 60:
                self.time += 1
                self.sub_frame_count = 0
                if self.time % 60 == 0:
                    try:
                        self.game.sauvegarder()
                    except Exception:
                        pass
            h, _ = self.get_time()
            if h >= 24:
                self.time = 0
                self.day += 1
