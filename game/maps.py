"""
RENAME THIS FILE terrain.py / MERGE WITH RDS' TERRAIN CODE
"""
import pygame

from engine import image
from game import isometric

import random


ground = None
water = None
trees = None
ground_tiles = None
water_tiles = None


def load_images():
    """
    God I wanna do this differently, but for the time being...
    """
    global ground, water, trees, ground_tiles, water_tiles
    ground = image.load_image("ground_textured")
    water = image.load_image("water")
    trees = image.load_image("ground_trees")
    ground_tiles = [pygame.transform.flip(ground, bool(n % 2), bool(n // 2)) for n in range(4)]
    water_tiles = [pygame.transform.flip(water, bool(n % 2), bool(n // 2)) for n in range(4)]


def select_image(cell: int) -> pygame.Surface:
    if cell == 0: return water_tiles[random.randint(0, 3)]
    if cell == 1: return ground_tiles[random.randint(0, 3)]
    if cell == 2: return trees
    return water


def generate_chunk(terrain: list[list[int]], cx: int, cy: int) -> tuple[pygame.Rect, pygame.Surface]:
    w, h = isometric.tile_size()
    surface = pygame.Surface((w * 10, h * 10), pygame.SRCALPHA)
    world_size = (w * 10, h * 10)

    for y in range(10):
        for x in range(10):
            px, py = isometric.tile_to_world_coords(x, y, world_size)
            r = pygame.Rect(0, 0, 160, 84).move_to(center=(px, py))
            img = select_image(terrain[cy * 10 + y][cx * 10 + x])
            surface.blit(img, r)

    total_w = isometric.get_world_size()[0]
    rect = pygame.Rect((total_w/2) + (cx-cy-1)*(w*10/2), (cx+cy)*(h*10/2), w*10, h*10)

    return rect, surface


def generate_map(terrain: list[list[int]]) -> list[tuple[pygame.Rect, pygame.Surface]]:
    if ground is None: load_images()

    n = len(terrain)
    chunks = []

    for cy in range(n // 10):
        for cx  in range(n // 10):
            chunks.append(generate_chunk(terrain, cx, cy))

    return chunks