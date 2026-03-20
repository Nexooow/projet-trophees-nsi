from __future__ import annotations

from typing import TYPE_CHECKING, Optional

import pygame

from constants import UIColors

from .element import Element

if TYPE_CHECKING:
    from .manager import UIManager


class Image(Element):
    """
    Affiche une pygame.Surface en tant qu'élément d'interface.
    """

    def __init__(
        self,
        ui: "UIManager",
        id: str,
        surface: Optional[pygame.Surface] = None,
        rect=(0, 0, 0, 0),
    ):
        self.image = surface
        self.scale_to_rect = False
        super().__init__(ui, id, rect)

    def set_image(
        self, surface: pygame.Surface, scale_to_rect: bool = False
    ) -> "Image":
        self.image = surface
        self.scale_to_rect = scale_to_rect
        return self

    def set_scale(self, scale_to_rect: bool) -> "Image":
        self.scale_to_rect = scale_to_rect
        return self

    def draw_self(self, screen: pygame.Surface, abs_rect: pygame.Rect):
        super().draw_self(screen, abs_rect)
        if self.image is None:
            return

        img = self.image
        if self.scale_to_rect:
            img = pygame.transform.scale(img, (abs_rect.width, abs_rect.height))

        if self.alpha < 255:
            img = img.copy()
            img.set_alpha(self.alpha)

        screen.blit(img, abs_rect.topleft)
