import pygame
from engine.scene import Scene
from engine import colors, image, mouse, debug

import numpy as np

from game.noiseHelper import generate_noise_map, noise_map_to_rgb
from game import terrain

class BiomesScene(Scene):
    def __init__(self, *args, **kwargs):
        self.width = 100
        self.height = 100

        self.map = pygame.surface.Surface((self.width, self.height))
        self.seed = 0
        self.terrain = None

        self.biomes = np.array([
            [50, 120, 200],   # water
            [124, 200, 80],   # plains
            [34, 139, 34],    # forest
        ], dtype=np.uint8)

    def update_map(self):
        self.terrain = terrain.create_terrain(self.width, self.height, self.seed)

        biome_array = np.array(self.terrain.grid)

        pixel_array = self.biomes[biome_array]

        self.map = pygame.surfarray.make_surface(pixel_array)

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
                elif event.key == pygame.K_LSHIFT:
                    self.test = not self.test
                    self.update_map()
                elif event.key == pygame.K_w:
                    self.octaves += 1
                elif event.key == pygame.K_s:
                    self.octaves -= 1
                    if self.octaves < 1: self.octaves = 1

    def update(self, dt):
        pass

    def render(self, surface):
        surface.fill(colors.pink)

        scaled_map = pygame.transform.scale(self.map, (surface.get_width(), surface.get_height()))

        surface.blit(scaled_map, (0, 0))