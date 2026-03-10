from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

import pygame

from constants import UIColors, FONT_M5X7
from lib.utils import parse_color

from .element import Element

if TYPE_CHECKING:
    from .manager import UIManager

class Label(Element):
    """
    Un simple label texte.
    """

    DEFAULT_FONT_PATH: str = FONT_M5X7
    DEFAULT_FONT_SIZE: int = 16

    def __init__(self, ui: "UIManager", id: str, text: str = "", rect=(0, 0, 0, 0)):
        self.text = text
        self.text_color = UIColors.TEXT
        self.font_path = self.DEFAULT_FONT_PATH
        self.font_size = self.DEFAULT_FONT_SIZE
        self.align = "left"  # "left" | "center" | "right"
        self.valign = "center"  # "haut" | "center" | "bas"
        self.padding = (4, 4)  # (horizontal, vertical)
        self.font_cache: Optional[pygame.font.Font] = None

        super().__init__(ui, id, rect)

    def set_text(self, text: str) -> "Label":
        self.text = text
        return self

    def set_text_color(self, color) -> "Label":
        self.text_color = parse_color(color)
        return self

    def set_font(self, name: Optional[str], size: int) -> "Label":
        self.font_name = name
        self.font_size = size
        self.font_cache = None  # invalider le cache
        return self
        
    def set_font_size(self, size: int) -> "Label":
        self.font_size = size
        self.font_cache = None
        return self

    def set_align(self, align: str, valign: str = "center") -> "Label":
        """
        Définit l'alignement du texte.
        align  : "left" | "center" | "right"
        valign : "top"  | "center" | "bottom"
        """
        self.align = align
        self.valign = valign
        return self

    def set_padding(self, horizontal: int, vertical: int) -> "Label":
        self.padding = (horizontal, vertical)
        return self

    def get_font(self) -> pygame.font.Font:
        if self.font_cache is None:
            if self.font_path:
                try:
                    self.font_cache = pygame.font.Font(self.font_path, self.font_size)
                except FileNotFoundError:
                    self.font_cache = pygame.font.Font(None, self.font_size)
            else:
                self.font_cache = pygame.font.Font(None, self.font_size)
        return self.font_cache

    def current_text_color(self) -> Any:
        return UIColors.TEXT_DISABLED if not self.enabled else self.text_color

    def draw_self(self, screen: pygame.Surface, abs_rect: pygame.Rect):
        super().draw_self(screen, abs_rect)
        if not self.text:
            return
        font = self.get_font()
        color = self.current_text_color()
        text_surf = font.render(self.text, True, color)
        self.blit_aligned(screen, text_surf, abs_rect)

    def blit_aligned(
        self, screen: pygame.Surface, text_surf: pygame.Surface, abs_rect: pygame.Rect
    ):
        text_width, text_height = text_surf.get_size()
        px, py = self.padding

        # Alignement horizontal
        if self.align == "center":
            x = abs_rect.x + (abs_rect.width - text_width) // 2
        elif self.align == "right":
            x = abs_rect.right - text_width - px
        else:
            x = abs_rect.x + px

        if self.valign == "center":
            y = abs_rect.y + (abs_rect.height - text_height) // 2
        elif self.valign == "bottom":
            y = abs_rect.bottom - text_height - py
        else:
            y = abs_rect.y + py

        screen.blit(text_surf, (x, y))
