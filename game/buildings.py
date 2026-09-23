"""
Buildings, entities that are bound to the grid
"""


import pygame

from engine import image, spritesheet, animation, director
from engine.scene import Camera
from game import isometric, units
import game.actions as actions
import game.pathfinding as pathfinding
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
    """
    bottom_offset: int
    area: Area

    blacklist: list[int] = [0, 2, 5, 6]

    def __init__(self, pos: Coords, allegiance: Allegiance, *groups):
        building_type = type(self)
        super().__init__(allegiance, building_type.bottom_offset, *groups)

        self.pos = pos
        self.image = image.load_image(f"buildings/{building_type.name}{'' if allegiance == Allegiance.Player else '_red'}")
        self.area = building_type.area
        rect = pygame.Rect(0, 0, *self.image.size)
        px, py = isometric.tile_to_world_coords(*self.pos)
        ox = 80 if building_type.area == Area.TwoByTwo else 0  # offset the X from tile center on TwoByTwo
        self.rect = rect.move_to(centerx = px + ox, bottom = py + self.bottom_offset)

        self.shadow = image.load_image(f"shadows/shadow{building_type.area}")

        self.action_processor = actions.ActionProcessor(self)
        self.spawn_offset = 0

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

    def spawn_unit(self, unit: units.Unit):
        """
        Spawn an entity around this building
        """
        if self.area == Area.TwoByTwo:
            positions = [(0, 1), (1, 1), (2, 1), (2, 0), (2, -1), (-1, 1), (2, -2), (1, -2), (0, -2), (-1, -2), (-1, -1), (-1, 0)]
        else:
            positions = [(-1, 2), (0, 2), (1, 2), (2, 2), (2, 1), (2, 0), (2, -1), (2, -2), (1, -2), (0, -2), (-1, -2), (-2, -2), (-2, -1), (-2, 0), (-2, 1), (-2, 2)]
        for n in range(len(positions)):
            dx, dy = positions[(n + self.spawn_offset) % len(positions)]
            x, y = self.pos[0] + dx, self.pos[1] + dy
            limit = isometric.get_dimension()
            if 0 <= x < limit and 0 <= y < limit:
                walkmap = pathfinding.create_walkable_map(director.global_data["terrain"], director.global_data["buildings"], [0, 2, 5, 6])
                if walkmap[y][x] == 1:
                    director.global_data["entities"].add(unit((x, y), self.allegiance, director.global_data["units"]))
                    self.spawn_offset = (self.spawn_offset + 1) % 5
                    return

    def update(self, dt):
        super().update(dt)
        self.action_processor.update()

    def draw_shadow(self, surface: pygame.Surface, camera: Camera):
        r = pygame.Rect(0, 0, *self.shadow.size).move_to(center=isometric.world_to_screen_coords(*self.get_center(), camera))
        surface.blit(self.shadow, r)


class Nexus(Building):
    name = "nexus"
    display_name = "Nexus"
    bottom_offset = 74
    area = Area.ThreeByThree
    sound = "nexus"
    max_health = 1000


class Pod(Building):
    name = "pod"
    display_name = "Pod"
    bottom_offset = 52
    area = Area.TwoByTwo
    sound = "pod"
    max_health = 150


class Tower(Building):
    name = "tower"
    display_name = "Tower"
    bottom_offset = 50
    area = Area.TwoByTwo
    max_health = 100

    def __init__(self, pos, allegiance, *groups):
        super().__init__(pos, allegiance, *groups)

        tower_color = "tower" if allegiance == Allegiance.Player else "tower_red"
        sheet = spritesheet.load_spritesheet("tower")
        self.animation = animation.AnimationHandler(sheet)
        self.animation.play(tower_color)
        self.image = sheet.get_sprite(f"{tower_color}1")

    def update(self, dt):
        self.animation.update(dt)
        self.image = self.animation.get_frame()
        return super().update(dt)


class Farm(Building):
    name = "fungusfarm"
    sound = "fungusfarm"
    display_name = "Fungus Farm"
    bottom_offset = 84
    area = Area.ThreeByThree
    max_health = 300


class Lumbermill(Building):
    name = "lumbermill"
    sound = "lumbermill"
    display_name = "Lumbermill"
    bottom_offset = 94
    area = Area.ThreeByThree
    max_health = 300

    def draw_shadow(self, surface: pygame.Surface, camera: Camera):
        cx, cy = isometric.world_to_screen_coords(*self.get_center(), camera)
        r = pygame.Rect(0, 0, *self.shadow.size).move_to(center=(cx + 40, cy))
        surface.blit(self.shadow, r)


class Foundry(Building):
    name = "foundry"
    display_name = "Foundry"
    sound = "foundry"
    bottom_offset = 104
    area = Area.ThreeByThree
    max_health = 300

    def draw_shadow(self, surface: pygame.Surface, camera: Camera):
        cx, cy = isometric.world_to_screen_coords(*self.get_center(), camera)
        r = pygame.Rect(0, 0, *self.shadow.size).move_to(center=(cx + 40, cy + 10))
        surface.blit(self.shadow, r)


class Barracks(Building):
    name = "barracks"
    sound = "barracks"
    display_name = "Barracks"
    bottom_offset = 104
    area = Area.ThreeByThree
    max_health = 450


class Siegery(Building):
    name = "siegery"
    sound = "siegery"
    display_name = "Siegery"
    bottom_offset = 84
    area = Area.ThreeByThree
    max_health = 600
