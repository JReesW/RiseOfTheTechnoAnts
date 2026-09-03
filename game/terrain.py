import pygame
import random
import time
import math

from game.noiseHelper import generate_noise_map, normalize_noise_map

import numpy as np

#IDs [water, plains, forest, team1, team2]

def create_terrain(width: int, height: int, seed: int):
    start = time.perf_counter()

    # create edge distance map
    y, x = np.indices((height, width))

    edge_distance = np.minimum.reduce([x, y, width - 1 - x, height - 1 - y])
    edge_distance_normal = edge_distance / edge_distance.max()
    edge_distance = 1 - edge_distance_normal

    # make middle of map lower
    edge_distance = np.where(edge_distance < 0.2, edge_distance_normal * -0.025, edge_distance)


    altitude_map = normalize_noise_map(generate_noise_map(width, height, seed, octaves=1, frequency=0.05))
    greenery_map = normalize_noise_map(generate_noise_map(width, height, seed, octaves=1, frequency=0.15))

    print(f"noise map made: {time.perf_counter() - start}")

    # variables for level gen
    water_level = 0.30

    base_forest_chance = 0.15
    forest_bonus = 0.15
    # water level plus drop off and if altitude is lower than that number it gets the bonus chance
    forest_bonus_dropoff = 0.10

    # apply the edge distance map as effectively a slope map, then normilize it
    altitude_map += edge_distance * water_level
    altitude_map = altitude_map / altitude_map.max()


    # pick a random spot in the corners for the team regions
    ran = random.Random(seed)
    
    grid = [[0] * width for _ in range(height)]

    team1_x = ran.randint(int(width * 0.10), int(width * 0.15))
    team1_y = ran.randint(int(height * 0.10), int(height * 0.15))

    team2_x = ran.randint(int(width * 0.85), int(width * 0.90))
    team2_y = ran.randint(int(height * 0.85), int(height * 0.90))

    spawn_radius = 6

    for y in range(height):
        for x in range(width):
            if math.dist((team1_x, team1_y), (x, y)) <= spawn_radius:
                grid[y][x] = 3
                continue
            if math.dist((team2_x, team2_y), (x, y)) <= spawn_radius:
                grid[y][x] = 4
                continue

            altitude = altitude_map[y, x]
            greenery = greenery_map[y, x]

            forest_chance = base_forest_chance

            if (altitude > water_level and altitude < water_level + forest_bonus_dropoff):
                forest_chance += forest_bonus

            if altitude <= water_level:
                grid[y][x] = 0
            elif altitude > water_level and greenery < forest_chance:
                grid[y][x] = 2
            else:
                grid[y][x] = 1

    print(f"biome grid made: {time.perf_counter() - start}")

    return Terrain(grid)

class Terrain():
    def __init__(self, grid: list[list[int]]):
        self.grid: list[list[int]] = grid