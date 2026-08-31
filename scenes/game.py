import pygame
from engine.scene import Scene
from engine import colors, image, mouse


terrain = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 1, 1, 1, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
]


class Game(Scene):
    def __init__(self, *args, **kwargs):
        self.grass_tile = image.load_image("grass_tile")
        self.water_tile = image.load_image("water_tile")

        self.map = self.generate_map()

    def generate_map(self):
        n = len(terrain)
        w, h = n * 82, n * 41  # based on a 80x42 tile sprite
        surface = pygame.Surface((w, h), pygame.SRCALPHA)

        for y, row in enumerate(terrain):
            for x, cell in enumerate(row):
                px = (w / 2) + (x - y) * 41
                py = 20 + (x + y) * 20
                r = pygame.Rect(0, 0, 82, 41).move_to(center=(px, py))
                img = self.grass_tile if cell == 0 else self.water_tile
                surface.blit(img, r)
        return surface
    
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                pass
                
    def update(self, dt):
        pass

    def render(self, surface):
        surface.fill(colors.black)

        surface.blit(self.map, pygame.Rect(0, 0, *self.map.get_size()).move_to(center=(960, 540)))
