from __future__ import annotations

from colony.Room import Room
from constants import (
    QUEEN_LARVAS,
    QUEEN_MAX_LARVAE,
    QUEEN_UPGRADES,
    UIColors,
)
from lib.file import File
from lib.ui.button import Button

QUEEN_MAX_HP = 100
QUEEN_LOW_FOOD_THRESHOLD = 20

PADDING = 6
GAP = 6
TITLE_HEIGHT = 36
TITLE_FONT_SIZE = 42
TAB_HEIGHT = 28
TAB_FONT_SIZE = 22
SECTION_HEIGHT = 18
LARVAE_ITEM_HEIGHT = 52
LARVAE_BAR_HEIGHT = 12
SCROLL_ITEM_HEIGHT = 100
ITEM_GAP = 8
BTN_HEIGHT = 26
BTN_WIDTH = 110


class Queen(Room):
    ENTRY_OFFSET_X_RATIO = 0.0
    ENTRY_OFFSET_Y_RATIO = 0.5

    def __init__(self, colony, data: dict):
        width_px = data["width"] * 8
        height_px = data["height"] * 8
        entry_offset = (
            int(width_px * self.ENTRY_OFFSET_X_RATIO),
            int(height_px * self.ENTRY_OFFSET_Y_RATIO),
        )
        super().__init__(
            colony,
            "queen",
            {**data, "walkable": [], "entry_offset": entry_offset},
        )

        self.max_hp: int = QUEEN_MAX_HP
        self.hp: int = QUEEN_MAX_HP

        self.feed_interval: int = 60
        self.feed_time: int = 25

        self.born_queue = File()
        self.current_born = None  # (type_fourmi, temps_restant)

        # Onglet actif : "production" | "upgrades"
        self.active_tab: str = "production"

        # Niveaux d'amélioration déjà achetés (clé = id amélioration).
        # Pour les améliorations sans niveaux : 0 = non débloquée, 1 = débloquée.
        self.upgrade_levels: dict[str, int] = {k: 0 for k in QUEEN_UPGRADES}

        # Nombre max de slots de larves (peut croître avec l'upgrade "larvae_slots")
        self.max_larvae: int = QUEEN_MAX_LARVAE

        # Timer de production de larves en frames (60 frames = 1 seconde).
        # Représente le temps écoulé sur la larve actuellement en tête de file.
        self.larvae_timer: int = 0

    def update_self(self, events):
        if self.game.time.every(minutes=self.feed_interval):
            #self.colony.tasks.add_task(
            #    "feed_queen",
            #    data={"deadline": self.feed_time},
            #    on_expired=self.on_queen_starved,
            #)
            pass # TODO: fix 

        self.update_larvae_production()

    def update_larvae_production(self):
        """
        Fait avancer le timer de production de la première larve en file.
        Quand le timer atteint la durée totale, la fourmi est créée et
        retirée de la file.
        """
        if self.born_queue.est_vide():
            self.larvae_timer = 0
            return

        # Ne pas avancer pendant la pause
        if self.game.time.is_paused():
            return

        ant_type = self.born_queue.sommet()
        ant_data = QUEEN_LARVAS.get(ant_type, {})
        total_frames = ant_data.get("time", 30) * 60

        # Appliquer le bonus de vitesse de naissance si l'amélioration est achetée
        birth_speed_lvl = self.upgrade_levels.get("birth_speed", 0)
        if birth_speed_lvl > 0:
            # Chaque niveau réduit le temps de 10 %
            reduction = 1.0 - 0.10 * birth_speed_lvl
            total_frames = max(1, int(total_frames * reduction))

        self.larvae_timer += 1

        if self.larvae_timer >= total_frames:
            
            print("naissance")

            self.born_queue.defiler()
            self.larvae_timer = 0
            self.spawn_ant(ant_type)

            # Reconstruire le menu si la sidebar est ouverte sur la reine
            if self.colony.sidebar and self.colony.sidebar.main_panel.visible:
                self.interact()

    def spawn_ant(self, ant_type: str):
        """
        Émet une tâche 'deliver_larva' pour qu'une ouvrière récupère
        la larve ici et la transporte jusqu'à la nurserie.
        """
        nursery = self.colony.get_room("nursery")
        if nursery is None:
            return
        
        print("fourmi envoyée")

        queen_entry = self.get_passable_entry()
        nursery_entry = nursery.get_passable_entry()
            
        if queen_entry is None or nursery_entry is None:
            return

        queen_cx, queen_cy = queen_entry
        nursery_cx, nursery_cy = nursery_entry

        self.colony.tasks.add_task(
            "deliver_larva",
            data={
                "ant_type": ant_type,
                "pickup_pos": (queen_cx, queen_cy),
                "delivery_pos": (nursery_cx, nursery_cy),
            },
        )

    def interact(self):
        sidebar = self.colony.sidebar
        assert sidebar is not None

        panel_w = sidebar.width
        panel_h = sidebar.height
        inner_w = panel_w - PADDING * 2

        larvae_section_h = (
            SECTION_HEIGHT
            + PADDING * 2
            + self.max_larvae * (LARVAE_ITEM_HEIGHT + GAP)
            - GAP
        )

        y_title = PADDING
        y_tabs = y_title + TITLE_HEIGHT + GAP
        y_scroll = y_tabs + TAB_HEIGHT + GAP
        scroll_h = panel_h - y_scroll - GAP - larvae_section_h - PADDING
        y_larvae = y_scroll + scroll_h + GAP

        tab_w = (inner_w - GAP) // 2

        ui = self.colony.ui
        root = (
            ui.panel(
                "queen_root",
                (0, 0, panel_w, panel_h),
            )
            .set_border(None, 0)
            .set_bg_color(UIColors.BG_DARK)
        )

        root.add_child(
            ui.label(
                "queen_title",
                "Reine",
                (PADDING, y_title, inner_w, TITLE_HEIGHT),
            )
            .set_font_size(TITLE_FONT_SIZE)
            .set_align("center", "center")
        )

        root.add_child(
            self.make_tab_btn(
                "queen_tab_prod",
                "Production",
                PADDING,
                y_tabs,
                tab_w,
                TAB_HEIGHT,
                "production",
            )
        )
        root.add_child(
            self.make_tab_btn(
                "queen_tab_upgr",
                "Améliorations",
                PADDING + tab_w + GAP,
                y_tabs,
                tab_w,
                TAB_HEIGHT,
                "upgrades",
            )
        )

        scroll = ui.scrollable_panel(
            "queen_scroll",
            (PADDING, y_scroll, inner_w, scroll_h),
        )
        self.fill_scroll(scroll, inner_w)
        root.add_child(scroll)

        root.add_child(self.make_larvae_section(inner_w, y_larvae, larvae_section_h))

        sidebar.set_content(root)
        sidebar.show()

    def make_tab_btn(self, id, text, x, y, w, h, tab_id) -> Button:
        """Crée un bouton d'onglet avec un visuel actif/inactif."""
        ui = self.colony.ui
        btn: Button = ui.button(id, text, (x, y, w, h))
        btn.set_font_size(TAB_FONT_SIZE)
        if self.active_tab == tab_id:
            btn.set_colors(normal=UIColors.BG, hover=UIColors.BG_HOVER)
        btn.on("click", lambda t=tab_id: self.switch_tab(t))
        return btn

    def switch_tab(self, tab_id: str):
        """Change l'onglet actif et reconstruit le menu."""
        self.active_tab = tab_id
        self.interact()

    def fill_scroll(self, scroll, inner_w):
        """Ajoute les cartes correspondant à l'onglet actif dans le scroll."""
        if self.active_tab == "production":
            self.fill_production(scroll, inner_w)
        else:
            self.fill_upgrades(scroll, inner_w)

    def fill_production(self, scroll, inner_w):
        ui = self.colony.ui
        card_w = inner_w - PADDING * 2

        name_h = 32
        stat_h = 24
        btn_y = SCROLL_ITEM_HEIGHT - PADDING - BTN_HEIGHT
        stat_w = (card_w - PADDING * 2 - GAP) // 2

        for i, (ant_type, data) in enumerate(QUEEN_LARVAS.items()):
            y_card = i * (SCROLL_ITEM_HEIGHT + ITEM_GAP) + PADDING

            card = (
                ui.panel(
                    f"queen_prod_card_{ant_type}",
                    (PADDING, y_card, card_w, SCROLL_ITEM_HEIGHT),
                )
                .set_bg_color(UIColors.BG)
                .set_border(UIColors.BORDER, 1)
            )

            card.add_child(
                ui.label(
                    f"queen_prod_name_{ant_type}",
                    data["label"],
                    (PADDING, PADDING, card_w - PADDING * 2, name_h),
                )
                .set_font_size(26)
                .set_align("left", "center")
            )

            stat_y = PADDING + name_h + GAP

            card.add_child(
                ui.label(
                    f"queen_prod_cost_{ant_type}",
                    f"{data['cost']} nourriture",
                    (PADDING, stat_y, stat_w, stat_h),
                )
                .set_font_size(18)
                .set_align("left", "center")
                .set_text_color(UIColors.FILLED_BAR)
            )

            card.add_child(
                ui.label(
                    f"queen_prod_time_{ant_type}",
                    f"{data['time']} s",
                    (PADDING + stat_w + GAP, stat_y, stat_w, stat_h),
                )
                .set_font_size(18)
                .set_align("left", "center")
                .set_text_color(UIColors.TEXT)
            )

            can_produce = (
                len(self.born_queue.content) < self.max_larvae
                and self.colony.food >= data["cost"]
            )
            btn: Button = ui.button(
                f"queen_prod_btn_{ant_type}",
                "Produire",
                (PADDING, btn_y, BTN_WIDTH, BTN_HEIGHT),
            )
            btn.set_font_size(18)
            if can_produce:
                btn.on("click", lambda t=ant_type: self.enqueue_larva(t))
            else:
                btn.set_enabled(False)

            card.add_child(btn)
            scroll.add_child(card)

    def is_upgradable(self, upg_id: str) -> bool:
        """
        Retourne True si l'amélioration possède des niveaux (liste non vide),
        False si c'est un simple déverrouillage.
        """
        return bool(QUEEN_UPGRADES[upg_id].get("levels"))

    def fill_upgrades(self, scroll, inner_w):
        """
        Ajoute les cartes d'amélioration dans le scroll.
        """
        ui = self.colony.ui

        card_w = inner_w - PADDING * 2
        name_h = 32
        effect_h = 22
        btn_y = SCROLL_ITEM_HEIGHT - PADDING - BTN_HEIGHT
        lvl_badge_w = 90

        for i, (upg_id, data) in enumerate(QUEEN_UPGRADES.items()):
            y_card = i * (SCROLL_ITEM_HEIGHT + ITEM_GAP) + PADDING
            current_lvl = self.upgrade_levels.get(upg_id, 0)
            is_upgradable = self.is_upgradable(upg_id)
            name_w = card_w - PADDING * 2 - lvl_badge_w - GAP
            effect_y = PADDING + name_h + GAP

            if is_upgradable:
                max_lvl = len(data["levels"])
                maxed_out = current_lvl >= max_lvl
                lvl_text = "Max" if maxed_out else f"niv. {current_lvl} / {max_lvl}"
                lvl_color = UIColors.GREEN if maxed_out else UIColors.FILLED_BAR
            else:
                # Amélioration à déverrouillage unique
                maxed_out = current_lvl >= 1  # 1 = débloquée
                lvl_text = "Débloquée" if maxed_out else "Verrouillée"
                lvl_color = UIColors.GREEN if maxed_out else UIColors.TEXT_DISABLED

            card = (
                ui.panel(
                    f"queen_upg_card_{upg_id}",
                    (PADDING, y_card, card_w, SCROLL_ITEM_HEIGHT),
                )
                .set_bg_color(UIColors.BG)
                .set_border(UIColors.BORDER, 1)
            )

            card.add_child(
                ui.label(
                    f"queen_upg_name_{upg_id}",
                    data["label"],
                    (PADDING, PADDING, name_w, name_h),
                )
                .set_font_size(24)
                .set_align("left", "center")
            )

            card.add_child(
                ui.label(
                    f"queen_upg_lvl_{upg_id}",
                    lvl_text,
                    (PADDING + name_w + GAP, PADDING, lvl_badge_w, name_h),
                )
                .set_font_size(16)
                .set_align("right", "center")
                .set_text_color(lvl_color)
            )

            if not maxed_out:
                if is_upgradable:
                    next_effect = data["levels"][current_lvl]["effect"]
                    effect_text = f"Prochain : {next_effect}"
                else:
                    effect_text = data.get("description", "")
                effect_color = UIColors.TEXT
            else:
                if is_upgradable:
                    effect_text = "Niveau maximum atteint"
                else:
                    effect_text = data.get("description", "Amélioration active")
                effect_color = UIColors.TEXT_DISABLED

            card.add_child(
                ui.label(
                    f"queen_upg_effect_{upg_id}",
                    effect_text,
                    (PADDING, effect_y, card_w - PADDING * 2, effect_h),
                )
                .set_font_size(17)
                .set_align("left", "center")
                .set_text_color(effect_color)
            )

            if not maxed_out:
                if is_upgradable:
                    next_cost = data["levels"][current_lvl]["cost"]
                else:
                    next_cost = data.get("cost", 0)

                btn_label = f"{next_cost} nourr." if next_cost > 0 else "Débloquer"
                btn: Button = ui.button(
                    f"queen_upg_btn_{upg_id}",
                    btn_label,
                    (PADDING, btn_y, BTN_WIDTH, BTN_HEIGHT),
                )
                btn.set_font_size(17)
                if self.colony.food >= next_cost:
                    btn.on("click", lambda uid=upg_id: self.buy_upgrade(uid))
                else:
                    btn.set_enabled(False)
            else:
                btn = ui.button(
                    f"queen_upg_btn_{upg_id}",
                    "Max" if is_upgradable else "✓",
                    (PADDING, btn_y, BTN_WIDTH, BTN_HEIGHT),
                )
                btn.set_font_size(17)
                btn.set_enabled(False)

            card.add_child(btn)
            scroll.add_child(card)

    def make_larvae_section(self, inner_w, y, h):
        """
        Affiche les larves en file d'attente avec la progression de la première.
        """
        ui = self.colony.ui

        queued = [item for (item, _) in self.born_queue.content]
        nb_filled = len(queued)

        section = (
            ui.panel(
                "queen_larvae_section",
                (PADDING, y, inner_w, h),
            )
            .set_bg_color(UIColors.BG)
            .set_border(UIColors.BORDER, 1)
        )

        section.add_child(
            ui.label(
                "queen_larvae_title",
                f"En production  ({nb_filled} / {self.max_larvae})",
                (PADDING, PADDING, inner_w - PADDING * 2, SECTION_HEIGHT),
            )
            .set_font_size(20)
            .set_align("left", "center")
            .set_text_color(UIColors.TEXT)
        )

        slot_w = inner_w - PADDING * 2
        label_h = LARVAE_ITEM_HEIGHT - LARVAE_BAR_HEIGHT - GAP - PADDING
        

        for idx in range(self.max_larvae):
            slot_y = PADDING + SECTION_HEIGHT + GAP + idx * (LARVAE_ITEM_HEIGHT + GAP)
            filled = idx < nb_filled
            
            print(filled, idx)

            slot = (
                ui.panel(
                    f"queen_larva_slot_{idx}",
                    (PADDING, slot_y, slot_w, LARVAE_ITEM_HEIGHT),
                )
                .set_border(UIColors.BORDER, 1)
                .set_bg_color(UIColors.BG_HOVER if filled else UIColors.BG_DARK)
            )

            if filled:
                ant_type = queued[idx]
                ant_data = QUEEN_LARVAS.get(ant_type, {})
                label_text = ant_data.get("label", ant_type)

                # Calcul du temps total (en tenant compte de l'accélération)
                total_seconds = ant_data.get("time", 30)
                birth_speed_lvl = self.upgrade_levels.get("birth_speed", 0)
                if birth_speed_lvl > 0:
                    reduction = 1.0 - 0.10 * birth_speed_lvl
                    total_seconds = max(1, int(total_seconds * reduction))
                total_frames = total_seconds * 60

                # Progression uniquement pour la larve en tête de file (idx == 0)
                if idx == 0 and total_frames > 0:
                    progress = min(1.0, self.larvae_timer / total_frames)
                    # Temps restant en secondes
                    remaining_frames = max(0, total_frames - self.larvae_timer)
                    remaining_s = remaining_frames // 60
                    time_text = f"{remaining_s} s"
                else:
                    progress = 0.0
                    time_text = f"{total_seconds} s"

                slot.add_child(
                    ui.label(
                        f"queen_larva_name_{idx}",
                        label_text,
                        (PADDING, PADDING, slot_w - PADDING * 2, label_h),
                    )
                    .set_font_size(19)
                    .set_align("left", "center")
                )
                slot.add_child(
                    ui.label(
                        f"queen_larva_time_{idx}",
                        time_text,
                        (PADDING, PADDING, slot_w - PADDING * 2, label_h),
                    )
                    .set_font_size(17)
                    .set_align("right", "center")
                    .set_text_color(UIColors.TEXT)
                )

                bar_y = PADDING + label_h + GAP
                slot.add_child(
                    ui.progress_bar(
                        f"queen_larva_bar_{idx}",
                        (PADDING, bar_y, slot_w - PADDING * 2, LARVAE_BAR_HEIGHT),
                    ).set_value(progress)
                )
            else:
                slot.add_child(
                    ui.label(
                        f"queen_larva_empty_{idx}",
                        "Vide",
                        (0, 0, slot_w, LARVAE_ITEM_HEIGHT),
                    )
                    .set_font_size(18)
                    .set_align("center", "center")
                    .set_text_color(UIColors.TEXT_DISABLED)
                )

            section.add_child(slot)

        return section

    def enqueue_larva(self, ant_type: str):
        """
        Ajoute une larve dans la file si un slot est disponible et que
        la colonie a assez de nourriture.
        """
        data = QUEEN_LARVAS.get(ant_type, {})
        cost = data.get("cost", 0)

        if len(self.born_queue.content) >= self.max_larvae:
            return
        if self.colony.food < cost:
            return

        self.colony.food -= cost
        self.born_queue.enfiler(ant_type)
        self.interact()

    def buy_upgrade(self, upg_id: str):
        """
        Achète le prochain niveau d'une amélioration (avec ou sans niveaux).
        """
        data = QUEEN_UPGRADES[upg_id]
        current_lvl = self.upgrade_levels.get(upg_id, 0)
        is_levelable = self.is_upgradable(upg_id)

        if is_levelable:
            max_lvl = len(data["levels"])
            if current_lvl >= max_lvl:
                return
            cost = data["levels"][current_lvl]["cost"]
        else:
            # Amélioration à déverrouillage unique
            if current_lvl >= 1:
                return
            cost = data.get("cost", 0)

        if self.colony.food < cost:
            return

        self.colony.food -= cost
        self.upgrade_levels[upg_id] = current_lvl + 1

        # Effets spéciaux des améliorations
        self.apply_upgrade_effect(upg_id, current_lvl + 1)

        self.interact()

    def apply_upgrade_effect(self, upg_id: str, new_level: int):
        """Applique l'effet secondaire d'une amélioration après achat."""
        if upg_id == "larvae_slots":
            self.max_larvae += 1
        # D'autres effets pourront être ajoutés ici selon l'upg_id

    def on_queen_starved(self):
        self.hp -= 10
        if self.hp <= 0:
            self.game.trigger_game_over("queen_starved")
