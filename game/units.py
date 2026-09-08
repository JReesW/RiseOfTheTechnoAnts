import pygame

from engine import image, spritesheet, animation, debug
from engine.scene import Camera
from game import isometric
from game.entities import Entity

import enum, math

hpi = math.pi / 2


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


class UnitSpriteSheets:
    """
    Preload sprite sheets
    """



class Unit(Entity):
    """
    Entities not bound by the grid, their pos is pixel-based (floating tile)
    """

    def __init__(self, pos: tuple[int, int], sheet_name: str, size: int, speed: int, *groups):
        super().__init__(0, *groups)
        self.pos = pos
        self.size = size  # radial size
        self.speed = speed
        self.state = State.Idle
        self.direction = Direction.East
        self.target = None

        self.sheet = spritesheet.SpriteSheet(sheet_name)
        self.animation = animation.AnimationHandler(self.sheet)
        self.image = self.sheet.get_sprite("Walk+X0")

        rect = pygame.Rect(0, 0, 48, 48)
        self.rect = rect.move_to(center=isometric.tile_to_world_coords(*pos, floating=True))

        self.shadow = image.load_image(f"antshadow")

    def set_target(self, target: tuple[int, int]):
        self.target = target

    def update(self, dt):
        self.update_state(dt)
        self.update_animation(dt)
        super().update(dt)

    def update_state(dt):
        pass

    def update_animation(dt):
        pass

    def draw_shadow(self, surface: pygame.Surface, camera: Camera):
        r = pygame.Rect(0, 0, *self.shadow.size).move_to(center=isometric.world_to_screen_coords(*self.pos, camera))
        surface.blit(self.shadow, r)


class Worker(Unit):
    def __init__(self, pos: tuple[int, int], *groups):
        super().__init__(pos, "worker", 20, 0.03, *groups)

    def update_state(self, dt):
        self.animation.update(dt)

        if self.target is not None:
            if math.dist(self.pos, self.target) < self.speed:
                self.target = None
                self.state = State.Idle
            else:
                self.state = State.Walking
                tx, ty = self.target
                px, py = self.pos
                theta = math.atan2(ty-py, tx-px)
                dx, dy = math.cos(theta) * self.speed, math.sin(theta) * self.speed

                # Back to quarter-pi shenanigans
                if theta < -hpi: self.direction = Direction.West
                elif theta < 0: self.direction = Direction.North
                elif theta < hpi: self.direction = Direction.East
                else: self.direction = Direction.South

                self.pos = px + dx, py + dy
                self.rect = self.rect.move_to(center=isometric.tile_to_world_coords(*self.pos, floating=True))

    def update_animation(self, dt):
        if self.state == State.Idle: self.animation.play(f"Idle{self.direction}")
        elif self.state == State.Walking: self.animation.play(f"Walk{self.direction}")
        self.image = self.animation.get_frame()
