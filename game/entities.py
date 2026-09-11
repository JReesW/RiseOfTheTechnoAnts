import pygame

from engine.scene import Camera
from engine import colors
from game import isometric
from game.types import *


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
                if sprite.health < sprite.max_health:
                    ratio = sprite.health / sprite.max_health
                    x, y, w, h = *isometric.world_to_screen_coords(*sprite.rect.bottomleft, self.camera), sprite.rect.width, 5
                    pygame.draw.rect(surface, colors.slate_gray, (x-1, y-1, w+2, h+2))
                    color = colors.red if ratio <= 0.25 else (colors.orange if ratio <= 0.5 else colors.lime)
                    pygame.draw.rect(surface, color, (x, y, w * ratio, h))

    def draw_shadows(self, surface, bgd = None, special_flags = 0):
        sprites: list[Entity] = self.sprites()
        for sprite in sprites:
            if sprite.rect.colliderect(self.camera.rect):
                sprite.draw_shadow(surface, self.camera)


class Entity(pygame.sprite.Sprite):
    sound: str = None
    max_health: int

    def __init__(self, allegiance: Allegiance, bottom_offset: int, *groups):
        super().__init__(*groups)
        self.health = self.max_health
        self.allegiance = allegiance
        self.bottom_offset = bottom_offset
        self.entity_group: Entities = None
        self.depth = 0

    def update(self, dt):
        self.depth = self.rect.bottom - self.bottom_offset
        if self.depth != self.layer:
            self.entity_group.change_layer(self, self.depth)
        if self.health <= 0:
            self.kill()

    def upgrade_max_health(self, factor: float):
        entity_type = type(self)
        entity_type.max_health *= factor
        self.health = self.max_health

    def draw_shadow(self, surface, camera):
        pass
