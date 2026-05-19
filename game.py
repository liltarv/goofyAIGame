import pygame

from controller import Controller
from game_state import GameState
from physics import PhysicsEngine
from view import Renderer


class Game:
    """High-level game orchestration.

    This class wires together the mutable game state, input controller,
    physics engine, and renderer so that the main entry point remains small.
    """

    def __init__(self) -> None:
        pygame.init()
        self.model = GameState()
        self.screen = pygame.display.set_mode((self.model.window_width, self.model.window_height))
        pygame.display.set_caption("Goofy AI Game")
        self.clock = pygame.time.Clock()
        self.controller = Controller()
        self.renderer = Renderer(self.model)
        self.renderer.initialize()
        self.physics = PhysicsEngine()
        self.running = True

    def run(self) -> None:
        while self.running:
            dt = self.clock.tick(60) / 1000.0
            self.running = self.controller.process_events(self.model)
            self.physics.update(self.model, dt)
            self.renderer.draw(self.screen)
            pygame.display.flip()

        pygame.quit()
