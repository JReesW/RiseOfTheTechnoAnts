import pygame
from engine.scene import Scene, Camera
from engine import colors, image, mouse, debug

from game import isometric

import random


terrain = []
with open("resources/terrain.txt", 'r') as file:
    for line in file.readlines():
        terrain.append([int(c) for c in line.strip()])


class Game(Scene):
    def __init__(self):
        isometric.initialize_isometry(len(terrain), 160, 84)
        
        self.window_size = pygame.display.get_surface().get_size()
        self.selector_image = image.load_image("selector")
        self.selector = (0, 0)

        self.map = self.generate_map()
        self.camera = Camera((7040, 200), x_bounds=(0, 16000 - 1920), y_bounds=(0, 8400 - 1080))
        self.cam_speed = 10
        
    def generate_map(self):
        grass = image.load_image("ground_textured")
        water = image.load_image("water")
        trees = image.load_image("ground_trees")
        grass_tiles = [pygame.transform.flip(grass, bool(n % 2), bool(n // 2)) for n in range(4)]
        water_tiles = [pygame.transform.flip(water, bool(n % 2), bool(n // 2)) for n in range(4)]

        w, h = isometric.get_world_size()
        surface = pygame.Surface((w, h), pygame.SRCALPHA)

        for y, row in enumerate(terrain):
            for x, cell in enumerate(row):
                px, py = isometric.tile_to_world_coords(x, y)
                r = pygame.Rect(0, 0, 160, 84).move_to(center=(px, py))
                if cell == 2:
                    img = trees
                else:
                    images = grass_tiles if cell == 1 else water_tiles
                    img = images[random.randint(0, 3)]
                surface.blit(img, r)
        return surface
    
    def handle_events(self, events):
        mouse = pygame.mouse.get_pos()

        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                pass

        if mouse[1] > self.window_size[1] - 20:
            self.camera.move(0, self.cam_speed)
        elif mouse[1] < 20:
            self.camera.move(0, -self.cam_speed)
        if mouse[0] > self.window_size[0] - 20:
            self.camera.move(self.cam_speed, 0)
        elif mouse[0] < 20:
            self.camera.move(-self.cam_speed, 0)

        self.selector = isometric.screen_coords_to_tile(*mouse, self.camera)
                
    def update(self, dt):
        pass

    def render(self, surface):
        surface.fill(colors.black)

        surface.blit(self.map, (0, 0), self.camera.rect)

        if 0 <= self.selector[0] < 100 and 0 <= self.selector[1] < 100:
            px, py = isometric.tile_to_screen_coords(*self.selector, self.camera)
            r = pygame.Rect(0, 0, 160, 84).move_to(center=(px, py))
            surface.blit(self.selector_image, r)
