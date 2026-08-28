import pygame
from engine.scene import Scene
from engine import colors, image, mouse

from game.bee import Bee, BeeStream
from game.swirl import HoneySwirl


class Game(Scene):
    def __init__(self, *args, **kwargs):
        image.load_image("bee0")
        image.load_image("bee1")

        self.ticks = 0
        self.space_held = False

        self.bees = BeeStream()
        # self.swirls = pygame.sprite.Group(
        #     HoneySwirl((400, 400), True),
        #     HoneySwirl((1000, 800), False)
        # )
        self.repels = [
            (1400, 700),
            (800, 200)
        ]
    
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.space_held = not self.space_held
                
    def update(self, dt):
        self.ticks += 1

        if self.space_held and self.ticks % 6 == 0:
            x, y = mouse.mousepos()
            self.bees.add(Bee((x-16, y-16), 0))

        self.bees.update(self.repels)
        # self.swirls.update() 

    def render(self, surface):
        surface.fill(colors.forest_green)

        self.bees.draw(surface)
        for repel in self.repels:
            pygame.draw.circle(surface, colors.red, repel, 10)
        # self.swirls.draw(surface)