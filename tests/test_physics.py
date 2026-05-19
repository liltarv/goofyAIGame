import unittest

from circle import Circle
from config import MIN_RED_SPLIT_RADIUS
from game_state import GameState
from physics import PhysicsEngine


class TestPhysics(unittest.TestCase):
    def test_small_red_does_not_split_on_green_collision(self):
        state = GameState()
        state.circles = []
        red = Circle(position=(100, 100), radius=MIN_RED_SPLIT_RADIUS, color="red", velocity=(20.0, 0.0))
        green = Circle(position=(120, 100), radius=30.0, color="green")
        state.circles.extend([red, green])

        PhysicsEngine().apply_collisions(state)

        red_circles = [circle for circle in state.circles if circle.color == "red"]
        self.assertEqual(len(red_circles), 1)

    def test_green_merge_after_hold_time(self):
        state = GameState()
        state.circles = []
        green_a = Circle(position=(100, 100), radius=30.0, color="green")
        green_b = Circle(position=(130, 100), radius=30.0, color="green")
        state.circles.extend([green_a, green_b])

        engine = PhysicsEngine()
        engine.handle_green_merge(state, 1.0)
        self.assertIn(frozenset({green_a.id, green_b.id}), state.merge_timers)

        engine.handle_green_merge(state, 1.5)
        green_circles = [circle for circle in state.circles if circle.color == "green"]
        self.assertEqual(len(green_circles), 1)


if __name__ == "__main__":
    unittest.main()
