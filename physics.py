import math
import random
from typing import List

from circle import Circle
from config import (
    GRAVITY_CONSTANT,
    MAX_RED_SPLIT_COUNT,
    MAX_RED_SPEED,
    MERGE_DISTANCE,
    MERGE_HOLD_TIME,
    MIN_RADIUS,
    MIN_RED_SPEED,
    MIN_RED_SPLIT_RADIUS,
)
from game_state import GameState


class PhysicsEngine:

    def update(self, model: GameState, dt: float) -> None:
        self.apply_green_gravity(model, dt)
        self.move_circles(model, dt)
        self.apply_collisions(model)
        self.handle_green_merge(model, dt)

    def apply_green_gravity(self, model: GameState, dt: float) -> None:
        greens = [c for c in model.circles if c.color == "green"]
        for i, circle_a in enumerate(greens):
            for circle_b in greens[i + 1 :]:
                displacement_x = circle_b.position[0] - circle_a.position[0]
                displacement_y = circle_b.position[1] - circle_a.position[1]
                distance_squared = displacement_x * displacement_x + displacement_y * displacement_y
                if distance_squared < 1.0:
                    continue
                force = GRAVITY_CONSTANT * circle_a.mass * circle_b.mass / distance_squared
                distance = math.sqrt(distance_squared)
                acceleration_a = force / circle_a.mass
                acceleration_b = force / circle_b.mass
                direction_x = displacement_x / distance
                direction_y = displacement_y / distance
                circle_a.velocity[0] += direction_x * acceleration_a * dt
                circle_a.velocity[1] += direction_y * acceleration_a * dt
                circle_b.velocity[0] -= direction_x * acceleration_b * dt
                circle_b.velocity[1] -= direction_y * acceleration_b * dt

    def move_circles(self, model: GameState, dt: float) -> None:
        for circle in model.circles:
            if circle.color == "red" and math.hypot(circle.velocity[0], circle.velocity[1]) < 10.0:
                circle.set_random_drift(MIN_RED_SPEED, MAX_RED_SPEED)
            circle.move(dt)
            circle.bounce_off_walls((model.play_width, model.play_height))
            if circle.color == "red":
                circle.clamp_velocity(MIN_RED_SPEED, MAX_RED_SPEED)

    def apply_collisions(self, model: GameState) -> None:
        circles = model.circles
        collided_ids = set()
        for i, circle_a in enumerate(circles):
            for circle_b in circles[i + 1 :]:
                if circle_a.id in collided_ids or circle_b.id in collided_ids:
                    continue
                if not circle_a.overlaps(circle_b):
                    continue
                if self._handle_red_green_collision(circle_a, circle_b, model):
                    collided_ids.add(circle_a.id)
                    collided_ids.add(circle_b.id)
                    continue
                self.resolve_elastic_collision(circle_a, circle_b)
                if circle_a.color == "red" or circle_b.color == "red":
                    self._randomize_red_after_collision(circle_a)
                    self._randomize_red_after_collision(circle_b)

    def _handle_red_green_collision(self, circle_a: Circle, circle_b: Circle, model: GameState) -> bool:
        red_circle = None
        green_circle = None
        if circle_a.color == "red" and circle_b.color == "green":
            red_circle = circle_a
            green_circle = circle_b
        elif circle_b.color == "red" and circle_a.color == "green":
            red_circle = circle_b
            green_circle = circle_a
        if red_circle is None:
            return False
        if red_circle.radius <= MIN_RED_SPLIT_RADIUS:
            return False
        self.split_red_circle(red_circle, model)
        return True

    def split_red_circle(self, circle: Circle, model: GameState) -> None:
        split_count = min(MAX_RED_SPLIT_COUNT, max(2, int(circle.area / 900.0)))
        split_area = circle.area / split_count
        split_radius = max(MIN_RADIUS, math.sqrt(split_area / math.pi))
        original_position = tuple(circle.position)
        model.remove_circle(circle)
        for _ in range(split_count):
            offset_angle = random.uniform(0, math.tau)
            offset_distance = random.uniform(circle.radius * 0.4, circle.radius * 1.2)
            spawn_x = original_position[0] + math.cos(offset_angle) * offset_distance
            spawn_y = original_position[1] + math.sin(offset_angle) * offset_distance
            spawn_x = min(max(split_radius, spawn_x), model.play_width - split_radius)
            spawn_y = min(max(split_radius, spawn_y), model.play_height - split_radius)
            new_circle = Circle(
                position=(spawn_x, spawn_y),
                radius=split_radius,
                color="red",
                velocity=(math.cos(offset_angle) * random.uniform(MIN_RED_SPEED, MAX_RED_SPEED), math.sin(offset_angle) * random.uniform(MIN_RED_SPEED, MAX_RED_SPEED)),
            )
            model.circles.append(new_circle)

    def resolve_elastic_collision(self, a: Circle, b: Circle) -> None:
        dx = b.position[0] - a.position[0]
        dy = b.position[1] - a.position[1]
        distance = math.hypot(dx, dy)
        if distance == 0:
            distance = a.radius + b.radius
            dx = distance
            dy = 0.0
        overlap = 0.5 * (a.radius + b.radius - distance + 1.0)
        if overlap > 0:
            nx = dx / distance
            ny = dy / distance
            a.position[0] -= nx * overlap
            a.position[1] -= ny * overlap
            b.position[0] += nx * overlap
            b.position[1] += ny * overlap
        nx = dx / distance
        ny = dy / distance
        dvx = a.velocity[0] - b.velocity[0]
        dvy = a.velocity[1] - b.velocity[1]
        relative_speed = dvx * nx + dvy * ny
        if relative_speed > 0:
            return
        restitution = 0.8
        impulse = -(1 + restitution) * relative_speed
        impulse /= (1 / a.mass) + (1 / b.mass)
        a.velocity[0] += (impulse * nx) / a.mass
        a.velocity[1] += (impulse * ny) / a.mass
        b.velocity[0] -= (impulse * nx) / b.mass
        b.velocity[1] -= (impulse * ny) / b.mass

    def _randomize_red_after_collision(self, circle: Circle) -> None:
        if circle.color == "red":
            angle = random.uniform(0, math.tau)
            speed = random.uniform(MIN_RED_SPEED, MAX_RED_SPEED)
            circle.velocity[0] = math.cos(angle) * speed
            circle.velocity[1] = math.sin(angle) * speed

    def handle_green_merge(self, model: GameState, dt: float) -> None:
        green_circles = [c for c in model.circles if c.color == "green"]
        active_pairs = set()
        for i, circle_a in enumerate(green_circles):
            for circle_b in green_circles[i + 1 :]:
                pair = frozenset({circle_a.id, circle_b.id})
                distance = circle_a.distance_to(circle_b)
                if distance < MERGE_DISTANCE:
                    active_pairs.add(pair)
                    current_time = model.merge_timers.get(pair, 0.0) + dt
                    model.merge_timers[pair] = current_time
                    if current_time >= MERGE_HOLD_TIME:
                        self.merge_green_circles(circle_a, circle_b, model)
                        return
                elif pair in model.merge_timers:
                    model.merge_timers.pop(pair, None)
        expired = [pair for pair in model.merge_timers if pair not in active_pairs]
        for pair in expired:
            model.merge_timers.pop(pair, None)

    def merge_green_circles(self, circle_a: Circle, circle_b: Circle, model: GameState) -> None:
        if circle_a.id == circle_b.id:
            return
        total_area = circle_a.area + circle_b.area
        new_radius = math.sqrt(total_area / math.pi)
        mass_weight = circle_a.mass + circle_b.mass
        new_velocity = [0.0, 0.0]
        if mass_weight > 0:
            new_velocity[0] = (circle_a.velocity[0] * circle_a.mass + circle_b.velocity[0] * circle_b.mass) / mass_weight
            new_velocity[1] = (circle_a.velocity[1] * circle_a.mass + circle_b.velocity[1] * circle_b.mass) / mass_weight
        new_position = [
            (circle_a.position[0] * circle_a.mass + circle_b.position[0] * circle_b.mass) / mass_weight,
            (circle_a.position[1] * circle_a.mass + circle_b.position[1] * circle_b.mass) / mass_weight,
        ]
        model.remove_circle(circle_a)
        model.remove_circle(circle_b)
        merged = Circle(position=tuple(new_position), radius=new_radius, color="green", velocity=tuple(new_velocity))
        model.circles.append(merged)
        model.reset_merge_timers()
