from __future__ import annotations

from typing import TYPE_CHECKING, Optional

import pygame

from constants import UIColors
from lib.utils import parse_color

from .element import Element

if TYPE_CHECKING:
    from .manager import UIManager


SCROLLBAR_WIDTH = 8  # largeur de la piste + poignée en pixels
SCROLL_SPEED = 20  # pixels scrollés par cran de molette


class ScrollablePanel(Element):
    """
    Conteneur qui affiche ses enfants dans une zone scrollable.
    """

    def __init__(self, ui: "UIManager", id: str, rect=(0, 0, 0, 0)):
        super().__init__(ui, id, rect)

        self.bg_color = UIColors.BG_DARK
        self.border_color = UIColors.BORDER
        self.border_width = 2

        # offset pour défilement vertical
        self.scroll_y: int = 0

        # hauteur du contenu, si None, calculé automatiquement
        self.content_height: Optional[int] = None

        # état du "drag" de la scrollbar
        self.dragging: bool = False
        self.drag_start_y: int = 0
        self.drag_start_scroll: int = 0

        # couleurs de la scrollbar
        self.scrollbar_track_color = UIColors.BG_DARK
        self.scrollbar_thumb_color = UIColors.BORDER
        self.scrollbar_thumb_hover = UIColors.BORDER_HOVER

        self.thumb_hovered: bool = False

    def set_content_height(self, height: int) -> "ScrollablePanel":
        """
        Fixe la hauteur du contenu. Par défaut elle est calculée automatiquement.
        """
        self.content_height = height
        return self

    def set_scroll(self, value: int) -> "ScrollablePanel":
        """
        Définit la position de défilement (clampée automatiquement).
        """
        self.scroll_y = self.clamp_scroll(value)
        return self

    def scroll_by(self, delta: int) -> "ScrollablePanel":
        """
        Déplace le défilement de `delta` pixels (positif = vers le bas).
        """
        self.scroll_y = self.clamp_scroll(self.scroll_y + delta)
        return self

    def set_scrollbar_colors(
        self, track=None, thumb=None, thumb_hover=None
    ) -> "ScrollablePanel":
        if track is not None:
            self.scrollbar_track_color = parse_color(track)
        if thumb is not None:
            self.scrollbar_thumb_color = parse_color(thumb)
        if thumb_hover is not None:
            self.scrollbar_thumb_hover = parse_color(thumb_hover)
        return self

    def get_content_height(self) -> int:
        """
        Retourne la hauteur totale du contenu (manuel ou auto).
        """
        if self.content_height is not None:
            return self.content_height
        if not self.children:
            return self.rect.height
        return max(c.rect.y + c.rect.height for c in self.children)

    def get_max_scroll(self) -> int:
        """
        Retourne le scroll maximum possible (0 si tout tient dans la vue).
        """
        return max(0, self.get_content_height() - self.rect.height)

    def clamp_scroll(self, value: int) -> int:
        """
        'Clamp' la valeur du scroll entre 0 et le scroll maximum possible.
        https://developer.mozilla.org/fr/docs/Web/CSS/Reference/Values/clamp
        """
        return max(0, min(value, self.get_max_scroll()))

    def scrollbar_rects(
        self, abs_rect: pygame.Rect
    ) -> tuple[Optional[pygame.Rect], Optional[pygame.Rect]]:
        """
        Retourne (track_rect, thumb_rect) en coordonnées absolues écran,
        ou (None, None) si la scrollbar n'est pas nécessaire.
        """
        if self.get_max_scroll() <= 0:
            return None, None

        content_h = self.get_content_height()
        view_h = abs_rect.height

        track_rect = pygame.Rect(
            abs_rect.right - SCROLLBAR_WIDTH,
            abs_rect.y,
            SCROLLBAR_WIDTH,
            view_h,
        )

        # taille de la poignée proportionnelle à la vue sur le contenu
        thumb_h = max(16, int(view_h * view_h / content_h))
        thumb_h = min(thumb_h, view_h)

        # position de la poignée
        scroll_ratio = self.scroll_y / max(1, self.get_max_scroll())
        thumb_y = abs_rect.y + int(scroll_ratio * (view_h - thumb_h))

        thumb_rect = pygame.Rect(
            abs_rect.right - SCROLLBAR_WIDTH,
            thumb_y,
            SCROLLBAR_WIDTH,
            thumb_h,
        )

        return track_rect, thumb_rect

    def draw(self, screen: pygame.Surface):
        if not self.visible:
            return

        abs_rect = self.get_absolute_rect()

        self.draw_self(screen, abs_rect)

        if not self.children:
            return

        # la scrollbar prend SCROLLBAR_WIDTH px sur la droite si nécessaire
        scrollbar_needed = self.get_max_scroll() > 0
        view_w = abs_rect.width - (SCROLLBAR_WIDTH if scrollbar_needed else 0)
        view_h = abs_rect.height
        content_h = self.get_content_height()

        # surface temporaire représentant tout le contenu
        content_surf = pygame.Surface((view_w, max(content_h, view_h)), pygame.SRCALPHA)

        # Détacher temporairement le parent de chaque enfant pour que
        # get_absolute_rect() parte de (0, 0) sur la surface de contenu,
        # et non depuis la position absolue écran du ScrollablePanel.
        for child in self.children:
            child.parent = None
            child.draw(content_surf)
            child.parent = self

        # Blit de la tranche visible avec clipping
        clip_rect = pygame.Rect(abs_rect.x, abs_rect.y, view_w, view_h)
        old_clip = screen.get_clip()
        screen.set_clip(clip_rect)
        screen.blit(content_surf, (abs_rect.x, abs_rect.y - self.scroll_y))
        screen.set_clip(old_clip)

        # Scrollbar
        track_rect, thumb_rect = self.scrollbar_rects(abs_rect)
        if track_rect is not None and thumb_rect is not None:
            if self.scrollbar_track_color is not None:
                pygame.draw.rect(screen, self.scrollbar_track_color, track_rect)
            thumb_color = (
                self.scrollbar_thumb_hover
                if self.thumb_hovered
                else self.scrollbar_thumb_color
            )
            if thumb_color is not None:
                pygame.draw.rect(screen, thumb_color, thumb_rect)

        # Redessiner la bordure par-dessus le contenu (évite les débordements visuels)
        if self.border_color is not None and self.border_width > 0:
            pygame.draw.rect(screen, self.border_color, abs_rect, self.border_width)

    def handle_event(self, event: pygame.event.Event):
        if not self.visible:
            return

        abs_rect = self.get_absolute_rect()

        # molette : uniquement si la souris survole le panel
        if event.type == pygame.MOUSEWHEEL:
            if abs_rect.collidepoint(pygame.mouse.get_pos()):
                self.scroll_by(-event.y * SCROLL_SPEED)
            return

        if self.enabled:
            self.handle_event_self(event)

        # Propagation aux enfants avec position traduite dans l'espace contenu
        if event.type in (
            pygame.MOUSEBUTTONDOWN,
            pygame.MOUSEBUTTONUP,
            pygame.MOUSEMOTION,
        ):
            translated = self.translate_event(event, abs_rect)
            if translated is not None:
                for child in self.children:
                    # Détacher temporairement le parent pour que
                    # get_absolute_rect() parte de (0,0), cohérent
                    # avec la surface de contenu utilisée au dessin.
                    child.parent = None
                    child.handle_event(translated)
                    child.parent = self

    def handle_event_self(self, event: pygame.event.Event):
        """Gère le hover et le drag de la poignée de scrollbar."""
        abs_rect = self.get_absolute_rect()
        _, thumb_rect = self.scrollbar_rects(abs_rect)

        if event.type == pygame.MOUSEMOTION:
            # Mise à jour du hover sur la poignée
            if thumb_rect is not None:
                self.thumb_hovered = thumb_rect.collidepoint(event.pos)

            # Drag en cours : recalcul du scroll
            if self.dragging and thumb_rect is not None:
                delta_mouse = event.pos[1] - self.drag_start_y
                view_h = abs_rect.height
                thumb_h = thumb_rect.height
                scroll_range = max(1, view_h - thumb_h)
                scroll_delta = int(delta_mouse * self.get_max_scroll() / scroll_range)
                self.scroll_y = self.clamp_scroll(self.drag_start_scroll + scroll_delta)

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if thumb_rect is not None and thumb_rect.collidepoint(event.pos):
                self.dragging = True
                self.drag_start_y = event.pos[1]
                self.drag_start_scroll = self.scroll_y

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False

    def translate_event(
        self, event: pygame.event.Event, abs_rect: pygame.Rect
    ) -> Optional[pygame.event.Event]:
        """
        Traduit la position souris de l'espace écran vers l'espace contenu.
        Retourne None si la souris est hors de la zone de contenu visible
        (e.g. sur la scrollbar ou en dehors du panel).
        """
        if not hasattr(event, "pos"):
            return event

        scrollbar_needed = self.get_max_scroll() > 0
        view_w = abs_rect.width - (SCROLLBAR_WIDTH if scrollbar_needed else 0)
        clip_rect = pygame.Rect(abs_rect.x, abs_rect.y, view_w, abs_rect.height)

        # On ne propage que si la souris est dans la zone de contenu visible
        if not clip_rect.collidepoint(event.pos):
            return None

        # Décalage : coordonnées relatives à la surface de contenu
        content_pos = (
            event.pos[0] - abs_rect.x,
            event.pos[1] - abs_rect.y + self.scroll_y,
        )

        if event.type == pygame.MOUSEBUTTONDOWN:
            return pygame.event.Event(
                pygame.MOUSEBUTTONDOWN,
                {"pos": content_pos, "button": event.button},
            )
        elif event.type == pygame.MOUSEBUTTONUP:
            return pygame.event.Event(
                pygame.MOUSEBUTTONUP,
                {"pos": content_pos, "button": event.button},
            )
        elif event.type == pygame.MOUSEMOTION:
            return pygame.event.Event(
                pygame.MOUSEMOTION,
                {"pos": content_pos, "rel": event.rel, "buttons": event.buttons},
            )
        return None
