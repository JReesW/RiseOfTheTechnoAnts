import pygame

from engine import image
from engine.scene import Camera
from game import isometric
from game.entities import Entity

import enum


class Area(enum.IntEnum):
    OneByOne = 1
    TwoByTwo = 2
    ThreeByThree = 3


# Add right offset too for 2x2 buildings?
class Building(Entity):
    def __init__(self, pos: tuple[int, int], image_name: str, bottom_offset: int, area: Area, *groups):
        super().__init__(bottom_offset, *groups)
        self.pos = pos
        self.image = image.load_image(image_name)
        self.area = area
        rect = pygame.Rect(0, 0, *self.image.size)
        px, py = isometric.tile_to_world_coords(*self.pos)
        ox = 80 if area == Area.TwoByTwo else 0  # offset the X from tile center on TwoByTwo
        self.rect = rect.move_to(centerx = px + ox, bottom = py + self.bottom_offset)

        self.shadow = image.load_image(f"shadow{area}")

    def occupies_tile(self, tile: tuple[int, int]) -> bool:
        """
        Return whether this building occupies the given tile
        """
        tx, ty = tile
        px, py = self.pos
        if self.area == Area.OneByOne:
            return px == tx and py == ty
        elif self.area == Area.TwoByTwo:
            return px <= tx <= px + 1 and py - 1 <= ty <= py
        return px - 1 <= tx <= px + 1 and py - 1 <= ty <= py + 1

    def get_center(self):
        """
        Get the world coord of this building's center
        """
        px, py = isometric.tile_to_world_coords(*self.pos)
        if self.area == Area.TwoByTwo:
            return px + 80, py
        return px, py

    def draw_shadow(self, surface: pygame.Surface, camera: Camera):
        r = pygame.Rect(0, 0, *self.shadow.size).move_to(center=isometric.world_to_screen_coords(*self.get_center(), camera))
        surface.blit(self.shadow, r)


class Nexus(Building):
    def __init__(self, pos: tuple[int, int], *groups):
        super().__init__(pos, "nexus", 84, Area.ThreeByThree, *groups)


class Pod(Building):
    def __init__(self, pos: tuple[int, int], *groups):
        super().__init__(pos, "nexus2", 42, Area.TwoByTwo, *groups)


class Tower(Building):
    def __init__(self, pos: tuple[int, int], *groups):
        super().__init__(pos, "nexus1", 25, Area.OneByOne, *groups)


class Farm(Building):
    def __init__(self, pos: tuple[int, int], *groups):
        super().__init__(pos, "fungusfarm", 84, Area.ThreeByThree, *groups)


# class Lumbermill(Building):
#     def __init__(self, pos: tuple[int, int], *groups):
#         super().__init__(bottom_offset, *groups)


# class Forgery(Building):
#     def __init__(self, pos: tuple[int, int], *groups):
#         super().__init__(bottom_offset, *groups)


# class Barracks(Building):
#     def __init__(self, pos: tuple[int, int], *groups):
#         super().__init__(bottom_offset, *groups)


# class Siegery(Building):
#     def __init__(self, pos: tuple[int, int], *groups):
#         super().__init__(bottom_offset, *groups)
