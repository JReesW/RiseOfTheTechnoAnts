import pygame

from engine import image
from game import isometric
from game.entities import Entity


# Add right offset too for 2x2 buildings?
class Building(Entity):
    def __init__(self, bottom_offset, *groups):
        super().__init__(bottom_offset, *groups)


class Nexus(Building):
    def __init__(self, pos: tuple[int, int], *groups):
        super().__init__(84, *groups)

        self.pos = pos
        self.image = image.load_image("nexus")
        rect = pygame.Rect(0, 0, 344, 440)
        px, py = isometric.tile_to_world_coords(*self.pos)
        self.rect = rect.move_to(centerx = px, bottom = py + self.bottom_offset)

    def occupies_tile(self, tile: tuple[int, int]) -> bool:
        """
        Return whether this building occupies the given tile
        """
        tx, ty = tile
        px, py = self.pos
        print(tx, ty)
        print(px, py)
        return px - 1 <= tx <= px + 1 and py - 1 <= ty <= py + 1
