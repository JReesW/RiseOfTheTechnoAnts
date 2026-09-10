import pygame

from game import isometric, maps
from game.types import *
from engine.scene import Camera
from engine import colors


class Overlay:
    """
    Overlay manager for the actions menu, resources, minimap, and unit selection
    """

    def __init__(self, terrain: Tilemap, camera: Camera):
        self.size = self.width, self.height = (320, 168)
        self.minimap = maps.generate_minimap(terrain, self.size)
        self.minimap_rect = pygame.Rect(0, 0, self.width, self.height).move_to(topright=(1910, 10))
        self.minimap_backdrop = pygame.Surface((self.width + 20, self.height + 20))  # minimap size + 10 on all edges
        self.minimap_backdrop.fill(colors.dark_slate_blue)
        self.minimap_backdrop_rect = pygame.Rect(0, 0, self.width + 20, self.height + 20).move_to(topright=(1920, 0))
        pygame.draw.rect(self.minimap_backdrop, colors.slate_blue, self.minimap_backdrop.get_rect(), 3)

        self.camera = camera
        self.cam_surface = pygame.Surface(self.size, pygame.SRCALPHA)
        ww, wh = isometric.get_world_size()
        self.camw, self.camh = self.width * (1920 / ww), self.height * (1080 / wh)

    def handle_events(self, mouse: Coords, events: list[pygame.event.Event]) -> bool:
        """
        Return whether the overlay has usurped the events
        """
        if self.minimap_backdrop_rect.collidepoint(mouse):
            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if self.minimap_rect.collidepoint(mouse):
                            # move the camera center to where the user clicked on the map
                            ww, wh = isometric.get_world_size()
                            x = pygame.math.remap(self.minimap_rect.left, self.minimap_rect.right, 0, ww, mouse[0])
                            y = pygame.math.remap(self.minimap_rect.top, self.minimap_rect.bottom, 0, wh, mouse[1])
                            self.camera.set_center((x, y))

            return True
        return False

    def update(self):
        pass

    def render(self, surface: pygame.Surface):
        # minimap
        surface.blit(self.minimap_backdrop, self.minimap_backdrop_rect)
        surface.blit(self.minimap, self.minimap_rect)

        self.cam_surface.fill((0, 0, 0, 0))
        ww, wh = isometric.get_world_size()
        cx, cy = pygame.math.remap(0, ww, 0, self.width, self.camera.rect.left), pygame.math.remap(0, wh, 0, self.height, self.camera.rect.top)
        cam_r = pygame.Rect(cx, cy, self.camw, self.camh)
        pygame.draw.rect(self.cam_surface, colors.white, cam_r, 1)
        surface.blit(self.cam_surface, self.minimap_rect)
