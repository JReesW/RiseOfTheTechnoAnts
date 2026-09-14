import pygame

from engine.scene import Scene
from engine import director


class Fade(Scene):
    def __init__(self, out: Scene, into: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.out = out
        self.into = director.get_scene(into)(*args, **kwargs)
        self.ticks = 0
        self.fade = pygame.Surface((1920, 1080), pygame.SRCALPHA)

    def update(self, dt):
        self.ticks += 1
        alpha = pygame.math.remap(0, 60, 0, 255, self.ticks) if self.ticks <= 60 else pygame.math.remap(61, 120, 255, 0, self.ticks)
        self.fade.fill((0, 0, 0, alpha))
        if self.ticks >= 120: director.scene = self.into

    def render(self, surface):
        scene = self.out if self.ticks <= 60 else self.into
        scene.render(surface)
        surface.blit(self.fade) 
