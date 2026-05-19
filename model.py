import random
from typing import Dict, List, Optional, Tuple

from circle import Circle
from config import DEFAULT_COLORS, INITIAL_CIRCLE_COUNT, MAX_RADIUS, MIN_RADIUS, PLAY_HEIGHT, PLAY_WIDTH, TABLE_WIDTH


class GameModel:
    def __init__(self, play_width: int = PLAY_WIDTH, play_height: int = PLAY_HEIGHT, table_width: int = TABLE_WIDTH):
        self.play_width = play_width
        self.play_height = play_height
        self.table_width = table_width
        self.window_width = self.play_width + self.table_width
        self.window_height = self.play_height
        self.circles: List[Circle] = []
        self.click_counts: Dict[str, int] = {color: 0 for color in DEFAULT_COLORS}
        self.merge_timers: Dict[frozenset, float] = {}
        self.spawn_initial_circles()

    def spawn_initial_circles(self, count: int = INITIAL_CIRCLE_COUNT) -> None:
        for _ in range(count):
            self.add_random_circle()

    def add_random_circle(self, color: Optional[str] = None, radius: Optional[float] = None) -> Optional[Circle]:
        color = color or random.choice(DEFAULT_COLORS)
        radius = radius or random.uniform(MIN_RADIUS, MAX_RADIUS)
        position = self.find_non_overlapping_position(radius)
        if position is None:
            return None
        circle = Circle(position=position, radius=radius, color=color)
        if circle.color == "red":
            circle.set_random_drift()
        self.circles.append(circle)
        return circle

    def find_non_overlapping_position(self, radius: float, max_attempts: int = 200) -> Optional[Tuple[float, float]]:
        for _ in range(max_attempts):
            x = random.uniform(radius, self.play_width - radius)
            y = random.uniform(radius, self.play_height - radius)
            candidate = Circle(position=(x, y), radius=radius, color="blue")
            if all(not candidate.overlaps(circle) for circle in self.circles):
                return x, y
        return None

    def remove_circle(self, circle: Circle) -> None:
        self.circles = [item for item in self.circles if item.id != circle.id]
        self._cleanup_merge_timers_for(circle)

    def _cleanup_merge_timers_for(self, circle: Circle) -> None:
        expired = [pair for pair in self.merge_timers if circle.id in pair]
        for pair in expired:
            self.merge_timers.pop(pair, None)

    def find_circle_at_point(self, point: Tuple[int, int]) -> Optional[Circle]:
        for circle in reversed(self.circles):
            if circle.contains_point(point):
                return circle
        return None

    def count_click(self, color: str) -> None:
        if color in self.click_counts:
            self.click_counts[color] += 1
        else:
            self.click_counts[color] = 1

    def spawn_circle_without_overlap(self) -> Optional[Circle]:
        return self.add_random_circle()

    def reset_merge_timers(self) -> None:
        self.merge_timers.clear()
