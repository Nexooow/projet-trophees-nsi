from colony.Room import Room
from lib.ui import UIColors
from constants import SCIENCE_UPGRADES

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
        self.research_progress = 0.0
        self.current_research = None

    def update_self(self, events):
        self.scientists_assigned = 0
        for ant in self.colony.ants:
            if ant.type == "scientist":
                self.scientists_assigned += 1

        if self.scientists_assigned > 0:
            self.colony.science += 0.01 * self.scientists_assigned

        if self.current_research is not None:
            self.research_progress += 0.01
            if self.research_progress >= 1:
                pass  # TODO: finir la recherche

    def interact(self):
        sidebar = self.colony.sidebar
        assert sidebar is not None

        panel_w = sidebar.width
        panel_h = sidebar.height
        inner_w = panel_w - PADDING * 2
        inner_h = panel_h - PADDING * 2

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
                "lab_science",
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

        # AJOUTER TOUTES LES AMELIORATIONS
        y_scroll = PADDING + TITLE_HEIGHT + GAP + 40*2

        root.add_child(
            ui.scrollable_panel(
                "lab_tree_content",
                (PADDING, y_scroll, inner_w, inner_h-y_scroll)
            ).add_children(self.scroll_upgrades(inner_w))
        )


        sidebar.set_content(root)
        sidebar.show()

    def scroll_upgrades (self, inner_w):
        elements = []
        y = 4
        height = 80
        for id, upgrade in SCIENCE_UPGRADES.items():
            elemid = f"lab_tree_upg_{id}"
            elements.append(
                self.colony.ui.panel(
                    elemid,
                    (4, y, inner_w-8, height)
                )
                .set_bg_color(UIColors.BG)
                .set_border(UIColors.BORDER, 1)
                .add_child(
                    self.colony.ui.label(
                        elemid + "_title",
                        upgrade.get("label"),
                        (6, y+2, inner_w-10, 20)
                    ).set_text_color(UIColors.TEXT).set_font_size(24)
                )
                .add_child(
                    self.colony.ui.label(
                        elemid + "_desc",
                    )
                )
            )
            y += height + 4
        return elements

    def serialize(self):
        return {
            "research_progress": self.research_progress,
            "current_research": self.current_research,
        }

    def restore(self, data):
        self.research_progress = data.get("research_progress", 0.0)
        self.current_research = data.get("current_research", None)
