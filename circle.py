import math
import random
from typing import Tuple

from config import GREEN_MASS_MULTIPLIER, MAX_RED_SPEED, MIN_RED_SPEED


class Circle:
    next_id = 1

    def __init__(self, position: Tuple[float, float], radius: float, color: str, velocity: Tuple[float, float] = (0.0, 0.0)):
        self.id = Circle.next_id
        Circle.next_id += 1
        self.position = [float(position[0]), float(position[1])]
        self.radius = float(radius)
        self.color = color
        self.velocity = [float(velocity[0]), float(velocity[1])]
        self.mass = self.compute_mass()

    @property
    def area(self) -> float:
        return math.pi * self.radius * self.radius

    def compute_mass(self) -> float:
        base_mass = self.area
        return base_mass * GREEN_MASS_MULTIPLIER if self.color == "green" else base_mass

    def distance_to(self, other: "Circle") -> float:
        dx = self.position[0] - other.position[0]
        dy = self.position[1] - other.position[1]
        return math.hypot(dx, dy)

    def overlaps(self, other: "Circle") -> bool:
        return self.distance_to(other) < (self.radius + other.radius)

    def contains_point(self, point: Tuple[int, int]) -> bool:
        dx = self.position[0] - point[0]
        dy = self.position[1] - point[1]
        return dx * dx + dy * dy <= self.radius * self.radius

    def move(self, dt: float) -> None:
        self.position[0] += self.velocity[0] * dt
        self.position[1] += self.velocity[1] * dt

    def set_random_drift(self, min_speed: float = MIN_RED_SPEED, max_speed: float = MAX_RED_SPEED) -> None:
        angle = random.uniform(0, math.tau)
        speed = random.uniform(min_speed, max_speed)
        self.velocity[0] = math.cos(angle) * speed
        self.velocity[1] = math.sin(angle) * speed

    def bounce_off_walls(self, bounds: Tuple[int, int]) -> None:
        max_x, max_y = bounds
        x, y = self.position
        vx, vy = self.velocity

        if x - self.radius < 0:
            self.position[0] = self.radius
            self.velocity[0] = abs(vx)
        elif x + self.radius > max_x:
            self.position[0] = max_x - self.radius
            self.velocity[0] = -abs(vx)

        if y - self.radius < 0:
            self.position[1] = self.radius
            self.velocity[1] = abs(vy)
        elif y + self.radius > max_y:
            self.position[1] = max_y - self.radius
            self.velocity[1] = -abs(vy)

    def clamp_velocity(self, min_speed: float = MIN_RED_SPEED, max_speed: float = MAX_RED_SPEED) -> None:
        vx, vy = self.velocity
        speed = math.hypot(vx, vy)
        if speed < min_speed:
            self.set_random_drift(min_speed, max_speed)
        elif speed > max_speed:
            scale = max_speed / speed
            self.velocity[0] *= scale
            self.velocity[1] *= scale
