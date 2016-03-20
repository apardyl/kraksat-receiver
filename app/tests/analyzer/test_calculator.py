import unittest
import random
import math

from app.analyzer.calculator import Calculator
from app.analyzer.collector import Collector

earth_mass = 5.97219e24
earth_radius = 6.3781e6


def acceleration(height, rad=earth_radius, mas=earth_mass):
    return Calculator.G * mas /\
           (rad + height) ** 2


def temperature(height):
    return -6.49 * height / 1000 + 273.15 + 20


def temperature_with_error(height):
    return temperature(height) + 0.01 * random.uniform(-1, 1)


def pressure(height):
    numerator = -((9.80665 + acceleration(height))/2) * 0.0289644 * height
    denominator = 8.31432 * ((temperature(height) + 273.15 + 20)/2)
    return 101325 * math.exp(numerator/denominator)


def pressure_with_error(height):
    return pressure(height) + 10 * random.uniform(-1, 1)


class CalculatorTest(unittest.TestCase):
    def setUp(self):
        self.collector = Collector()
        self.calc = Calculator(self.collector)

    def test_calculate(self):
        for i in range(100000, 0, -3):
            self.collector.add_value(1000 - i, 'altitude', i)
            self.collector.add_value(1000 - i, 'acceleration', acceleration(i))
        radius, mass = self.calc.calculate_radius_mass()
        self.assertAlmostEqual(radius, earth_radius, delta=1e4)
        self.assertAlmostEqual(mass / radius ** 2,
                               earth_mass / earth_radius ** 2, delta=1e7)

    def test_calculate_with_random(self):
        random_mass = random.uniform(1e10, 1e12)
        random_radius = random.uniform(1e5, 1e7)
        for i in range(1000, 0, -3):
            self.collector.add_value(1000 - i, 'altitude', i)
            self.collector.add_value(1000 - i, 'acceleration', acceleration(
                    i, random_radius, random_mass))
        radius, mass = self.calc.calculate_radius_mass()
        self.assertAlmostEqual(radius, random_radius, delta=1e4)
        self.assertAlmostEqual(mass / radius ** 2,
                               random_mass / random_radius ** 2, delta=1e7)

    def test_molar_mass(self):
        for i in range(1000, 0, -3):
            self.collector.add_value(1000 - i, 'altitude', i)
            self.collector.add_value(1000 - i, 'acceleration', acceleration(i))
            self.collector.add_value(1000 - i, 'pressure',
                                     pressure_with_error(i))
            self.collector.add_value(1000 - i, 'temperature',
                                     temperature_with_error(i))
        molar_mass = self.calc.calculate_molar_mass()
        self.assertIsNotNone(molar_mass)