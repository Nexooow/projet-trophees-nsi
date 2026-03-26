
from .State import State



class ExpeditionMenuState(State):
    def __init__(self, state_manager):
        super().__init__(state_manager, "expedition_menu", [])

        self.selected_ants = 1

    def enable(self):
        w, h = self.game.width, self.game.height

        self.ui.panel(
            "expedition_menu",
            (0, 0, w, h)
        ).add_child(

            self.ui.label(
                "title",
                "Choose ants for expedition",
                (0, 40, w, 40)
            ).set_align("center", "center")

        ).add_child(

            self.ui.label(
                "count_label",
                f"{self.selected_ants}",
                (w//2 - 50, h//2 - 25, 100, 50)
            ).set_align("center", "center")

        ).add_child(

            self.ui.button(
                "minus_btn", "-", (w//2 - 100, h//2 - 25, 40, 40)
            ).on("click", self.decrease_ants)

        ).add_child(

            self.ui.button(
                "plus_btn", "+", (w//2 + 60, h//2 - 25, 40, 40)
            ).on("click", self.increase_ants)

        ).add_child(

            self.ui.button(
                "confirm_btn", "Send", (w//2 - 100, h//2 + 60, 200, 50)
            ).on("click", self.confirm)

        ).add_child(

            self.ui.button(
                "cancel_btn", "Cancel", (w//2 - 100, h//2 + 120, 200, 40)
            ).on("click", self.cancel)
        )

    def increase_ants(self):
        colony = self.state_manager.get_state("colony")
        max_ants = len(colony.ants)

        if self.selected_ants < max_ants:
            self.selected_ants += 1
            self.sync_ui()

    def decrease_ants(self):
        if self.selected_ants > 1:
            self.selected_ants -= 1
            self.sync_ui()

    def sync_ui(self):
        lbl = self.ui.get("count_label")
        if lbl:
            lbl.set_text(str(self.selected_ants))

    def confirm(self):
        colony = self.state_manager.get_state("colony")

        colony.send_expedition(self.selected_ants)

        self.state_manager.set_state("expedition")

    def cancel(self):
        self.state_manager.set_state("colony")
    
    def end_expedition(self):
        colony = self.state_manager.get_state("colony")
        colony.ants.extend(self.ants)
        self.state_manager.set_state("colony")