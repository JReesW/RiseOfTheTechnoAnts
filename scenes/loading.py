import pygame

from engine.scene import Scene
from engine import director, text, colors


class Loading(Scene):
    def __init__(self, *args, **kwargs):
        self.go = False

    def update(self, dt):
        if not self.go:
            self.go = True
        else:
            director.change_scene("Game")

    def render(self, surface):
        surface.fill(colors.black)
        surf, rect = text.render("Loading...", colors.white, "Arial", 48, True)
        rect.bottomright = (1890, 1050)
        surface.blit(surf, rect)
