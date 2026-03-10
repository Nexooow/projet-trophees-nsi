import datetime

import pygame

from constants import GAME_NAME, UIColors

from .State import State

# ── Dimensions communes ────────────────────────────────────────────────────────
BTN_W, BTN_H = 260, 52
SPACING = BTN_H + 16
PANEL_PADDING = 32

# ── Palette du sous-menu sauvegardes ──────────────────────────────────────────
SAVE_CARD_H = 72
SAVE_CARD_GAP = 8
SAVE_CARD_PADDING = 12

SAVES_PANEL_W = 560
SAVES_TITLE_H = 48
SAVES_BACK_H = 44
SAVES_VERTICAL_MARGIN = 80  # marge totale réservée en haut et en bas de l'écran


class MenuState(State):
    def __init__(self, state_manager):
        super().__init__(state_manager, "menu", ["pause"])
        # "main" | "saves"
        self.view: str = "main"

    def enable(self):
        self.build_background_labels()
        self.show_view(self.view)

    def disable(self):
        self.view = "main"
        self.ui.clear()

    def update(self, events):
        self.ui.update(events)

    def draw(self):
        self.game.screen.fill("#28192f")
        line_y = self.game.height // 6 + 135
        pygame.draw.line(
            self.game.screen,
            UIColors.BORDER,
            (self.game.width // 2 - 140, line_y),
            (self.game.width // 2 + 140, line_y),
            1,
        )

    def build_background_labels(self):
        w, h = self.game.width, self.game.height

        self.ui.label(
            "menu_title",
            GAME_NAME,
            (0, h // 6, w, 80),
        ).set_font("assets/fonts/m5x7.ttf", 96).set_text_color(UIColors.TEXT).set_align(
            "center", "center"
        )

        self.ui.label(
            "menu_subtitle",
            "Sous titre ici",
            (0, h // 6 + 90, w, 36),
        ).set_font("assets/fonts/m5x7.ttf", 28).set_text_color(
            (180, 160, 130)
        ).set_align("center", "center")

    def show_view(self, view: str):
        """Détruit les panneaux de vue et reconstruit celui demandé."""
        self.destroy_view_panels()
        self.view = view
        if view == "main":
            self.build_main_panel()
        elif view == "saves":
            self.build_saves_panel()

    def destroy_view_panels(self):
        for panel_id in ("menu_main_panel", "menu_saves_panel"):
            el = self.ui.get(panel_id)
            if el is not None:
                self.remove_tree(el)

    def remove_tree(self, element):
        """Supprime récursivement un élément et tous ses descendants de ui.elements."""
        for child in list(element.children):
            self.remove_tree(child)
        element.children = []
        element.parent = None
        self.ui.remove(element.id)

    def build_main_panel(self):
        w, h = self.game.width, self.game.height

        btn_x = (w - BTN_W) // 2
        panel_y = h // 2 - 20

        btn_count = 3
        panel_h = SPACING * (btn_count - 1) + BTN_H + PANEL_PADDING * 2

        panel = self.ui.panel(
            "menu_main_panel",
            (
                btn_x - PANEL_PADDING,
                panel_y - PANEL_PADDING,
                BTN_W + PANEL_PADDING * 2,
                panel_h,
            ),
        ).set_z_index(0)

        panel.add_child(
            self.ui.button(
                "btn_new_game",
                "Nouvelle partie",
                (PANEL_PADDING, PANEL_PADDING, BTN_W, BTN_H),
            )
            .on("click", self.on_new_game)
            .set_z_index(1)
        )

        has_save = self.game.save.has_save()
        continue_btn = self.ui.button(
            "btn_continue",
            "Continuer",
            (PANEL_PADDING, PANEL_PADDING + SPACING, BTN_W, BTN_H),
        ).set_z_index(1)
        if has_save:
            continue_btn.on("click", lambda: self.show_view("saves"))
        else:
            continue_btn.set_enabled(False)
        panel.add_child(continue_btn)

        panel.add_child(
            self.ui.button(
                "btn_quit",
                "Quitter",
                (PANEL_PADDING, PANEL_PADDING + SPACING * 2, BTN_W, BTN_H),
            )
            .set_colors(
                normal=(110, 40, 40),
                hover=(150, 55, 55),
                active=(180, 65, 65),
            )
            .on("click", self.on_quit)
            .set_z_index(1)
        )

        self.ui.add(panel)

    def build_saves_panel(self):
        w, h = self.game.width, self.game.height
        saves = self.game.save.list_saves()

        saves_panel_max_h = h - SAVES_VERTICAL_MARGIN
        cards_total_h = len(saves) * (SAVE_CARD_H + SAVE_CARD_GAP) - SAVE_CARD_GAP
        scroll_h = min(
            cards_total_h,
            saves_panel_max_h - SAVES_TITLE_H - SAVES_BACK_H - PANEL_PADDING * 3,
        )
        scroll_h = max(scroll_h, SAVE_CARD_H)  # au moins une carte visible

        panel_h = (
            SAVES_TITLE_H
            + PANEL_PADDING
            + scroll_h
            + PANEL_PADDING
            + SAVES_BACK_H
            + PANEL_PADDING
        )
        panel_x = (w - SAVES_PANEL_W) // 2
        panel_y = max(PANEL_PADDING, (h - panel_h) // 2)

        panel = (
            self.ui.panel(
                "menu_saves_panel",
                (panel_x, panel_y, SAVES_PANEL_W, panel_h),
            )
            .set_bg_color(UIColors.BG_DARK)
            .set_border(None, 0)
            .set_z_index(2)
        )

        inner_w = SAVES_PANEL_W - PANEL_PADDING * 2

        panel.add_child(
            self.ui.label(
                "saves_title",
                "Choisir une sauvegarde",
                (PANEL_PADDING, PANEL_PADDING, inner_w, SAVES_TITLE_H),
            )
            .set_font("assets/fonts/m5x7.ttf", 36)
            .set_text_color(UIColors.TEXT)
            .set_align("center", "center")
            .set_z_index(3)
        )

        scroll_y_offset = PANEL_PADDING + SAVES_TITLE_H + PANEL_PADDING // 2

        if saves:
            scroll = (
                self.ui.scrollable_panel(
                    "saves_scroll",
                    (PANEL_PADDING, scroll_y_offset, inner_w, scroll_h),
                )
                .set_bg_color(UIColors.BG_DARK)
                .set_border(UIColors.BORDER, 1)
                .set_z_index(3)
            )
            self.fill_saves_scroll(scroll, inner_w, saves)
            panel.add_child(scroll)
        else:
            # Aucune sauvegarde (ne devrait pas arriver si has_save() == True)
            panel.add_child(
                self.ui.label(
                    "saves_empty",
                    "Aucune sauvegarde disponible.",
                    (PANEL_PADDING, scroll_y_offset, inner_w, scroll_h),
                )
                .set_font("assets/fonts/m5x7.ttf", 24)
                .set_text_color(UIColors.TEXT_DISABLED)
                .set_align("center", "center")
                .set_z_index(3)
            )

        back_y = scroll_y_offset + scroll_h + PANEL_PADDING
        back_btn_w = 160

        panel.add_child(
            self.ui.button(
                "saves_btn_back",
                "Retour",
                (PANEL_PADDING, back_y, back_btn_w, SAVES_BACK_H),
            )
            .on("click", lambda: self.show_view("main"))
            .set_z_index(3)
        )

        self.ui.add(panel)

    def fill_saves_scroll(self, scroll, inner_w, saves: list):
        """Remplit le ScrollablePanel avec une carte par sauvegarde."""
        card_w = inner_w - SAVE_CARD_PADDING * 2

        for idx, save in enumerate(saves):
            card_y = SAVE_CARD_PADDING + idx * (SAVE_CARD_H + SAVE_CARD_GAP)

            card = (
                self.ui.panel(
                    f"save_card_{idx}",
                    (SAVE_CARD_PADDING, card_y, card_w, SAVE_CARD_H),
                )
                .set_bg_color(UIColors.BG)
                .set_border(UIColors.BORDER, 1)
                .set_z_index(4)
            )

            ts = save.get("timestamp", 0)
            try:
                dt = datetime.datetime.fromtimestamp(ts)
                date_str = dt.strftime("%d/%m/%Y  %H:%M")
            except (OSError, OverflowError, ValueError):
                date_str = "Date inconnue"

            day = save.get("day", 1)
            save_id = save.get("save_id", "???")

            name_h = 28
            meta_h = 20
            name_y = (SAVE_CARD_H - name_h - meta_h - 4) // 2
            meta_y = name_y + name_h + 4

            text_w = card_w - SAVE_CARD_PADDING * 2 - 110  # laisser place au bouton

            card.add_child(
                self.ui.label(
                    f"save_card_name_{idx}",
                    f"Partie {idx + 1} - Jour {day}",
                    (SAVE_CARD_PADDING, name_y, text_w, name_h),
                )
                .set_font("assets/fonts/m5x7.ttf", 26)
                .set_text_color(UIColors.TEXT)
                .set_align("left", "center")
                .set_z_index(5)
            )

            card.add_child(
                self.ui.label(
                    f"save_card_meta_{idx}",
                    f"{date_str}",
                    (SAVE_CARD_PADDING, meta_y, text_w, meta_h),
                )
                .set_font("assets/fonts/m5x7.ttf", 16)
                .set_text_color(UIColors.TEXT_DISABLED)
                .set_align("left", "center")
                .set_z_index(5)
            )

            load_btn_w = 100
            load_btn_h = 34
            load_btn_x = card_w - SAVE_CARD_PADDING - load_btn_w
            load_btn_y = (SAVE_CARD_H - load_btn_h) // 2

            card.add_child(
                self.ui.button(
                    f"save_card_btn_{idx}",
                    "Charger",
                    (load_btn_x, load_btn_y, load_btn_w, load_btn_h),
                )
                .on("click", lambda sid=save["save_id"]: self.load_save(sid))
                .set_z_index(5)
            )

            scroll.add_child(card)

    def on_new_game(self):
        from states.ColonyState import ColonyState

        self.game.state.states_managers["colony"] = ColonyState(self.game.state)
        self.game.game_id = None
        self.game.state.set_state("colony")

    def load_save(self, save_id: str):
        """Charge une sauvegarde spécifique et bascule vers la colonie."""
        success = self.game.restaurer(save_id)
        if success:
            self.game.state.set_state("colony")
        else:
            self.show_view("main")

    def on_quit(self):
        self.game.running = False
