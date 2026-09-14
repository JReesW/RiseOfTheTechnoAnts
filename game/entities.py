import pygame

from engine.scene import Camera
from engine import colors, image
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
                if sprite.name == "worker" and sprite.carrying is not None:
                    img = image.load_image(f"icons/{sprite.carrying}")
                    r = img.get_rect(midbottom=isometric.world_to_screen_coords(*sprite.rect.midtop, self.camera))
                    surface.blit(img, r)

    def draw_shadows(self, surface, bgd = None, special_flags = 0):
        sprites: list[Entity] = self.sprites()
        for sprite in sprites:
            if sprite.rect.colliderect(self.camera.rect):
                sprite.draw_shadow(surface, self.camera)


class Entity(pygame.sprite.Sprite):
    name: str
    sound: str = None
    max_health: int
    is_implosion = False
    display_name: str

    def __init__(self, allegiance: Allegiance, bottom_offset: int, *groups):
        super().__init__(*groups)
        self.health = self.max_health
        self.allegiance = allegiance
        self.bottom_offset = bottom_offset
        self.entity_group: Entities = None
        self.depth = 0
        self.dead = False

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

    def hurt(self, damage: int):
        self.health -= damage

    def draw_shadow(self, surface, camera):
        pass

    def kill(self, silent: bool = False):
        if not self.is_implosion and not silent:
            self.entity_group.add(Implosion(self.rect, self.image))
        self.dead = True
        super().kill()


class Implosion(Entity):
    name = "implosion"
    is_implosion = True
    max_health = 1

    def __init__(self, rect: pygame.Rect, img: pygame.Surface, *groups):
        super().__init__(Allegiance.Nature, 0, *groups)
        self.t = 0
        # self.rect = rect
        self.width = rect.width
        self.blast_point = 30
        self.total_time = 90
        self.building_image = img.copy()
        self.image = pygame.Surface((self.width * 2, self.width * 2), pygame.SRCALPHA)
        self.rect = pygame.Rect(0, 0, self.width * 2, self.width * 2).move_to(center=rect.center)

        # animation parameters
        self.circle_a = 0
        self.circle_r = 0
        self.ring_a = 0
        self.ring_r = 0
        self.image_a = 0

    def update(self, dt):
        if self.t < self.blast_point:
            self.circle_a = int(pygame.math.remap(0, self.blast_point, 0, 255, self.t))
            self.circle_r = int(pygame.math.remap(0, self.blast_point, self.width, 0, self.t))
            if self.t < self.blast_point//3:
                self.image_a = int(pygame.math.remap(0, self.blast_point//3, 255, 0, self.t))
        elif self.t < self.total_time:
            self.circle_a = int(pygame.math.remap(self.blast_point, self.total_time, 255, 0, self.t))
            self.circle_r = int(pygame.math.remap(self.blast_point, self.total_time, 0, self.width * 1.5, self.t))
            self.ring_a = int(pygame.math.remap(self.blast_point, self.total_time, 255, 0, self.t))
            self.ring_r = int(pygame.math.remap(self.blast_point, self.total_time, 0, self.width * 2, self.t))
        else:
            self.kill()

        self.image.fill((0, 0, 0, 0))
        circle = pygame.transform.scale(image.load_image("technical/implosion"), (self.circle_r, self.circle_r))
        circle.set_alpha(self.circle_a)
        ring = pygame.transform.scale(image.load_image("technical/implosion_ring"), (self.ring_r, self.ring_r))
        ring.set_alpha(self.ring_a)
        self.building_image.set_alpha(self.image_a)
        if self.t < self.blast_point//3:
            self.image.blit(self.building_image, self.building_image.get_rect(center=self.image.get_rect().center))
        self.image.blit(circle, circle.get_rect(center=self.image.get_rect().center))
        if self.t >= self.blast_point:
            self.image.blit(ring, ring.get_rect(center=self.image.get_rect().center))

        self.t += 1
        return super().update(dt)
