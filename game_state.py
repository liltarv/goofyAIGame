from typing import Dict

from config import DEFAULT_COLORS
from model import GameModel


class GameState(GameModel):
    def get_circle_counts(self) -> Dict[str, int]:
        return {color: sum(1 for circle in self.circles if circle.color == color) for color in DEFAULT_COLORS}
