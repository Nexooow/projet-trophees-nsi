import typing

if typing.TYPE_CHECKING:
    from lib.ui import Element, UIManager


class Sidebar:
    ID = "sidebar"

    def __init__(self, ui: "UIManager", rect: tuple):
        self.ui = ui
        self.x = rect[0]
        self.y = rect[1]
        self.width = rect[2]
        self.height = rect[3]
        self.main_panel = ui.panel(
            self.ID, (self.x, self.y, self.width, self.height)
        ).set_z_index(13)
        self.content_panel_id = None

        self.main_panel.set_visible(False)

    def set_content(self, panel: "Element"):
        if self.content_panel_id:
            self.ui.remove(self.content_panel_id)
            self.main_panel.remove_child(self.content_panel_id)
        self.content_panel_id = panel.id
        self.ui.remove(panel.id)
        self.main_panel.add_child(panel)

    def show(self):
        self.main_panel.set_visible(True)

    def hide(self):
        if self.content_panel_id:
            self.main_panel.remove_child(self.content_panel_id)
            self.content_panel_id = None
        self.main_panel.set_visible(False)
