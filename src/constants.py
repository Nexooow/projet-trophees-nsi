"""
Fichier contenant la configuration et les constantes globales du jeu.
"""
import os

GAME_NAME = "Rise of the Anthill"
SAVES_PATH = os.path.join(os.path.dirname(__file__), "../", "data", "saves")

COLONY_WIDTH = 2867
COLONY_HEIGHT = 1612
COLONY_GRASS_START = 360
COLONY_UNDERGROUND_START = COLONY_GRASS_START+40

COLONY_BRUSH_SIZE = 20

COLONY_BRUSH_COLOR = "#b12935"
GALERY_COLOR = "#9c4e3e"
DARK_GALERY_COLOR = "#6e3228"
DIRT_COLOR = "#b86858"
DARK_DIRT_COLOR = "#783828"

class UIColors:
    BG = (92, 64, 51)  # #5C4033
    BG_HOVER = (125, 90, 63)  # #7D5A3F
    BG_DARK = (46, 31, 26)  # #2E1F1A
    BG_DISABLED = (62, 42, 35)  # #3E2A23

    TEXT = (244, 232, 193)  # #F4E8C1
    TEXT_HOVER = (255, 248, 220)  # #FFF8DC
    TEXT_DISABLED = (139, 115, 85)  # #8B7355

    BORDER = (200, 212, 168)  # #C8D4A8
    BORDER_HOVER = (212, 224, 188)  # #D4E0BC

    FILLED_BAR = (200, 212, 168)  # #C8D4A8
    UNFILLED_BAR = (74, 52, 40)  # #4A3428

    BTN_BG = (107, 68, 35)  # #6B4423
    BTN_BG_HOVER = (139, 90, 43)  # #8B5A2B
    BTN_BG_ACTIVE = (160, 104, 77)  # #A0684D

    SHADOW = (26, 18, 13)  # #1A120D
    
    GREEN = (50, 168, 82)
    DARK_GREEN = (20, 103, 86)
    
# colony tasks

TASK_ANT_TYPE: dict[str, str] = {
    "dig": "worker",
    "bring_food": "worker",
    "build": "worker",
    "fight": "warrior",
    "heal": "nurse",
    "research": "scientist",
    "explore": "explorer",
    "feed_queen": "worker",
}

TASK_DEFAULT_PRIORITY: dict[str, int] = {
    "dig": 1,
    "bring_food": 2,
    "build": 1,
    "fight": 5,
    "heal": 4,
    "research": 1,
    "explore": 1,
}

PRICE_PER_DIRTPIXEL = 2