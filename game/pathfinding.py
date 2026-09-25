"""
Pathfinding that allows entities to make their way across the map
"""


import pygame

import game.buildings as _buildings
from game.types import *

import queue, math


dirs = [
    (1, 0),
    (0, -1),
    (-1, 0),
    (0, 1),
    (1, 1),
    (-1, 1),
    (1, -1),
    (-1, -1)
]


def create_walkable_map(terrain: Tilemap, buildings: pygame.sprite.Group[_buildings.Building], blacklist: list[int], goal_building: _buildings.Building = None) -> Tilemap:
    """
    Create a tilemap indicating which tile is walkable (1) and which isn't (0)
    """
    walkmap: Tilemap = []

    # Mark all walkable tiles
    for y, row in enumerate(terrain):
        walkmap.append([])
        for cell in row:
            walkmap[y].append(0 if cell in blacklist else 1)

    # Mark tiles occupied by buildings as non-walkable
    for building in [b for b in buildings if b != goal_building]:
        bx, by = building.pos
        x1, x2, y1, y2 = 0, 0, 0, 0
        if building.area >= Area.TwoByTwo: x2, y1 = 1, -1
        if building.area == Area.ThreeByThree: x1, y2 = -1, 1
        for y in range(y1, y2+1):
            for x in range(x1, x2+1):
                walkmap[by + y][bx + x] = 0

    return walkmap


def pathfind(walkmap: Tilemap, start: Coords, goal: Coords) -> list[Coords]:
    """
    Returns the fastest route from the start to the goal in the given walking map
    """
    if walkmap[goal[1]][goal[0]] == 0: return []

    # Setup the count map and priority queue
    w, h = len(walkmap[0]), len(walkmap)
    prio = queue.PriorityQueue()
    count_map = [[None for _ in row] for row in walkmap]
    count_map[start[1]][start[0]] = 0
    prio.put((math.dist(start, goal), start))

    # Depth-first search based on a distance priority
    try:
        while True:
            _, (x, y) = prio.get(block=False)
            if (x, y) == goal:
                break
            for dx, dy in dirs:
                new_tile = nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and walkmap[ny][nx] and (count_map[ny][nx] is None or count_map[ny][nx] >= count_map[y][x]):
                    prio.put((math.dist(new_tile, goal), new_tile))
                    count_map[ny][nx] = count_map[y][x] + 1
    except queue.Empty:
        return []

    # Walk back through the count map
    prev = None
    pos = goal
    path = []
    while True:
        x, y = pos
        n = count_map[y][x]
        if n == 0: break
        path.append(pos)
        options = [(dx, dy) for dx, dy in dirs if n is not None and 0 <= y+dy < h and 0 <= x+dx < w and count_map[y+dy][x+dx] == n-1]

        if prev in options: pass
        elif len(options) == 1 or prev is None: prev = options[0]

        pos = prev[0] + pos[0], prev[1] + pos[1]

    return list(reversed([(x+0.5, y+0.5) for x, y in path]))
