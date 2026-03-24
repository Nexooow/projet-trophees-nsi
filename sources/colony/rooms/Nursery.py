from colony.ants.Nurse import Nurse
from colony.ants.Worker import Worker
from colony.ants.Scientist import Scientist
from colony.Room import Room
from constants import QUEEN_LARVAS, UIColors
from lib.ui import Label, ProgressBar

PADDING = 6
GAP = 6
TITLE_HEIGHT = 36
TITLE_FONT_SIZE = 42

# Durées d'incubation en frames (on utilise TimeManager.now(), qui counts frames).
# On prend le time (seconds) from QUEEN_LARVAS and convert to frames by *60
TIMES = {k: max(1, v.get("time", 0) * 60) for k, v in QUEEN_LARVAS.items()}


class Nursery(Room):
    def __init__(self, colony, data):
        super().__init__(
            colony,
            "nursery",
            {**data, "walkable": []},
        )

        # Liste des tuples (ant_type, start_time_frames)
        self.larvaes = []

        self.recent_deliveries = set()

    def update_self(self, events):
        for ant in list(self.colony.ants):
            if not isinstance(ant, Worker):
                continue
            task_data = getattr(ant, "task_data", None)
            current_task = (
                ant.get_current_task() if hasattr(ant, "get_current_task") else None
            )

            if (
                task_data is not None
                and current_task is not None
                and current_task.type == "deliver_larva"
                and self.rect is not None
                and self.rect.collidepoint(ant.pos.x, ant.pos.y)
            ):
                # Eviter de traiter plusieurs fois la même fourmi dans la même frame
                if ant.id in self.recent_deliveries:
                    continue
                # On enregistre la larve dans la nurserie
                self.assign_larvae(task_data)
                # Marquer pour éviter duplication
                self.recent_deliveries.add(ant.id)

        self.recent_deliveries = {
            wid
            for wid in self.recent_deliveries
            if any(
                a.id == wid
                and self.rect is not None
                and self.rect.collidepoint(a.pos.x, a.pos.y)
                for a in self.colony.ants
            )
        }

        if not self.larvaes:
            return

        now = self.game.time.now()
        hatched = []
        remaining = []
        for ant_type, start in self.larvaes:
            # Défaut : si le type inconnu, on hatch en tant qu'ouvrière
            required = TIMES.get(ant_type, TIMES.get("worker", 60 * 30))
            time_since_start = now - start
            if time_since_start >= required:
                hatched.append(ant_type)
            else:
                remaining.append((ant_type, start))

        self.larvaes = remaining
        for ant_type in hatched:
            ANT_CLASS_MAP = {"nurse": Nurse, "worker": Worker, "scientist": Scientist}
            ant_class = ANT_CLASS_MAP.get(ant_type, Worker)
            entry = self.get_passable_entry() or self.get_entry()
            data = {"power": 1, "xp": 0}
            new_ant = ant_class(self.colony, data, entry)
            self.colony.ants.append(new_ant)

    def assign_larvae(self, larvae_type):
        """
        Ajoute une larve à la file d'incubation de la nurserie, avec le timestamp
        actuel (TimeManager.now() retourne des "frames" / ticks).
        """
        # On enregistre le temps de dépôt en frames
        start = self.colony.game.time.now()
        self.larvaes.append((larvae_type, start))
        if self.colony.sidebar and self.colony.sidebar.main_panel.visible:
            self.update_ui()
        return start

    def update_ui(self):
        """
        Met à jour dynamiquement les labels et barres de progression de la nurserie
        si l'interface est visible (pour un retour visuel en temps réel).
        """
        if not (self.colony.sidebar and self.colony.sidebar.main_panel.visible):
            return

        ui = self.colony.ui

        for i, (ant_type, start) in enumerate(self.larvaes):
            # Calcul du ratio et du temps restant
            total_required = TIMES.get(ant_type, TIMES.get("worker", 60 * 30))
            elapsed = max(0, self.colony.game.time.now() - start)
            remaining = max(0, total_required - elapsed)
            seconds_remaining = int(remaining // 60)
            frac = (
                min(1.0, float(elapsed) / float(total_required))
                if total_required > 0
                else 1.0
            )

            # Label
            label = ui.get(f"nursery_item_label_{i}")
            if label is not None and isinstance(label, Label):
                try:
                    label.set_text(f"{i + 1} {ant_type} - {seconds_remaining}s")
                except Exception:
                    # Certains labels peuvent ne pas implémenter set_text dans des mocks/tests
                    pass

            # Progress bar
            pb = ui.get(f"nursery_item_pb_{i}")
            if isinstance(pb, ProgressBar):
                try:
                    pb.set_value(frac)
                except Exception:
                    pass

    def interact(self):
        """
        Construit une interface interactive pour la nurserie :
        - liste scrollable des larves en incubation
        - barre de progression pour chaque larve
        """
        sidebar = self.colony.sidebar
        assert sidebar is not None

        panel_w = sidebar.width
        panel_h = sidebar.height
        inner_w = panel_w - PADDING * 2

        y_title = PADDING
        y_tabs = y_title + TITLE_HEIGHT + GAP

        ui = self.colony.ui
        root = (
            ui.panel(
                "nursery_root",
                (0, 0, panel_w, panel_h),
            )
            .set_border(None, 0)
            .set_bg_color(UIColors.BG_DARK)
        )

        root.add_child(
            ui.label(
                "nursery_title",
                "Nurserie",
                (PADDING, y_title, inner_w, TITLE_HEIGHT),
            )
            .set_font_size(TITLE_FONT_SIZE)
            .set_align("center", "center")
        )

        # Zone scrollable listant les larves en incubation
        scroll_y = y_tabs + GAP
        scroll_h = panel_h - scroll_y - PADDING
        scroll = ui.scrollable_panel(
            "nursery_scroll", (PADDING, scroll_y, inner_w, scroll_h)
        )

        item_h = 48
        gap_item = 6

        for i, (ant_type, start) in enumerate(self.larvaes):
            y = i * (item_h + gap_item) + PADDING

            # Calculs temps
            total_required = TIMES.get(ant_type, TIMES.get("worker", 60 * 30))
            elapsed = max(0, self.colony.game.time.now() - start)
            frac = float(elapsed) / float(total_required) if total_required > 0 else 1.0
            frac = min(1.0, max(0.0, frac))

            label = ui.label(
                f"nursery_item_label_{i}",
                f"{i + 1}. {ant_type}",
                (PADDING, y, inner_w // 3, item_h),
            )
            label.set_align("left", "center").set_font_size(18)
            scroll.add_child(label)

            bar_x = PADDING + inner_w // 3 + GAP
            bar_w = inner_w - (inner_w // 3) - PADDING - GAP
            pb = ui.progress_bar(f"nursery_item_pb_{i}", (bar_x, y + 12, bar_w, 20))
            pb.set_value(frac).set_show_text(False)
            scroll.add_child(pb)

        content_height = len(self.larvaes) * (item_h + gap_item) + PADDING
        scroll.set_content_height(content_height)

        root.add_child(scroll)

        sidebar.set_content(root)
        sidebar.show()
