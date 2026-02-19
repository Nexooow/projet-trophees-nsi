import math
import random
from typing import List, Optional, Tuple


class Perlin:

    # 8 gradients unitaires 2D répartis uniformément
    gradientS: List[Tuple[float, float]] = [
        (1.0, 0.0),
        (-1.0, 0.0),
        (0.0, 1.0),
        (0.0, -1.0),
        (0.7071067811865476, 0.7071067811865476),
        (-0.7071067811865476, 0.7071067811865476),
        (0.7071067811865476, -0.7071067811865476),
        (-0.7071067811865476, -0.7071067811865476),
    ]

    def __init__(
        self,
        seed: Optional[int] = None,
        scale: float = 1.0,
        octaves: int = 1,
        persistence: float = 0.5,
        lacunarity: float = 2.0,
        offset: Tuple[float, float] = (0.0, 0.0),
        normalize: bool = True,
        threshold: Optional[float] = None,
        threshold_values: Tuple[float, float] = (0.0, 1.0),
        steps: Optional[int] = None,
    ) -> None:
        if seed is None:
            seed = random.randint(1, 2**32 - 1)

        self.seed = seed
        self.rng = random.Random(seed)

        self.scale = max(scale, 1e-9)
        self.octaves = max(1, int(octaves))
        self.persistence = persistence
        self.lacunarity = lacunarity
        self.offset = offset
        self.normalize = normalize
        self.threshold = threshold
        self.threshold_values = threshold_values
        self.steps = steps

        # table de permutation
        perm = list(range(256))
        self.rng.shuffle(perm)
        self.perm: List[int] = perm + perm

    def fade(self, t: float) -> float:
        """
        Fonction de lissage
        """
        return t * t * t * (t * (t * 6.0 - 15.0) + 10.0)

    def lerp(self, a: float, b: float, t: float) -> float:
        """Interpolation linéaire entre a et b"""
        return a + t * (b - a)

    def gradient(self, hash_val: int, x: float, y: float) -> float:
        """
        Produit scalaire entre le gradient sélectionné par hash_val et le
        vecteur (x, y)
        """
        gx, gy = self.gradientS[hash_val % len(self.gradientS)]
        return gx * x + gy * y

    def raw_noise(self, x: float, y: float) -> float:
        """
        Bruit de Perlin 2D classique à (x, y)
        """
        # Coin inférieur gauche de la cellule (en coordonnées entières)
        xi: int = math.floor(x) & 255
        yi: int = math.floor(y) & 255

        # Position fractionnaire dans la cellule
        xf: float = x - math.floor(x)
        yf: float = y - math.floor(y)

        # Courbes de fade pour l'interpolation
        u: float = self.fade(xf)
        v: float = self.fade(yf)

        # Hash des quatre coins de la cellule
        aa: int = self.perm[self.perm[xi] + yi]
        ab: int = self.perm[self.perm[xi] + yi + 1]
        ba: int = self.perm[self.perm[xi + 1] + yi]
        bb: int = self.perm[self.perm[xi + 1] + yi + 1]

        # Interpolation bilinéaire des produits scalaires
        x1: float = self.lerp(
            self.gradient(aa, xf, yf),
            self.gradient(ba, xf - 1.0, yf),
            u,
        )
        x2: float = self.lerp(
            self.gradient(ab, xf, yf - 1.0),
            self.gradient(bb, xf - 1.0, yf - 1.0),
            u,
        )

        return self.lerp(x1, x2, v)

    def noise(self, x: float, y: float) -> float:
        """
        Calcule le bruit de Perlin à la position (x, y) en appliquant
        toutes les options de configuration (normalisation, paliers ...).
        """
        amplitude: float = 1.0
        frequency: float = 1.0
        value: float = 0.0
        max_amplitude: float = 0.0

        for _ in range(self.octaves):
            sample_x = (x * frequency / self.scale) + self.offset[0]
            sample_y = (y * frequency / self.scale) + self.offset[1]
            value += self.raw_noise(sample_x, sample_y) * amplitude
            max_amplitude += amplitude
            amplitude *= self.persistence
            frequency *= self.lacunarity

        # normaliser par la somme des amplitudes pour rester dans [-1, 1]
        value /= max_amplitude

        if self.normalize: # value prend les valeurs de [-1, 1], si normalize est vrai, value prend les valeurs de [0, 1]
            value = (value + 1.0) * 0.5
            value = max(0.0, min(1.0, value))

        # seuil binaire entre les valeurs données en param
        if self.threshold is not None:
            low, high = self.threshold_values
            value = low if value < self.threshold else high

        # créer N paliers (N=steps) pour faciliter l'implémentation pour la carte (par exemple)
        elif self.steps is not None and self.steps > 1:
            value = math.floor(value * self.steps) / (self.steps - 1)
            value = max(0.0, min(1.0, value))

        return value
