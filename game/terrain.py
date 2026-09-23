"""
Terrain generation using OpenSimplex
"""

import random
import math
import numpy as np
import opensimplex

#IDs [water, plains, forest, team1, team2, bushes, ores]


def generate_noise_map(width: int, height: int, seed: int, amplitude=1.0, frequency=0.1, octaves=3, persistence=0.5, lacunarity=2.0):
    noise_array = np.zeros([height, width])
    os = opensimplex.OpenSimplex(seed)

    max_value = 0

    for _ in range(octaves):
        x_array = np.arange(width) * frequency
        y_array = np.arange(height) * frequency

        next_array = os.noise2array(x_array, y_array)

        noise_array += next_array * amplitude
        max_value += amplitude

        amplitude *= persistence
        frequency *= lacunarity

    return noise_array / max_value

def normalize_noise_map(noise_array):
    return (noise_array + 1) / 2


def create_terrain(width: int, height: int, seed: int):
    # create edge distance map
    y, x = np.indices((height, width))

    edge_distance = np.minimum.reduce([x, y, width - 1 - x, height - 1 - y])
    edge_distance_normal = edge_distance / edge_distance.max()
    edge_distance = 1 - edge_distance_normal

    # make middle of map lower
    edge_distance = np.where(edge_distance < 0.2, edge_distance_normal * -0.025, edge_distance)

    altitude_map = normalize_noise_map(generate_noise_map(width, height, seed << 42, octaves=1, frequency=0.05))
    greenery_map = normalize_noise_map(generate_noise_map(width, height, seed << 16, octaves=1, frequency=0.15))

    resource_map = normalize_noise_map(generate_noise_map(width, height, seed << 24, octaves=1, frequency=0.5))

    # variables for level gen
    water_level = 0.30

    base_forest_chance = 0.15
    forest_bonus = 0.15
    # water level plus drop off and if altitude is lower than that number it gets the bonus chance
    forest_bonus_dropoff = 0.10

    bush_resource_level = 0.15
    bush_altitude_level = 0.5

    ore_resource_level = 0.2
    ore_altitude_level = 0.75

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

            resource = resource_map[y, x]

            forest_chance = base_forest_chance

            if (altitude > water_level and altitude < water_level + forest_bonus_dropoff):
                forest_chance += forest_bonus

            if altitude <= water_level:
                grid[y][x] = 0
            elif altitude > water_level and greenery < forest_chance:
                grid[y][x] = 2
            elif greenery >= 0.5 and resource <= bush_resource_level and altitude <= bush_altitude_level:
                grid[y][x] = 5
            elif greenery < 0.5 and resource <= ore_resource_level and altitude > ore_altitude_level:
                grid[y][x] = 6
            else:
                grid[y][x] = 1

    return grid
