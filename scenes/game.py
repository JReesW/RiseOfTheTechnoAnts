import pygame
from engine.scene import Scene, Camera
from engine import colors, image, mouse

import random, sys


terrain = []
with open("resources/terrain.txt", 'r') as file:
    for line in file.readlines():
        terrain.append([int(c) for c in line.strip()])

# terrain = [
#     [1, 1],
#     [0, 0]
# ]


class Game(Scene):
    def __init__(self):
        self.window_size = pygame.display.get_surface().get_size()

        self.map = self.generate_map()
        self.camera = Camera((8000, 4200), x_bounds=(0, 16000 - 1920), y_bounds=(0, 8400 - 1080))
        self.cam_speed = 10
        
    def generate_map(self):
        grass = image.load_image("ground_textured")
        water = image.load_image("water")
        trees = image.load_image("ground_trees")
        grass_tiles = [pygame.transform.flip(grass, bool(n % 2), bool(n // 2)) for n in range(4)]
        water_tiles = [pygame.transform.flip(water, bool(n % 2), bool(n // 2)) for n in range(4)]

        n = len(terrain)
        w, h = n * 160, n * 84  # based on a 82x39 tile sprite
        print(f"Generating terrain image of {w} x {h} pixels")
        surface = pygame.Surface((w, h), pygame.SRCALPHA)
        print(f"Terrain image is {surface.get_bytesize() * w * h} bytes")

        for y, row in enumerate(terrain):
            for x, cell in enumerate(row):
                px = (w // 2) + (x - y) * 80
                py = 42 + (x + y) * 42
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
                
    def update(self, dt):
        pass

    def render(self, surface):
        surface.fill(colors.black)

        surface.blit(self.map, (0, 0), self.camera.rect)
