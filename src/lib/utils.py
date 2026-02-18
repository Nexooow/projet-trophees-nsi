import pygame
from typing import Optional, Any


def normalize_rect(rect) -> pygame.Rect:
    """Convertit n'importe quelle valeur rect-compatible en pygame.Rect."""
    if rect is None:
        return pygame.Rect(0, 0, 0, 0)
    if isinstance(rect, (tuple, list)):
        return pygame.Rect(*rect)
    if isinstance(rect, pygame.Rect):
        return rect.copy()
    return pygame.Rect(rect)

def parse_color(color) -> Optional[Any]:
    """Convertit une chaîne hexadécimale ou un tuple en tuple RGBA."""
    if color is None:
        return None
    if isinstance(color, str):
        return tuple(pygame.Color(color))
    return color