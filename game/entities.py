import pygame

from engine.scene import Camera
from game import isometric


"""
Entities are stored in one big group that draws only those in view of the camera, and in correct order too
"""


class Entities(pygame.sprite.LayeredUpdates):
    def __init__(self, camera: Camera, *sprites, **kwargs):
        super().__init__(*sprites, **kwargs)
        self.camera = camera

    def add(self, *sprites, **kwargs):
        for sprite in sprites:
            sprite.entity_group = self
        super().add(*sprites, **kwargs)

    def draw(self, surface, bgd = None, special_flags = 0):
        sprites: list[pygame.sprite.Sprite] = self.sprites()
        for sprite in sprites:
            if sprite.rect.colliderect(self.camera.rect):
                surface.blit(sprite.image, isometric.world_to_screen_coords(*sprite.rect.topleft, self.camera), special_flags=special_flags)

    def draw_shadows(self, surface, bgd = None, special_flags = 0):
        sprites: list[Entity] = self.sprites()
        for sprite in sprites:
            if sprite.rect.colliderect(self.camera.rect):
                sprite.draw_shadow(surface, self.camera)


class Entity(pygame.sprite.Sprite):
    sound: str = None

    def __init__(self, bottom_offset: int, *groups):
        super().__init__(*groups)
        self.bottom_offset = bottom_offset
        self.entity_group: Entities = None
        self.depth = 0

    def update(self, dt):
        self.depth = self.rect.bottom - self.bottom_offset
        if self.depth != self.layer:
            self.entity_group.change_layer(self, self.depth)

    def draw_shadow(self, surface, camera):
        pass
