import math
import random

import pygame
from constants import (
    COLONY_GRASS_START,
    COLONY_WIDTH,
    DAY_COLOR,
    DAY_END,
    DAY_START,
    NIGHT_COLOR,
    SUNRISE_COLOR,
    SUNSET_COLOR,
)
from lib.utils import lerp_color


class Sky:
    def __init__(self, game):
        self.game = game
        self.width = COLONY_WIDTH
        self.height = COLONY_GRASS_START

        self.stars = [
            {
                "x": random.randint(0, self.width),
                "y": random.randint(0, self.height),
                "size": random.randint(1, 3),
                "alpha": random.randint(150, 255),
                "twinkle_speed": random.uniform(0.002, 0.005),
                "twinkle_offset": random.uniform(0, 6.28),
            }
            for _ in range(150)
        ]

    def get_sky_color(self):
        minutes = self.game.time.time % 1440
        color = NIGHT_COLOR

        if 6 * 60 <= minutes < 9 * 60:  # 6h-9h
            factor = (minutes - 360) / 180
            if factor < 0.5:
                color = lerp_color(NIGHT_COLOR, SUNRISE_COLOR, factor * 2)
            else:
                color = lerp_color(SUNRISE_COLOR, DAY_COLOR, (factor - 0.5) * 2)
        elif 9 * 60 <= minutes < 18 * 60:  # Jour
            color = DAY_COLOR
        elif 18 * 60 <= minutes < 21 * 60:  # 18h-21h
            factor = (minutes - 18 * 60) / 180
            if factor < 0.5:
                color = lerp_color(DAY_COLOR, SUNSET_COLOR, factor * 2)
            else:
                color = lerp_color(SUNSET_COLOR, NIGHT_COLOR, (factor - 0.5) * 2)

        return color

    def draw(self, surface):
        color = self.get_sky_color()

        pygame.draw.rect(surface, color, (0, 0, self.width, self.height))

        minutes = self.game.time.time % 1440

        if color != DAY_COLOR:
            star_alpha_mult = 1.0
            if 6 * 60 <= minutes < 9 * 60:
                star_alpha_mult = 1.0 - ((minutes - 360) / 180)
            elif 18 * 60 <= minutes < 21 * 60:
                star_alpha_mult = (minutes - 18 * 60) / 180
            elif 9 * 60 <= minutes < 18 * 60:
                star_alpha_mult = 0.0

            if star_alpha_mult > 0:
                current_time = pygame.time.get_ticks()
                for star in self.stars:
                    alpha = int(star["alpha"] * star_alpha_mult)
                    if alpha > 0:
                        twinkle = math.sin(
                            current_time * star["twinkle_speed"]
                            + star["twinkle_offset"]
                        )
                        final_alpha = max(0, min(255, alpha + int(twinkle * 50)))
                        s = pygame.Surface(
                            (star["size"], star["size"]), pygame.SRCALPHA
                        )
                        s.fill((255, 255, 255, final_alpha))
                        surface.blit(s, (star["x"], star["y"]))

    def draw_clock(self, surface):
        """Dessine l'horloge sur la surface donnée"""
        w, h = surface.get_size()
        minutes = self.game.time.time % 1440

        sky_color = self.get_sky_color()
        surface.fill(sky_color)

        center_x, center_y = w // 2, h + 20
        radius = h - 30

        orb_color = (200, 200, 200)
        angle = 0

        if DAY_START <= minutes < DAY_END:
            # Soleil
            orb_color = (255, 255, 0)
            ratio = (minutes - DAY_START) / (DAY_END - DAY_START)
            angle = math.pi + ratio * math.pi
        else:
            # Lune
            orb_color = (200, 200, 200)
            if minutes >= DAY_END:
                ratio = (minutes - DAY_END) / (1440 - DAY_END + DAY_START)
            else:
                ratio = (minutes + (1440 - DAY_END)) / (1440 - DAY_END + DAY_START)
            angle = math.pi + ratio * math.pi

        orb_x = center_x + math.cos(angle) * radius
        orb_y = center_y + math.sin(angle) * radius

        pygame.draw.circle(surface, orb_color, (int(orb_x), int(orb_y)), 10)
