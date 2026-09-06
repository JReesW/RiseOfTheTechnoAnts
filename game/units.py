import pygame

from engine import image, spritesheet, animation
from engine.scene import Camera
from game import isometric
from game.entities import Entity

import enum


class State(enum.IntEnum):
    Idle = 0
    Walking = 1
    Working = 2
    Attacking = 3


class Direction(enum.StrEnum):
    East = "+X"
    SouthEast = "+X+Y"
    South = "+Y"
    SouthWest = "-X+Y"
    West = "-X"
    NorthWest = "-X-Y"
    North = "-Y"
    NorthEast = "+X-Y"


class Unit(Entity):
    """
    Entities not bound by the grid, their pos is pixel-based
    """

    def __init__(self, pos: tuple[int, int], sheet_name: str, size: int, *groups):
        super().__init__(0, *groups)
        self.pos = pos
        self.size = size  # radial size
        self.state = State.Idle
        self.direction = Direction.East

        self.sheet = spritesheet.SpriteSheet(sheet_name)
        self.animation = animation.AnimationHandler(self.sheet)

        rect = pygame.Rect(0, 0, 48, 48)
        self.rect = rect.move_to(center=pos)

        self.shadow = image.load_image(f"antshadow")

    def update(self, dt):
        self.update_state(dt)
        self.update_animation(dt)
        super().update()

    def update_state(dt):
        pass

    def update_animation(dt):
        pass

    def draw_shadow(self, surface: pygame.Surface, camera: Camera):
        r = pygame.Rect(0, 0, *self.shadow.size).move_to(center=isometric.world_to_screen_coords(*self.pos, camera))
        surface.blit(self.shadow, r)


class Worker(Unit):
    def __init__(self, pos: tuple[int, int], *groups):
        super().__init__(pos, "worker", 20, *groups)

    def update_state(self, dt):
        self.state = State.Walking
        self.animation.update(dt)

    def update_animation(self, dt):
        if self.state == State.Idle: self.animation.play(f"Idle{self.state}")
        elif self.state == State.Walking: self.animation.play(f"Walk{self.direction}")
        self.image = self.animation.get_frame()
