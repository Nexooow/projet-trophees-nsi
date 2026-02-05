import math
import random

class PerlinNoise:
    def __init__ (self, seed=None):
        self.seed = seed if seed is not None else random.randint(0, 999999)
        # TODO: implémenter le perlin noise, avec systèle de seed pour avoir un perlin noise différent à chaque partie,
        #  mais le même à chaque fois pour une même seed