import pygame
from engine.scene import Camera


"""
Entities are stored in one big group that draws only those in view of the camera, and in correct order too
"""


class Entities(pygame.sprite.LayeredUpdates):
    def __init__(self, camera: Camera, *sprites, **kwargs):
        super().__init__(*sprites, **kwargs)
        self.camera = camera

    def draw(self, surface, bgd = None, special_flags = 0):
        sprites: list[pygame.sprite.Sprite] = self.sprites()
        for sprite in sprites:
            if sprite.rect.colliderect(self.camera.rect):
                surface.blit(sprite.image, (sprite.rect.left - self.camera.rect.left, sprite.rect.top - self.camera.rect.top), special_flags=special_flags)


class Entity(pygame.sprite.Sprite):
    def __init__(self, bottom_offset: int, *groups):
        super().__init__(*groups)
        self.bottom_offset = bottom_offset
        self.__layer = 0

    def update(self):
        self.__layer = self.rect.bottom - self.bottom_offset
