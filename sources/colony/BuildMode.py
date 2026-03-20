import math
import typing
from tabnanny import NannyNag

import pygame
from constants import (
    COLONY_BRUSH_COLOR,
    COLONY_BRUSH_SIZE,
    COLONY_HEIGHT,
    COLONY_UNDERGROUND_START,
    COLONY_WIDTH,
    PRICE_PER_DIRTPIXEL,
    ROOMS_CONFIG,
)
from lib.ui import Button, Label, UIColors
from lib.utils import distance

if typing.TYPE_CHECKING:
    from states.ColonyState import ColonyState


class BuildMode:
    def __init__(self, colony_state: "ColonyState"):
        self.colony = colony_state
        self.ui = colony_state.ui
        self.enabled = False
        self.valid_selections = set()
        self.selections = set()
        self.builds = []

        self.selected_room_type = None
        self.room_current_rect = None
        self.placed_rooms = []

    def get_dug_pixels(self) -> int:
        """
        Retourne une approximation du nombre de pixels qui vont être creusés.
        Permet de calculer le coût en nourriture de la construction.
        """
        count = 0
        for x, y in self.selections:
            count += math.pi * (COLONY_BRUSH_SIZE / 2) ** 2
        return math.ceil(count)

    def get_gallery_price(self):
        """
        Retourne le coût en nourriture du creusage des galeries.
        """
        return self.get_dug_pixels() * PRICE_PER_DIRTPIXEL

    def get_room_price(self):
        """
        Retourne le coût de la salle sélectionnée.
        """
        total_cost = 0
        for _, room_type in self.placed_rooms:
            total_cost += ROOMS_CONFIG[room_type]["cost"]
        return total_cost

    def get_price(self):
        """
        Retourne le coût total de la construction.
        """
        return self.get_gallery_price() + self.get_room_price()

    def switch(self):
        assert self.colony.sidebar is not None
        sidebar = self.colony.sidebar

        self.enabled = not self.enabled
        btn = self.ui.get("colony_btn_build")
        if isinstance(btn, Button):
            if self.enabled:
                btn.set_colors(normal=UIColors.GREEN, hover=UIColors.DARK_GREEN)
            else:
                btn.set_colors(normal=UIColors.BTN_BG, hover=UIColors.BTN_BG_HOVER)

        if self.enabled:
            panel = (
                self.ui.panel(
                    "colony_sidebar_build",
                    (4, 4, sidebar.width - 4 * 2, sidebar.height - 4 * 2),
                )
                .set_border(None, 0)
                .add_children(
                    [
                        self.ui.label(
                            "colony_sidebar_build_title",
                            "Construction",
                            (4, 6, sidebar.width - 8 * 2, 30),
                        )
                        .set_font_size(36)
                        .set_align("center", "center"),
                        self.ui.label(
                            "colony_sidebar_build_dug",
                            "Pixels creusés",
                            (4, 36 + 6, sidebar.width - 8 * 2, 30),
                        )
                        .set_font_size(24)
                        .set_align("left", "center"),
                        self.ui.label(
                            "colony_sidebar_colony_price",
                            f"Galeries : {self.get_gallery_price():.1f}",
                            (4, 36 + 25, sidebar.width - 8 * 2, 30),
                        )
                        .set_font_size(20)
                        .set_align("right", "center")
                        .set_text_color(UIColors.TEXT_SECONDARY),
                        self.ui.label(
                            "colony_sidebar_room_price",
                            f"Salle : {self.get_room_price()}",
                            (4, 36 + 45, sidebar.width - 8 * 2, 30),
                        )
                        .set_font_size(20)
                        .set_align("right", "center")
                        .set_text_color(UIColors.TEXT_SECONDARY),
                        self.ui.label(
                            "colony_sidebar_total_price",
                            f"Total : {self.get_price():.1f}",
                            (4, 36 + 65, sidebar.width - 8 * 2, 30),
                        )
                        .set_font_size(22)
                        .set_align("right", "center")
                        .set_text_color(UIColors.TEXT),
                    ]
                )
            )

            # Boutons de sélection de salles
            y_offset = 36 + 100
            panel.add_child(
                self.ui.label(
                    "colony_sidebar_rooms_label",
                    "Salles",
                    (4, y_offset, sidebar.width - 8 * 2, 20),
                ).set_font_size(20)
            )
            y_offset += 25

            for room_id, config in ROOMS_CONFIG.items():

                def select_room(rid=room_id):
                    if self.selected_room_type == rid:
                        self.selected_room_type = None
                    else:
                        self.selected_room_type = rid
                    self.room_current_rect = None

                panel.add_child(
                    self.ui.button(
                        f"btn_room_{room_id}",
                        f"{config['label']} ({config['cost']})",
                        (4, y_offset, sidebar.width - 8 * 2, 25),
                    )
                    .set_font_size(18)
                    .on("click", select_room)
                )
                y_offset += 30

            panel.add_children(
                [
                    self.ui.button(
                        "colony_sidebar_build_cancel",
                        "Annuler",
                        (4, sidebar.height - 46 - 30 - 4, sidebar.width - 8 * 2, 30),
                    )
                    .set_font_size(24)
                    .set_align("center", "center")
                    .on("click", self.cancel_build),
                    self.ui.button(
                        "colony_sidebar_build_start",
                        "Démarrer la construction",
                        (4, sidebar.height - 46, sidebar.width - 8 * 2, 30),
                    )
                    .set_font_size(24)
                    .set_align("center", "center")
                    .on("click", self.start_build),
                ]
            )

            sidebar.set_content(panel.set_z_index(13))
            sidebar.show()
        else:
            sidebar.hide()

    def find_closest_selection(self, select_x, select_y) -> typing.Optional[tuple]:
        selections_tri = sorted(
            self.selections, key=lambda s: distance(s, (select_x, select_y))
        )
        select_proche = selections_tri[0]
        if distance(select_proche, (select_x, select_y)) <= 2 * COLONY_BRUSH_SIZE:
            return select_proche
        else:
            return None

    def is_linked_gallery(self, select_x, select_y):
        pos = self.colony.grid.pixel_to_cell(
            select_x, select_y - COLONY_UNDERGROUND_START
        )
        cell = self.colony.grid.get_cell(*pos)
        if not cell:
            return False
        return cell["state"] == "empty" or cell["state"] == "partial"

    def closest_valid(self, select_x, select_y):
        if not self.selections:
            return False

        # On cherche s'il y a une sélection valide assez proche
        for sel_x, sel_y in self.valid_selections:
            if distance((sel_x, sel_y), (select_x, select_y)) <= COLONY_BRUSH_SIZE:
                return True
        return False

    def validate_selections(self):
        """
        Parcourt les sélections pour valider celles qui sont connectées
        à une galerie existante ou à une sélection déjà valide.
        """
        to_validate = [
            sel for sel in self.selections if sel not in self.valid_selections
        ]

        # On valide ce qui touche une galerie
        still_invalid = []
        for sel in to_validate:
            if self.is_linked_gallery(sel[0], sel[1]):
                self.valid_selections.add(sel)
            else:
                still_invalid.append(sel)

        # on propage la validité par proximité
        changed = True
        while changed and still_invalid:
            changed = False
            remaining = []
            for sel in still_invalid:
                if self.closest_valid(sel[0], sel[1]):
                    self.valid_selections.add(sel)
                    changed = True
                else:
                    remaining.append(sel)
            still_invalid = remaining

    def update(self, events):
        self.sync_ui()

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:  # clear
                    self.selections.clear()
                    self.room_start_pos = None
                    self.room_current_rect = None

            if self.selected_room_type:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                    # On fixe la position de la salle au clic droit
                    if self.room_current_rect:
                        self.placed_rooms.append(
                            (self.room_current_rect.copy(), self.selected_room_type)
                        )
                        # On valide immédiatement les pixels de cette salle
                        rect = self.room_current_rect
                        for x in range(rect.left, rect.right, COLONY_BRUSH_SIZE):
                            for y in range(rect.top, rect.bottom, COLONY_BRUSH_SIZE):
                                self.selections.add((x, y))
                        self.validate_selections()

        if not self.selected_room_type:
            if pygame.mouse.get_pressed()[2]:
                mouse_pos = pygame.mouse.get_pos()
                mouse_pos = (
                    mouse_pos[0] - self.colony.camera_x,
                    mouse_pos[1] - self.colony.camera_y,
                )
                if (
                    mouse_pos[0] >= 0
                    and mouse_pos[0] < COLONY_WIDTH
                    and mouse_pos[1] >= 0
                    and mouse_pos[1] < COLONY_HEIGHT
                    and mouse_pos[1] > COLONY_UNDERGROUND_START + COLONY_BRUSH_SIZE
                ):
                    brush_x = mouse_pos[0] - COLONY_BRUSH_SIZE // 2
                    brush_y = mouse_pos[1] - COLONY_BRUSH_SIZE // 2

                    self.selections.add((brush_x, brush_y))
                    self.validate_selections()
        elif self.selected_room_type:
            mouse_pos = pygame.mouse.get_pos()
            mouse_world = (
                mouse_pos[0] - self.colony.camera_x,
                mouse_pos[1] - self.colony.camera_y,
            )

            config = ROOMS_CONFIG[self.selected_room_type]
            w_px = config["width"] * 8
            h_px = config["height"] * 8

            # aperçu
            self.room_current_rect = pygame.Rect(
                mouse_world[0] - w_px // 2, mouse_world[1] - h_px // 2, w_px, h_px
            )

    def sync_ui(self):
        gallery_ui = self.colony.ui.get("colony_sidebar_colony_price")
        if isinstance(gallery_ui, Label):
            gallery_ui.set_text(f"Galeries : {self.get_gallery_price():.1f}")

        room_ui = self.colony.ui.get("colony_sidebar_room_price")
        if isinstance(room_ui, Label):
            room_ui.set_text(f"Salle : {self.get_room_price()}")

        total_ui = self.colony.ui.get("colony_sidebar_total_price")
        if isinstance(total_ui, Label):
            total_ui.set_text(f"Total : {self.get_price():.1f}")

    def draw(self):
        mouse_pos = pygame.mouse.get_pos()
        mouse_world_pos = (
            mouse_pos[0] - self.colony.camera_x,
            mouse_pos[1] - self.colony.camera_y,
        )

        radius = COLONY_BRUSH_SIZE / 2

        room_pixels = set()
        for rect, _ in self.placed_rooms:
            for rx in range(rect.left, rect.right, COLONY_BRUSH_SIZE):
                for ry in range(rect.top, rect.bottom, COLONY_BRUSH_SIZE):
                    room_pixels.add((rx, ry))

        for x, y in self.selections:
            if (x, y) in room_pixels:
                continue

            center_x = x + radius
            center_y = y + radius
            pygame.draw.circle(
                self.colony.world,
                "green" if (x, y) in self.valid_selections else COLONY_BRUSH_COLOR,
                (center_x, center_y),
                radius,
            )

        # aperçu
        for rect, room_type in self.placed_rooms:
            entry_x = rect.centerx
            entry_y = rect.centery
            is_valid = self.is_linked_gallery(entry_x, entry_y)
            color = (0, 255, 0) if is_valid else (255, 0, 0)

            pygame.draw.rect(self.colony.world, color, rect, 3)
            pygame.draw.rect(self.colony.world, (*color, 80), rect, 3)

        if self.room_current_rect:
            # Vérifier si l'entrée (centre) est proche d'une galerie
            entry_x = self.room_current_rect.centerx
            entry_y = self.room_current_rect.centery
            is_valid = self.is_linked_gallery(entry_x, entry_y)

            color = (0, 255, 0) if is_valid else (255, 0, 0)

            # Dessiner le rectangle de la salle
            pygame.draw.rect(self.colony.world, color, self.room_current_rect, 3)
            pygame.draw.rect(self.colony.world, (*color, 60), self.room_current_rect, 3)

        if (
            not self.selected_room_type
            and mouse_world_pos[0] >= 0
            and mouse_world_pos[0] < COLONY_WIDTH
            and mouse_world_pos[1] >= 0
            and mouse_world_pos[1] < COLONY_HEIGHT
            and mouse_world_pos[1] > COLONY_UNDERGROUND_START + COLONY_BRUSH_SIZE
        ):
            brush_x = mouse_world_pos[0]
            brush_y = mouse_world_pos[1]

            pygame.draw.circle(
                self.colony.world,
                COLONY_BRUSH_COLOR,
                (brush_x, brush_y),
                radius,
            )

    def start_build(self):
        """
        Commence la construction.
        """
        if not self.valid_selections:
            self.switch()
            return

        to_build = set(self.valid_selections)
        ordered_builds = []

        current_layer = []
        for sel in list(to_build):  # galeries adjacentes aux galeries existantes
            if self.is_linked_gallery(*sel):
                current_layer.append(sel)
                to_build.remove(sel)

        ordered_builds.extend(current_layer)

        while current_layer and to_build:
            next_layer = []
            remaining = list(to_build)
            for candidate in remaining:
                for node in current_layer:
                    if distance(candidate, node) <= COLONY_BRUSH_SIZE:
                        next_layer.append(candidate)
                        to_build.remove(candidate)
                        break

            ordered_builds.extend(next_layer)
            current_layer = next_layer

        # créer les tâches
        total = len(ordered_builds)
        for i, pos in enumerate(ordered_builds):
            # priorité décroissante pour que les ouvrières commencent par le début
            prio = max(1, 100 - int((i / total) * 90))
            self.colony.pending_builds.append({"pos": pos, "priority": prio})

        self.colony.check_pending_builds()

        # Si des salles ont été placées, on les ajoute à la liste des salles
        if self.placed_rooms:
            for rect, room_type in self.placed_rooms:
                config = ROOMS_CONFIG[room_type]
                room_data = {
                    "x": rect.x // 8,
                    "y": (rect.y - COLONY_UNDERGROUND_START) // 8,
                    "width": config["width"],
                    "height": config["height"],
                }

                # TODO: lancer la construction de la salle

        # retire les séléctions qui vont être construites (aka celles qui sont valides)
        for built in ordered_builds:
            if built in self.selections:
                self.selections.remove(built)

        self.valid_selections.clear()
        self.selected_room_type = None
        self.room_current_rect = None
        self.placed_rooms = []
        self.switch()

    def cancel_build(self):
        """
        Annule la construction.
        """
        self.selections.clear()
        self.selected_room_type = None
        self.room_current_rect = None
        self.placed_rooms = []
        self.switch()
