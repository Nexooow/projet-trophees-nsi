from __future__ import annotations

from typing import TYPE_CHECKING, Optional

import pygame

from constants import UIColors

from .element import Element
from lib.utils import parse_color

if TYPE_CHECKING:
    from .manager import UIManager


class ProgressBar(Element):
    """
    Barre de remplissage horizontale affichant un ratio (0.0 – 1.0).
    """

    def __init__(self, ui: "UIManager", id: str, rect=(0, 0, 0, 0)):
        self._value = 1.0
        self.filled_color = UIColors.FILLED_BAR
        self.unfilled_color = UIColors.UNFILLED_BAR
        self.show_text = False
        self.text_color = UIColors.TEXT
        self.font_cache: Optional[pygame.font.Font] = None
        self.font_size = 14

        super().__init__(ui, id, rect)
        self.border_color = UIColors.BORDER
        self.border_width = 2
        
    @property # ajoute rapidement le getter et setter pour l'attribut value
    def value(self) -> float:
        return self._value
        
    def set_value(self, value: float) -> "ProgressBar":
        self._value = max(0.0, min(1.0, value))
        return self

    def set_colors(self, filled, unfilled) -> "ProgressBar":
        self.filled_color = parse_color(filled)
        self.unfilled_color = parse_color(unfilled)
        return self

    def set_show_text(self, show: bool, font_size: int = 14) -> "ProgressBar":
        self.show_text = show
        self.font_size = font_size
        self.font_cache = None
        return self

    def get_font(self) -> pygame.font.Font:
        if self.font_cache is None:
            self.font_cache = pygame.font.Font(None, self.font_size)
        return self.font_cache

    def draw_self(self, screen: pygame.Surface, abs_rect: pygame.Rect):
        # Fond vide
        if self.unfilled_color is not None:
            pygame.draw.rect(
                screen,
                self.unfilled_color,
                abs_rect,
            )

        # Portion remplie
        fill_w = int(abs_rect.width * self.value)
        if fill_w > 0 and self.filled_color is not None:
            fill_rect = pygame.Rect(abs_rect.x, abs_rect.y, fill_w, abs_rect.height)
            pygame.draw.rect(
                screen,
                self.filled_color,
                fill_rect,
            )

        # Bordure
        if self.border_color is not None and self.border_width > 0:
            pygame.draw.rect(
                screen,
                self.border_color,
                abs_rect,
                self.border_width,
            )

        # Étiquette de pourcentage
        if self.show_text:
            font = self.get_font()
            text = f"{int(self.value * 100)}%"
            surf = font.render(text, True, self.text_color)
            tx = abs_rect.x + (abs_rect.width - surf.get_width()) // 2
            ty = abs_rect.y + (abs_rect.height - surf.get_height()) // 2
            screen.blit(surf, (tx, ty))
