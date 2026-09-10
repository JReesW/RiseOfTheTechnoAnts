import pygame

from engine import image
from game.entities import Entity
from game import isometric, units, buildings
from game.types import *

import random


tree_offsets = [
    (-10, 22),
    (-22, -20),
    (-50, 8),
    (10, -18),
    (25, 20),
    (46, -12)
]


class Inventory:
    def __init__(self, wood: int, metal: int, food: int, allegiance: Allegiance):
        self.wood = wood
        self.metal = metal
        self.food = food
        self.allegiance = allegiance

        self.population = 0
        self.population_cap = 0

    def update(self, _units: pygame.sprite.Group[units.Unit], _buildings: pygame.sprite.Group[buildings.Building]):
        pods = 0
        for building in _buildings:
            if building.name == "pod" and building.allegiance == self.allegiance:
                pods += 1
        self.population_cap = pods * 10

        workers = 0
        for unit in _units:
            if unit.name == "worker" and unit.allegiance == self.allegiance:
                workers += 1
        self.population = workers



class Resource(Entity):
    def __init__(self, pos: Coords, bottom_offset, *groups):
        super().__init__(Allegiance.Nature, bottom_offset, *groups)
        self.pos = pos
        self.center = isometric.tile_to_world_coords(*pos)
        self.shadow: pygame.Surface = None

    def draw_shadow(self, surface, camera):
        r = self.rect.move_to(center=isometric.world_to_screen_coords(self.center[0], self.center[1] - 37, camera))
        surface.blit(self.shadow, r)


class Tree(Resource):
    def __init__(self, pos: Coords, *groups):
        super().__init__(pos, 0, *groups)
        self.center = isometric.tile_to_world_coords(*pos)

        self.image = self.generate_trees()
        self.rect = pygame.Rect(0, 0, *self.image.size).move_to(centerx=self.center[0], bottom=self.center[1]+20)

    def generate_trees(self):
        tree_imgs = [image.load_image("tree1"), image.load_image("tree2")]
        offsets = random.sample(tree_offsets, random.randint(4, 5))
        trees: list[tuple[pygame.Rect, int]] = []
        for x, y in sorted(offsets, key=lambda p: p[1]):
            rect = pygame.Rect(0, 0, 42, 84).move_to(centerx = x, bottom = y)
            img = random.randint(0, 1)
            trees.append((rect, img))
        r1, *rects = [r for r, _ in trees]
        totalrect = r1.unionall(rects)

        self.shadow = pygame.Surface(totalrect.size, pygame.SRCALPHA)
        surface = pygame.Surface(totalrect.size, pygame.SRCALPHA)
        for rect, img in trees:
            r = rect.move(-totalrect.left, -totalrect.top)
            surface.blit(tree_imgs[img], r)
            self.shadow.blit(image.load_image("treeshadow"), r)

        return surface
