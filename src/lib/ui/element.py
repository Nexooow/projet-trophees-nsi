from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Optional

import pygame

from constants import UIColors

from lib.utils import normalize_rect, parse_color

if TYPE_CHECKING:
    # importe UIManager seulement pour la validation de type,
    # afin d'éviter les imports cycliques lors de l'éxécution
    from .manager import UIManager


class Element:
    """
    Classe de base pour tous les éléments d'interface.
    """

    def __init__(self, ui: "UIManager", id: str, rect=(0, 0, 0, 0)):
        self.ui = ui
        self.id = id
        self.rect = normalize_rect(rect)

        self.visible = True
        self.enabled = True
        self.z_index = 0
        self.alpha = 255

        self.parent: Optional["Element"] = None
        self.children: list["Element"] = []

        # style
        self.bg_color: Optional[Any] = None
        self.border_color: Optional[Any] = None
        self.border_width: int = 0

        # "callbacks"
        self.on_click: Optional[Callable] = None
        self.on_hover_enter: Optional[Callable] = None
        self.on_hover_leave: Optional[Callable] = None
        self.hovered = False

    def set_rect(self, rect) -> "Element":
        self.rect = normalize_rect(rect)
        return self

    def get_absolute_rect(self) -> pygame.Rect:
        """
        Retourne le rectangle absolu de l'élément,
        décalé par la position de tous ses ancêtres.
        """
        if self.parent is not None:
            pr = self.parent.get_absolute_rect()
            return pygame.Rect(
                self.rect.x + pr.x,
                self.rect.y + pr.y,
                self.rect.width,
                self.rect.height,
            )
        return self.rect.copy()

    def set_visible(self, visible: bool) -> "Element":
        self.visible = visible
        return self

    def toggle_visible(self) -> "Element":
        self.visible = not self.visible
        return self

    def set_enabled(self, enabled: bool) -> "Element":
        self.enabled = enabled
        for child in self.children:
            child.set_enabled(enabled)
        return self

    def set_z_index(self, z: int) -> "Element":
        self.z_index = z
        self.ui.sort_elements()
        return self

    def set_alpha(self, alpha: int) -> "Element":
        """Définit la transparence globale de l'élément (0-255)."""
        self.alpha = max(0, min(255, alpha))
        return self

    def set_bg_color(self, color) -> "Element":
        self.bg_color = parse_color(color)
        return self

    def set_border(self, color, width: int = 2) -> "Element":
        self.border_color = parse_color(color)
        self.border_width = width
        return self

    def on(self, event: str, callback: Callable) -> "Element":
        """
        Enregistre un callback pour un événement donné.
        Événements supportés : "click", "hover_enter", "hover_leave".
        """
        match event:
            case "click":
                self.on_click = callback
            case "hover_enter":
                self.on_hover_enter = callback
            case "hover_leave":
                self.on_hover_leave = callback
        return self

    def add_child(self, child: "Element") -> "Element":
        """
        Attache un élément enfant.
        """
        child.parent = self
        self.children.append(child)
        return self

    def remove_child(self, child_id: str) -> "Element":
        self.children = [c for c in self.children if c.id != child_id]
        return self

    def draw(self, screen: pygame.Surface):
        if not self.visible:
            return
        abs_rect = self.get_absolute_rect()
        self.draw_self(screen, abs_rect)
        for child in self.children:
            child.draw(screen)

    def draw_self(self, screen: pygame.Surface, abs_rect: pygame.Rect):
        """
        Dessine l'élément.
        """
        if self.bg_color is not None:
            s = pygame.Surface((abs_rect.width, abs_rect.height), pygame.SRCALPHA)
            s.set_alpha(self.alpha)
            pygame.draw.rect(
                s,
                self.bg_color,
                (0, 0, abs_rect.width, abs_rect.height),
            )
            screen.blit(s, abs_rect.topleft)

        if self.border_color is not None and self.border_width > 0:
            pygame.draw.rect(
                screen,
                self.border_color,
                abs_rect,
                self.border_width,
            )

    def handle_event(self, event: pygame.event.Event):
        """
        Propage les événements d'entrée à cet élément et à tous ses enfants.
        """
        if not self.visible:
            return
        if self.enabled:
            self.handle_event_self(event)
        for child in self.children:  # délègue les événements aux enfants
            child.handle_event(event)

    def handle_event_self(self, event: pygame.event.Event):
        abs_rect = self.get_absolute_rect()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if abs_rect.collidepoint(event.pos) and self.on_click:
                self.on_click()

        elif event.type == pygame.MOUSEMOTION:
            hovered = abs_rect.collidepoint(event.pos)
            if hovered and not self.hovered:
                self.hovered = True
                if self.on_hover_enter:
                    self.on_hover_enter()
            elif not hovered and self.hovered:
                self.hovered = False
                if self.on_hover_leave:
                    self.on_hover_leave()
