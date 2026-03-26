"""
Fichier contenant la configuration et les constantes globales du jeu.
"""

import os

GAME_NAME = "Rise of the Anthill"
SAVES_PATH = os.sep.join([os.path.dirname(__file__), "..", "data", "saves"])

CURRENT_SAVE_VERSION = 1

CELL_STATES = {
    "empty": 0,
    "full_v1": 1,
    "full_v2": 2,
    "full_v3": 3,
    "full_v4": 4,
    "occupied": 10,
    "occupied_walkable": 11,
}

ASSETS_PATH = os.sep.join([os.path.dirname(__file__), "..", "data", "assets"])
ROOMS_PATH = os.sep.join([ASSETS_PATH, "rooms"])

FONTS_PATH = os.sep.join([ASSETS_PATH, "fonts"])
FONT_M5X7 = os.sep.join([FONTS_PATH, "m5x7.ttf"])

DAY_START = 6 * 60
DAY_END = 21 * 60

COLONY_WIDTH = 2867
COLONY_HEIGHT = 1612
COLONY_GRASS_START = 360
COLONY_UNDERGROUND_START = COLONY_GRASS_START + 40

COLONY_BRUSH_SIZE = 20

COLONY_BRUSH_COLOR = "#b12935"
GALERY_COLOR = "#9c4e3e"
DARK_GALERY_COLOR = "#6e3228"
DIRT_COLOR = "#b86858"
DARK_DIRT_COLOR = (115, 65, 55)

NIGHT_COLOR = (11, 14, 41)
SUNRISE_COLOR = (255, 153, 102)
DAY_COLOR = (125, 190, 250)
SUNSET_COLOR = (235, 107, 86)


class UIColors:
    BG = (92, 64, 51)  # #5C4033
    BG_HOVER = (125, 90, 63)  # #7D5A3F
    BG_DARK = (46, 31, 26)  # #2E1F1A
    BG_DISABLED = (62, 42, 35)  # #3E2A23

    TEXT = (244, 232, 193)  # #F4E8C1
    TEXT_SECONDARY = (204, 193, 159)
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


# colony constants
INITIAL_FOOD_CAPACITY = 5000
INITIAL_MAX_ENERGY = 100
ENERGY_RECOVERY_RATE = 0.5  # per second in dormitory
ENERGY_RECOVERY_RATE_GROUND = 0.1  # per second on ground
ENERGY_CONSUMPTION_RATE = 0.05  # per second when working/moving

# colony tasks

TASK_ANT_TYPE: dict = {
    "dig": "worker",
    "build": "worker",
    "fight": "warrior",
    "heal": "nurse",
    "research": "scientist",
    "explore": "explorer",
    "bring_food": "worker",
    "bring_food_queen": "worker",
    "deliver_larva": "worker",
}

TASK_DEFAULT_PRIORITY: dict = {
    "dig": 1,
    "bring_food": 2,
    "build": 1,
    "fight": 5,
    "heal": 4,
    "research": 1,
    "explore": 1,
    "bring_food_queen": 10,
    "deliver_larva": 8,
    "clean": 3,
    "rest": 0,
}

PRICE_PER_DIRTPIXEL = 0.05

# Nombre maximum de larves en production simultanée (augmentable plus tard)
QUEEN_MAX_LARVAE = 3

# Fourmis productibles par la reine : coût en nourriture et temps en secondes
QUEEN_LARVAS: dict = {
    "worker": {
        "label": "Ouvrière",
        "cost": 500,
        "time": 30,
    },
    "nurse": {
        "label": "Nourrice",
        "cost": 700,
        "time": 40,
    },
    "warrior": {
        "label": "Guerrière",
        "cost": 1000,
        "time": 60,
    },
    "scientist": {
        "label": "Scientifique",
        "cost": 4000,
        "time": 9,
    },
    "explorer": {
        "label": "Exploratrice",
        "cost": 2000,
        "time": 50,
    },
}

# Améliorations disponibles via la reine pour la colonie
QUEEN_UPGRADES: dict = {
    "birth_speed": {
        "label": "Vitesse de naissance",
        "description": "Réduit le temps de production des fourmis",
        "levels": [
            {"cost": 5000, "effect": "-10 %"},
            {"cost": 7500, "effect": "-10 %"},
            {"cost": 10000, "effect": "-10 %"},
        ],
    },
    "science": {
        "label": "Progrès scientifique",
        "description": "Débloque les technologies scientifiques",
        "cost": 7000,
        "levels": [],
    },
}

# TODO: ajouter des items, utilisables dans le système d'exploration/combat
# Dictionnaires des items disponibles, la clé est l'ID de l'item
# La valeur doit être un dictionnaire avec les clés "label", "description"
ITEMS = {
    "allumette": {
        "label": "Match",
        "description": "Fait exploser la bombe de son choix"
    }
}

# Configuration des salles constructibles
ROOMS_CONFIG = {
    "queen": {
        "label": "Reine",
        "description": "Le cœur de la colonie.",
        "cost": 0,
        "width": 12,
        "height": 12,
        "entry_offset": (0.0, 0.75),
    },
    "depot": {
        "label": "Dépôt",
        "description": "Stockage de nourriture.",
        "cost": 0,
        "width": 13,
        "height": 8,
        "entry_offset": (0.5, 1.0),
    },
    "nursery": {
        "label": "Nurserie",
        "description": "Lieu où les larves se développent.",
        "cost": 1500,
        "width": 15,
        "height": 7,
        "entry_offset": (1.0, 0.75),
    },
    "laboratory": {
        "label": "Laboratoire",
        "description": "Permet aux scientifiques de mener des recherches.",
        "cost": 3000,
        "width": 12,
        "height": 10,
        "entry_offset": (0.0, 0.5),
    },
    "dormitory": {
        "label": "Dortoir",
        "description": "Permet aux fourmis de récupérer leur énergie.",
        "cost": 1200,
        "width": 10,
        "height": 7,
        "entry_offset": (0.5, 1.0),
    },
    #"waste_yard": {
    #    "label": "Dépotoir",
    #    "description": "Réduit les maladies en centralisant les déchets.",
    #    "cost": 800,
    #    "width": 8,
    #    "height": 6,
    #    "entry_offset": (0.5, 1.0),
    #},
}

SCIENCE_UPGRADES = {
    "demineur": {
        "label": "Démineur",
        "description": "Lors de la résolution automatique de l'exploration, vos fourmis évitent les bombes.",
        "cost": 500,  # coût en science
    }
}
