import pygame
from engine import image


class HoneySwirl(pygame.sprite.Sprite):
    def __init__(self, position: tuple[int, int], clockwise: bool):
        super().__init__()
        self.position = position
        self.clockwise = clockwise
        self.angle = 0

        self.base_image = pygame.transform.flip(image.load_image("honeyswirl"), flip_x=not clockwise, flip_y=False)
        self.rect = pygame.Rect(64, 64, *position)

    def update(self, *args, **kwargs):
        self.angle += -3 if self.clockwise else 3

        self.image = pygame.transform.rotate(self.base_image, angle=self.angle)
        self.rect = self.image.get_rect(center=self.position)