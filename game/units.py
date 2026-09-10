import pygame

from engine import image, spritesheet, animation, debug
from engine.scene import Camera
from game import isometric
from game.entities import Entity
from game.types import *

import enum, math

hpi = math.pi / 2
qpi = lambda n: (math.pi / 4) * n


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
    loaded = False
    worker = None
    ...

    @staticmethod
    def load():
        UnitSpriteSheets.loaded = True
        UnitSpriteSheets.worker = spritesheet.SpriteSheet("worker")

    @staticmethod
    def get(name: str) -> spritesheet.SpriteSheet:
        if not UnitSpriteSheets.loaded: raise Exception("Unit spritesheets haven't been loaded in yet")
        if name == "worker": return UnitSpriteSheets.worker
        raise NameError(f"No unit spritesheet found with the name {name}")



class Unit(Entity):
    """
    Entities not bound by the grid, their pos is pixel-based (floating tile)

     - `pos`: their floating tile coordinates
     - `sheet_name`: the name of their spritesheet
     - `size`: their radial size in pixels
     - `speed`: their movement speed (floatingtile/tick)
     - `blacklist`: list of terrain values they can't move through
    """
    name: str
    size: int
    speed: int
    blacklist: list[int]

    def __init__(self, pos: Coords, allegiance: Allegiance, *groups):
        unit_type = type(self)
        super().__init__(allegiance, 0, *groups)
        self.pos = pos
        self.size = unit_type.size
        self.speed = unit_type.speed
        self.state = State.Idle
        self.direction = Direction.East
        self.target = None
        self.targets = []

        self.sheet = UnitSpriteSheets.get(unit_type.name)
        self.animation = animation.AnimationHandler(self.sheet)
        self.image = self.sheet.get_sprite("Walk+X0")

        rect = pygame.Rect(0, 0, 48, 48)
        self.rect = rect.move_to(center=isometric.tile_to_world_coords(*pos, floating=True))

        self.shadow = image.load_image(f"shadows/antshadow")

    def set_targets(self, targets: list[Coords]):
        self.target = None
        self.targets = targets

    def update(self, dt):
        self.update_state(dt)
        self.update_animation(dt)
        super().update(dt)

    def update_state(dt):
        pass

    def update_animation(dt):
        pass

    def draw_shadow(self, surface: pygame.Surface, camera: Camera):
        r = pygame.Rect(0, 0, *self.shadow.size).move_to(center=isometric.tile_to_screen_coords(*self.pos, camera, True))
        surface.blit(self.shadow, r)


class Worker(Unit):
    name = "worker"
    size = 20
    speed = 0.03
    blacklist = [0]
    
    def update_state(self, dt):
        self.animation.update(dt)

        if self.target is None and self.targets:
            self.target, *self.targets = self.targets

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

                if qpi(-3) < theta <= qpi(-1): self.direction = Direction.North
                elif qpi(-1) < theta <= qpi(1): self.direction = Direction.East
                elif qpi(1) < theta <= qpi(3): self.direction = Direction.South
                else: self.direction = Direction.West

                self.pos = px + dx, py + dy
                self.rect = self.rect.move_to(center=isometric.tile_to_world_coords(*self.pos, floating=True))

    def update_animation(self, dt):
        if self.state == State.Idle: self.animation.play(f"Idle{self.direction}")
        elif self.state == State.Walking: self.animation.play(f"Walk{self.direction}")
        self.image = self.animation.get_frame()
