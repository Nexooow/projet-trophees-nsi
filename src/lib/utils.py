import pygame
from typing import Optional, Any
import os

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
    return pygame.mixer.music.load(path)

def distance(pos1, pos2):
    return ((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2) ** 0.5