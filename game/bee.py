import pygame
from engine import image
from math import sin, cos, pi, dist, degrees


class Bee(pygame.sprite.Sprite):
    def __init__(self, position: tuple[int, int], angle: float):
        super().__init__()
        self.position = pygame.Vector2(position)
        self.direction = pygame.Vector2(0, 0)
        self.direction.from_polar((1, angle))
        self.ticks = 0
        self.rect = pygame.Rect(32, 32, 0, 0)
        self.image = image.load_image("bee1")

    def update(self, repels: list[tuple[int, int]], *args, **kwargs):
        self.ticks += 1

        for repel in repels:
            d = dist(self.position, repel)
            if d < 100:
                v_repel = pygame.math.Vector2(self.position[0] - repel[0], self.position[1] - repel[1]).normalize()
                inv_d = (100 - d) / 500
                self.direction = (self.direction + v_repel * inv_d).normalize()

        # print(self.direction)
        self.position += self.direction * 5
        self.rect.center = self.position

        self.image = image.load_image(f"bee{(self.ticks % 4) // 2}", rotation=-self.direction.angle)


class BeeStream(pygame.sprite.Group):
    def __init__(self, *sprites):
        super().__init__(*sprites)
