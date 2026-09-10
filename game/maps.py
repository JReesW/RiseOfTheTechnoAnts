"""
RENAME THIS FILE terrain.py / MERGE WITH RDS' TERRAIN CODE
"""
import pygame

from engine import image, colors
from game import isometric
from game.types import *

import random


ground = None
water = None
bush = None
ore = None
ground_tiles = None
water_tiles = None


def load_images():
    """
    God I wanna do this differently, but for the time being...
    """
    global ground, water, trees, bush, ore, ground_tiles, water_tiles
    ground = image.load_image("tiles/ground_textured")
    water = image.load_image("tiles/water")
    bush = image.load_image("tiles/ground_bush")
    ore = image.load_image("tiles/ground_ore")
    ground_tiles = [pygame.transform.flip(ground, bool(n % 2), bool(n // 2)) for n in range(4)]
    water_tiles = [pygame.transform.flip(water, bool(n % 2), bool(n // 2)) for n in range(4)]


def select_image(cell: int) -> pygame.Surface:
    if cell == 0: return water_tiles[random.randint(0, 3)]
    if cell == 5: return bush
    if cell == 6: return ore
    return ground_tiles[random.randint(0, 3)]


def generate_chunk(terrain: Tilemap, cx: int, cy: int) -> tuple[pygame.Rect, pygame.Surface]:
    """
    Generate a chunk of the map, returning the chunk's rect and surface
    """
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


def generate_map(terrain: Tilemap) -> list[tuple[pygame.Rect, pygame.Surface]]:
    """
    Generate the entire map, returning a list of all chunks
    """
    if ground is None: load_images()

    n = len(terrain)
    chunks = []

    for cy in range(n // 10):
        for cx  in range(n // 10):
            chunks.append(generate_chunk(terrain, cx, cy))

    return chunks


def generate_minimap(terrain: Tilemap, size: tuple[int, int]) -> pygame.Surface:
    """
    Generate a minimap version of the terrain
    """
    images = {
        0: image.load_image("minimap/water"),
        1: image.load_image("minimap/ground"),
        2: image.load_image("minimap/forest"),
        3: image.load_image("minimap/ground"),
        4: image.load_image("minimap/ground"),
        5: image.load_image("minimap/bush"),
        6: image.load_image("minimap/ore")
    }

    tw, th = 20, 9
    w, h = len(terrain[0]) * tw, len(terrain) * th
    surface = pygame.Surface((w, h), pygame.SRCALPHA)
    surface.fill(colors.black)

    for y, row in enumerate(terrain):
        for x, tile in enumerate(row):
            px = (w // 2) + (x - y) * (tw/2)
            py = (th/2) + (x + y) * (th/2)
            r = pygame.Rect(0, 0, tw, th).move_to(center=(px, py))
            img = images[tile]
            surface.blit(img, r)

    return pygame.transform.scale(surface, size)
