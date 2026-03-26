from colony.Room import Room
from constants import SCIENCE_UPGRADES
from lib.ui import Button, Label, UIColors

PADDING = 6
GAP = 6
TITLE_HEIGHT = 36
TITLE_FONT_SIZE = 42


class Laboratory(Room):
    def __init__(self, colony, data):
        super().__init__(
            colony,
            "laboratory",
            {**data, "walkable": []},
        )
        self.scientists_assigned = 0

    def update_self(self, events):
        self.scientists_assigned = 0
        for ant in self.colony.ants:
            if ant.type == "scientist":
                self.scientists_assigned += 1

        if self.scientists_assigned > 0:
            # Gain de science basé sur le nombre de scientifiques
            self.colony.science += 0.005 * self.scientists_assigned

        self.update_ui()

    def interact(self):
        sidebar = self.colony.sidebar
        assert sidebar is not None

        panel_w = sidebar.width
        panel_h = sidebar.height
        inner_w = panel_w - PADDING * 2

        ui = self.colony.ui
        root = (
            ui.panel("lab_root", (0, 0, panel_w, panel_h))
            .set_border(None, 0)
            .set_bg_color(UIColors.BG_DARK)
        )

        root.add_child(
            ui.label(
                "lab_title", "Laboratoire", (PADDING, PADDING, inner_w, TITLE_HEIGHT)
            )
            .set_font_size(TITLE_FONT_SIZE)
            .set_align("center", "center")
        )

        root.add_child(
            ui.label(
                "lab_science_display",
                f"Science : {int(self.colony.science)}",
                (PADDING, PADDING + TITLE_HEIGHT + GAP, inner_w, 30),
            )
            .set_font_size(28)
            .set_align("center", "center")
        )

        y_research = PADDING + TITLE_HEIGHT + GAP + 40
        root.add_child(
            ui.label(
                "lab_tree_title",
                "Arbre Technologique",
                (PADDING, y_research, inner_w, 30),
            )
            .set_font_size(24)
            .set_align("center", "center")
        )

        y_scroll = y_research + 30 + GAP
        scroll_h = panel_h - y_scroll - PADDING

        scroll_panel = ui.scrollable_panel(
            "lab_tree_content", (PADDING, y_scroll, inner_w, scroll_h)
        )

        self.fill_upgrades(scroll_panel, inner_w)

        root.add_child(scroll_panel)

        sidebar.set_content(root)
        sidebar.show()

    def fill_upgrades(self, scroll_panel, inner_w):
        y = 0
        height = 100

        for id, upgrade in SCIENCE_UPGRADES.items():
            elemid = f"lab_tree_upg_{id}"

            panel = (
                self.colony.ui.panel(elemid, (0, y, inner_w, height))
                .set_bg_color(UIColors.BG)
                .set_border(UIColors.BORDER, 1)
            )

            # Title
            panel.add_child(
                self.colony.ui.label(
                    elemid + "_title",
                    upgrade.get("label", id),
                    (6, 4, inner_w - 12, 24),
                )
                .set_text_color(UIColors.TEXT)
                .set_font_size(24)
            )

            # Description
            desc = upgrade.get("description", "")
            panel.add_child(
                self.colony.ui.label(elemid + "_desc", desc, (6, 30, inner_w - 12, 40))
                .set_text_color(UIColors.TEXT_SECONDARY)
                .set_font_size(16)
                .set_align("left", "top")
            )

            # Button
            btn_w = 120
            btn_h = 24
            btn_x = inner_w - btn_w - 6
            btn_y = height - btn_h - 6

            owned = self.colony.science_upgrades.get(id, False)
            cost = upgrade.get("cost", 0)

            btn_text = "Acquis" if owned else f"{cost} Science"

            btn = self.colony.ui.button(
                elemid + "_btn", btn_text, (btn_x, btn_y, btn_w, btn_h)
            )

            # Important: capture 'id' with default arg to avoid loop variable binding issue
            btn.on("click", lambda u=id: self.buy_upgrade(u))

            panel.add_child(btn)

            scroll_panel.add_child(panel)
            y += height + GAP

        scroll_panel.set_content_height(y)
        self.update_ui()

    def buy_upgrade(self, upgrade_id):
        if self.colony.science_upgrades.get(upgrade_id, False):
            return

        cost = SCIENCE_UPGRADES[upgrade_id]["cost"]
        if self.colony.science >= cost:
            self.colony.science -= cost
            self.colony.science_upgrades[upgrade_id] = True
            self.update_ui()

    def update_ui(self):
        if not (self.colony.sidebar and self.colony.sidebar.main_panel.visible):
            return

        ui = self.colony.ui

        # Update Science Label
        lbl = ui.get("lab_science_display")
        if isinstance(lbl, Label):
            lbl.set_text(f"Science : {int(self.colony.science)}")

        # Update Upgrade Buttons
        for id, upgrade in SCIENCE_UPGRADES.items():
            elemid = f"lab_tree_upg_{id}_btn"
            btn = ui.get(elemid)
            if isinstance(btn, Button):
                owned = self.colony.science_upgrades.get(id, False)
                cost = upgrade.get("cost", 0)

                if owned:
                    btn.set_text("Acquis")
                    btn.set_enabled(False)
                    btn.set_colors(
                        normal=UIColors.BG_DISABLED, hover=UIColors.BG_DISABLED
                    )
                else:
                    btn.set_text(f"{cost} Science")
                    if self.colony.science >= cost:
                        btn.set_enabled(True)
                    else:
                        btn.set_enabled(False)

    def serialize(self):
        return {}

    def restore(self, data):
        pass
