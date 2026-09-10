import pygame

from engine import image
from engine.scene import Camera
from game import isometric
from game.entities import Entity
from game.types import *

import enum


class Area(enum.IntEnum):
    OneByOne = 1
    TwoByTwo = 2
    ThreeByThree = 3


def blocked_tiles(walkmap: Tilemap, pos: Coords, building_type: type[Building]) -> list[Coords]:
    blocked = []
    bx, by = pos
    x1, x2, y1, y2 = 0, 0, 0, 0
    if building_type.area >= Area.TwoByTwo: x2, y1 = 1, -1
    if building_type.area == Area.ThreeByThree: x1, y2 = -1, 1
    for y in range(y1, y2+1):
        for x in range(x1, x2+1):
            nx, ny = bx + x, by + y
            if nx < 0 or nx >= len(walkmap[0]) or ny < 0 or ny >= len(walkmap) or walkmap[ny][nx] == 0:
                blocked.append((nx, ny))
    return blocked


class Building(Entity):
    """
    Entities bound by the grid, their pos is tile-based

     - `pos`: its tile coordinates
     - `image_name`: the basis for all image names of this building
     - `bottom_offset`: how far the rect's bottom has to be offset from the position
     - `area`: the dimensions of how many tiles it takes in place
    """
    name: str
    bottom_offset: int
    area: Area

    blacklist: list[int] = [0, 2, 5, 6]

    def __init__(self, pos: Coords, allegiance: Allegiance, *groups):
        building_type = type(self)
        super().__init__(allegiance, building_type.bottom_offset, *groups)

        self.pos = pos
        self.image = image.load_image(f"buildings/{building_type.name}")
        self.area = building_type.area
        rect = pygame.Rect(0, 0, *self.image.size)
        px, py = isometric.tile_to_world_coords(*self.pos)
        ox = 80 if building_type.area == Area.TwoByTwo else 0  # offset the X from tile center on TwoByTwo
        self.rect = rect.move_to(centerx = px + ox, bottom = py + self.bottom_offset)

        self.shadow = image.load_image(f"shadows/shadow{building_type.area}")

    def occupies_tile(self, tile: Coords) -> bool:
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
    name = "nexus"
    bottom_offset = 74
    area = Area.ThreeByThree
    sound = "nexus"


class Pod(Building):
    name = "pod"
    bottom_offset = 52
    area = Area.TwoByTwo
    sound = "pod"


class Tower(Building):
    name = "nexus1"
    bottom_offset = 25
    area = Area.OneByOne


class Farm(Building):
    name = "fungusfarm"
    bottom_offset = 84
    area = Area.ThreeByThree


# class Lumbermill(Building):
#     name = ...
#     bottom_offset = ...
#     area = ...


# class Forgery(Building):
#     name = ...
#     bottom_offset = ...
#     area = ...


class Barracks(Building):
    name = "barracks"
    bottom_offset = 104
    area = Area.ThreeByThree


class Siegery(Building):
    name = "siegery"
    bottom_offset = 84
    area = Area.ThreeByThree
