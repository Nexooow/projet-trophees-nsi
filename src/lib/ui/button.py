from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pygame

from constants import UIColors

from .label import Label
from lib.utils import parse_color

if TYPE_CHECKING:
    from .manager import UIManager


class Button(Label):
    """
    Bouton interactif avec états visuels au survol et désactivé.
    """

    def __init__(self, ui: "UIManager", id: str, text: str = "", rect=(0, 0, 0, 0)):
        super().__init__(ui, id, text, rect)

        self.font_size = 22
        self.align = "center"
        self.valign = "center" # alignement vertical
        self.border_width = 2
        self.border_color = UIColors.BORDER
        self.bg_color = UIColors.BTN_BG

        self.bg_normal = UIColors.BTN_BG
        self.bg_hover = UIColors.BTN_BG_HOVER
        self.bg_active = UIColors.BTN_BG_ACTIVE
        self.bg_disabled = UIColors.BG_DISABLED
        self.is_pressed = False

    def set_colors(
        self,
        normal=None,
        hover=None,
        active=None,
        disabled=None,
    ) -> "Button":
        if normal is not None:
            self.bg_normal = parse_color(normal)
        if hover is not None:
            self.bg_hover = parse_color(hover)
        if active is not None:
            self.bg_active = parse_color(active)
        if disabled is not None:
            self.bg_disabled = parse_color(disabled)
        return self

    def current_bg(self) -> Any:
        if not self.enabled:
            return self.bg_disabled
        if self.is_pressed:
            return self.bg_active
        if self.hovered:
            return self.bg_hover
        return self.bg_normal

    def current_text_color(self) -> Any:
        if not self.enabled:
            return UIColors.TEXT_DISABLED
        if self.hovered:
            return UIColors.TEXT_HOVER
        return self.text_color

    def current_border_color(self) -> Any:
        return (
            UIColors.BORDER_HOVER if self.hovered and self.enabled else UIColors.BORDER
        )

    def draw_self(self, screen: pygame.Surface, abs_rect: pygame.Rect):
        # Fond
        s = pygame.Surface((abs_rect.width, abs_rect.height), pygame.SRCALPHA)
        s.set_alpha(self.alpha)
        pygame.draw.rect(
            s,
            self.current_bg(),
            (0, 0, abs_rect.width, abs_rect.height),
        )
        # Bordure
        if self.border_width > 0:
            pygame.draw.rect(
                s,
                self.current_border_color(),
                (0, 0, abs_rect.width, abs_rect.height),
                self.border_width,
            )
        screen.blit(s, abs_rect.topleft)

        # Texte
        if self.text:
            font = self.get_font()
            text_surf = font.render(self.text, True, self.current_text_color())
            self.blit_aligned(screen, text_surf, abs_rect)

    def handle_event_self(self, event: pygame.event.Event):
        super().handle_event_self(event)
        abs_rect = self.get_absolute_rect()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if abs_rect.collidepoint(event.pos):
                self.is_pressed = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.is_pressed = False
