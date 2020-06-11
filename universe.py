from tkinter import *
import math
STAR_COLORS = [(247, 210, 35), (53, 218, 247), (247, 146, 53),
               (240, 219, 218), (54, 77, 231)]


class Planet:
    def __init__(self):
        self.distance = 0
        self.diameter = 0
        self.foliage = 0
        self.minerals = 0
        self.water = 0
        self.gases = 0
        self.temperature = 0
        self.population = 0
        self.ring = False
        self.moons = []

    def __str__(self):
        s = ""
        for name, val in vars(self).items():
            s += f"{name}: {val}\n"
        return s

    def __repr__(self):
        return self.__str__()


class StarSystem:
    def __init__(self, x, y, gen_full_system=False):
        self.x = x
        self.y = y
        self.gen_full_system = gen_full_system
        self.planets = []

        # set random seed based on location
        self.seed = (self.x & 0xFFFF) << 16 | (self.y & 0xFFF)

        # not all locations have a star
        self.star_exists = (self.rnd_int(0, 20) == 1)
        if not self.star_exists:
            return

        # generate star
        self.star_diameter = self.rnd_double(10, 40)
        self.star_color = STAR_COLORS[self.rnd_int(0, 4)]

        # when looking at the galaxy map, we don't need full system
        if not self.gen_full_system:
            return

        # generate planets
        distance_from_star = self.rnd_double(60, 200)
        num_planets = self.rnd_int(0, 10)

        for i in range(num_planets):
            p = Planet()
            p.distance = distance_from_star
            distance_from_star += self.rnd_double(20, 200)
            p.diameter = self.rnd_double(4, 20)
            # temperature decreases as distance increases
            p.temperature = 1000 - p.distance * 3
            # foliage is normally distributed, centered on 20 degrees C
            p.foliage = (math.e ** (-0.02 * (p.temperature - 20) ** 2))
            # bigger diameter means more minerals due to the square-cube law
            p.minerals = (p.diameter ** 2) / 400
            # more foliage means more gases and water
            p.gases = p.foliage
            p.water = p.foliage

            # normalize to 100%
            correction_factor = 1 / (p.foliage + p.minerals + p.gases + p.water)
            p.foliage *= correction_factor
            p.minerals *= correction_factor
            p.gases *= correction_factor
            p.water *= correction_factor

            # population is random for now, negative lower bound so
            # 20% of planets have no population
            p. population = max(self.rnd_int(-5000000, 20000000), 0)

            # 20% of planets have a ring
            p.ring = (self.rnd_int(0, 10) == 1)

            num_moons = max(self.rnd_int(-5, 5), 0)
            # a moon is just a diameter for now
            for j in range(num_moons):
                p.moons.append(self.rnd_double(1, 5))

            self.planets.append(p)

    def rnd(self):
        # Lehmer 64-bit generator
        self.seed = self.seed * 48271 % 0x7fffffff
        return self.seed

    def rnd_int(self, mi, ma):
        return (self.rnd() % (ma - mi)) + mi

    def rnd_double(self, mi, ma):
        return (self.rnd() / 2147483647) * (ma - mi)

    def __str__(self):
        return f"x: {self.x}\ny: {self.y}\ngen_full_system: {self.gen_full_system}\nseed: {self.seed}"

    def __repr__(self):
        return self.__str__()
