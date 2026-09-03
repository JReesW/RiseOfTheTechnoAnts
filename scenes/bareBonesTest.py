import pygame
from engine.scene import Scene
from engine import colors, image, mouse, debug, director

import numpy as np

from game.noiseHelper import generate_noise_map, noise_map_to_rgb, normalize_noise_map
from game import terrain

import time

class BBTScene(Scene):
    def __init__(self, *args, **kwargs):
        self.width = 100
        self.height = 100

        self.map = pygame.surface.Surface((self.width, self.height))
        self.seed = 0
        self.terrain = None

        self.biomes = np.array([
            [50, 120, 200], # water
            [124, 200, 80], # plains
            [34, 139, 34], # forest
            [255, 0, 0], #team1
            [0, 0, 255], #team2
        ], dtype=np.uint8)

        self.update_map()

    def update_map(self):
        start = time.perf_counter()
        # altitude_map = generate_noise_map(self.width, self.height, self.seed, octaves=1, frequency=0.05)

        # def is_lake(x):
        #     return 1.0 if x < 0 else -1.0

        # lake_check = np.vectorize(is_lake)

        # altitude_map = lake_check(altitude_map)
        y, x = np.indices((self.height, self.width))
        nx = (x - self.width / 2) / (self.width / 2)
        ny = (y - self.height / 2) / (self.height / 2)
    
        altitude_map = np.minimum(1, (nx**2 + ny**2) / np.sqrt(2))
        altitude_map = noise_map_to_rgb(altitude_map)

        self.map = pygame.surfarray.make_surface(altitude_map)

        print(f"everything complete: {time.perf_counter() - start}")

        debug.debug("seed", self.seed)
    
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.update_map()
                elif event.key == pygame.K_UP:
                    self.seed += 1
                    self.update_map()
                elif event.key == pygame.K_DOWN:
                    self.seed -= 1
                    self.update_map()
                elif event.key == pygame.K_RETURN:
                    director.change_scene("BiomesScene")
                    director._set_scene()

    def update(self, dt):
        pass

    def render(self, surface):
        surface.fill(colors.pink)

        scaled_map = pygame.transform.scale(self.map, (surface.get_width(), surface.get_height()))

        surface.blit(scaled_map, (0, 0))