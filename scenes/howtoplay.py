import pygame

from engine.scene import Scene
from engine import director, image


class HowToPlay(Scene):
    def __init__(self, *args, **kwargs):
        self.background = image.load_image("howtoplay")
        self.rect = pygame.Rect(1444, 953, 406, 111)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.rect.collidepoint(pygame.mouse.get_pos()):
                    director.change_scene("Loading")

    def render(self, surface):
        surface.blit(self.background)
