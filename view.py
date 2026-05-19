import pygame
from typing import Tuple

from config import COLOR_MAP, DEFAULT_COLORS
from game_state import GameState


class Renderer:
    def __init__(self, model: GameState):
        self.model = model
        self.background_color = (24, 28, 35)
        self.grid_color = (45, 50, 63)
        self.text_color = (240, 240, 240)
        self.table_background = (28, 34, 46)
        self.font = None

    def initialize(self) -> None:
        self.font = pygame.font.Font(None, 28)

    def draw(self, screen: pygame.Surface) -> None:
        screen.fill(self.background_color)
        self.draw_playfield(screen)
        self.draw_table(screen)

    def draw_playfield(self, screen: pygame.Surface) -> None:
        for circle in self.model.circles:
            color = COLOR_MAP.get(circle.color, (200, 200, 200))
            pygame.draw.circle(
                screen,
                color,
                (int(circle.position[0]), int(circle.position[1])),
                int(circle.radius),
            )
        border_rect = pygame.Rect(0, 0, self.model.play_width, self.model.play_height)
        pygame.draw.rect(screen, self.grid_color, border_rect, 3)

    def draw_table(self, screen: pygame.Surface) -> None:
        if self.font is None:
            self.initialize()
        table_x = self.model.play_width + 10
        pygame.draw.rect(
            screen,
            self.table_background,
            pygame.Rect(self.model.play_width, 0, self.model.table_width, self.model.window_height),
        )
        circle_counts = self.model.get_circle_counts()

        heading = self.font.render("Circle Counts", True, self.text_color)
        screen.blit(heading, (table_x, 20))
        y = 60
        for color in DEFAULT_COLORS:
            text = f"{color.title()}: {circle_counts.get(color, 0)}"
            rendered = self.font.render(text, True, COLOR_MAP.get(color, self.text_color))
            screen.blit(rendered, (table_x, y))
            y += 32

        click_heading = self.font.render("Clicks", True, self.text_color)
        screen.blit(click_heading, (table_x, y + 10))
        y += 44
        for color in DEFAULT_COLORS:
            text = f"{color.title()}: {self.model.click_counts.get(color, 0)}"
            rendered = self.font.render(text, True, COLOR_MAP.get(color, self.text_color))
            screen.blit(rendered, (table_x, y))
            y += 32

        help_lines = [
            "Left-click a circle to remove it.",
            'Press "x" to spawn a circle.',
        ]
        y += 20
        for line in help_lines:
            rendered = self.font.render(line, True, self.text_color)
            screen.blit(rendered, (table_x, y))
            y += 28
