import pygame
import random

from game.noiseHelper import generate_noise_map, normalize_noise_map

#IDs [water, plains, forest]

def create_terrain(width: int, height: int, seed: int):
    altitude_map = normalize_noise_map(generate_noise_map(width, height, seed, octaves=3))

    ran = random.Random(seed)

    grid = [[0] * width for _ in range(height)]

    water_level = 0.30

    base_forest_chance = 0.01
    forest_bonus = 0.15
    # water level plus drop off and if altitude is lower than that number it gets the bonus chance
    forest_bonus_dropoff = 0.05

    for y in range(height):
        for x in range(width):
            altitude = altitude_map[x, y]

            if altitude <= water_level:
                grid[y][x] = 0
            elif altitude > water_level and ran.random() < (forest_bonus if altitude < water_level + forest_bonus_dropoff else base_forest_chance):
                grid[y][x] = 2
            else:
                grid[y][x] = 1

    return Terrain(grid)

class Terrain():
    def __init__(self, grid: list[list[int]]):
        self.grid: list[list[int]] = grid