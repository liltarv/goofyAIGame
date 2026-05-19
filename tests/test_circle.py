import math
import unittest

from circle import Circle
from config import GREEN_MASS_MULTIPLIER


class TestCircle(unittest.TestCase):
    def test_compute_mass_for_green_circle(self):
        circle = Circle(position=(0, 0), radius=10.0, color="green")
        expected_mass = circle.area * GREEN_MASS_MULTIPLIER
        self.assertAlmostEqual(circle.mass, expected_mass)

    def test_circle_overlap(self):
        circle_a = Circle(position=(100, 100), radius=30, color="red")
        circle_b = Circle(position=(130, 100), radius=30, color="blue")
        self.assertTrue(circle_a.overlaps(circle_b))
        circle_b.position = [200.0, 200.0]
        self.assertFalse(circle_a.overlaps(circle_b))


if __name__ == "__main__":
    unittest.main()
