import pygame
from pygame.locals import KEYDOWN, K_x, MOUSEBUTTONDOWN, QUIT
from typing import Tuple

from game_state import GameState


class Controller:
    def process_events(self, model: GameState) -> bool:
        for event in pygame.event.get():
            if event.type == QUIT:
                return False
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                self.handle_click(model, event.pos)
            if event.type == KEYDOWN and event.key == K_x:
                model.spawn_circle_without_overlap()
        return True

    def handle_click(self, model: GameState, position: Tuple[int, int]) -> None:
        selected = model.find_circle_at_point(position)
        if selected is None:
            return
        model.count_click(selected.color)
        model.remove_circle(selected)
