import os
from typing import Any, Optional

import pygame


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


def import_asset(*args):
    path = os.sep.join(["data", "assets"] + list(args))
    return pygame.image.load(path)


def import_sound(*args):
    path = os.sep.join(["data", "assets", "sounds"] + list(args))
    return path


def use_font(size):
    return pygame.font.Font(
        os.sep.join(["data", "assets", "fonts", "m5x7.ttf"]), size or 16
    )


def distance(pos1, pos2):
    return ((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2) ** 0.5


def lerp(a, b, t):
    """Interpolation linéaire entre a et b par t"""
    return a + (b - a) * t


def lerp_color(c1, c2, t):
    """Interpolation linéaire entre deux couleurs (tuples RGB ou RGBA)"""
    return tuple(int(lerp(c1[i], c2[i], t)) for i in range(len(c1)))


def fill(surface, color):
    """Remplace la couleur d'une surface pygame en conservant le canal alpha de chaque pixel."""
    w, h = surface.get_size()
    r, g, b, _ = color
    for x in range(w):
        for y in range(h):
            a = surface.get_at((x, y))[3]
            surface.set_at((x, y), pygame.Color(r, g, b, a))
    return surface


def mouse_over(unit):
    """
    Retourne True si la souris survole le sprite de l'unité
    (collision pixel-perfect via le mask).
    """
    mouse = pygame.mouse.get_pos()
    if not unit.rect.collidepoint(mouse):
        return False
    rel_x = mouse[0] - unit.rect.x
    rel_y = mouse[1] - unit.rect.y
    mask_w, mask_h = unit.mask.get_size()

    if 0 <= rel_x < mask_w and 0 <= rel_y < mask_h:
        return unit.mask.get_at((rel_x, rel_y))

    return False