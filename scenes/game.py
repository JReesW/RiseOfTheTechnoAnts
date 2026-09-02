import pygame
from engine.scene import Scene, Camera
from engine import colors, image, debug
from settings import SCREEN_SIZE, SCREEN_HEIGHT, SCREEN_WIDTH

from game import isometric, maps

import random


terrain = []
with open("resources/terrain.txt", 'r') as file:
    for line in file.readlines():
        terrain.append([int(c) for c in line.strip()])


class Game(Scene):
    def __init__(self):
        isometric.initialize_isometry(len(terrain), 160, 84)
        
        self.selector_image = image.load_image("selector")
        self.selector = (0, 0)

        self.map = maps.generate_map(terrain)

        map_w, map_h = isometric.get_world_size()
        self.camera = Camera((7040, 0), screen_size=SCREEN_SIZE, x_bounds=(0, map_w - SCREEN_WIDTH), y_bounds=(0, map_h - SCREEN_HEIGHT))
        self.cam_speed = 10
    
    def handle_events(self, events):
        mouse = pygame.mouse.get_pos()

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    pass

        if mouse[1] > SCREEN_HEIGHT - 20:
            self.camera.move(0, self.cam_speed)
        elif mouse[1] < 20:
            self.camera.move(0, -self.cam_speed)
        if mouse[0] > SCREEN_WIDTH - 20:
            self.camera.move(self.cam_speed, 0)
        elif mouse[0] < 20:
            self.camera.move(-self.cam_speed, 0)

        self.selector = isometric.screen_coords_to_tile(*mouse, self.camera)
                
    def update(self, dt):
        pass

    def render(self, surface):
        surface.fill(colors.black)

        for rect, surf in self.map:
            if rect.colliderect(self.camera.rect):
                surface.blit(surf, (rect.left - self.camera.rect.left, rect.top - self.camera.rect.top))

        if 0 <= self.selector[0] < 100 and 0 <= self.selector[1] < 100:
            px, py = isometric.tile_to_screen_coords(*self.selector, self.camera)
            r = pygame.Rect(0, 0, 160, 84).move_to(center=(px, py))
            surface.blit(self.selector_image, r)
