import pygame

from engine import image, spritesheet, animation, debug, director
from engine.scene import Camera
from game import isometric, pathfinding
from game.entities import Entity
import game.buildings as buildings
from game.types import *

import enum, math

qpi = lambda n: (math.pi / 4) * n


class State(enum.IntEnum):
    Idle = 0
    Walking = 1
    Building = 2
    Gathering = 3
    Attacking = 4


class Direction(enum.StrEnum):
    East = "X"
    South = "XF"
    West = "YF"
    North = "Y"


class Task:
    """"""


class Build(Task):
    def __init__(self, ghost_building, pos: Coords, allegiance: Allegiance, returnpos: Coords):
        self.ghost_building = ghost_building
        self.pos = pos
        self.allegiance = allegiance
        self.returnpos = returnpos


class Gather(Task):
    def __init__(self, pickup: Coords, item: str):
        self.pickup = pickup
        self.item =  item
        self.mining_time = 180


class Dropoff(Task):
    def __init__(self, building, redo: Gather):
        self.building = building
        self.redo = redo


class Attack(Task):
    def __init__(self, target: Entity):
        self.target = target


class Unit(Entity):
    """
    Entities not bound by the grid, their pos is pixel-based (floating tile)
    """
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
        self.task = None
        self.carrying = None

        self.sheet = spritesheet.load_spritesheet(unit_type.name + ('' if self.allegiance == Allegiance.Player else '_red'))
        self.animation = animation.AnimationHandler(self.sheet)
        self.image = self.sheet.get_sprite("WalkX0")

        rect = self.image.get_rect()
        self.rect = rect.move_to(center=isometric.tile_to_world_coords(*pos, floating=True))

        self.shadow = image.load_image(f"shadows/antshadow")

    def set_targets(self, targets: list[Coords]):
        """
        Set the path of targets this unit must follow
        """
        self.target = None
        self.targets = targets

    def set_task(self, pos: Coords):
        """
        Check if a task can be set for this unit if it has been sent somewhere
        """
        pass

    def update_task(self):
        """
        Handle how the task at hand must change once this unit is standing still while not idling
        """
        pass

    def update(self, dt):
        self.update_state(dt)
        self.update_animation(dt)
        super().update(dt)

    def update_state(self, dt):
        if self.target is None:
            if self.targets:
                self.target, *self.targets = self.targets
            elif self.task is not None:
                self.update_task()

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
        self.animation.update(dt)
        self.image = self.animation.get_frame()

    def draw_shadow(self, surface: pygame.Surface, camera: Camera):
        r = pygame.Rect(0, 0, *self.shadow.size).move_to(center=isometric.tile_to_screen_coords(*self.pos, camera, True))
        surface.blit(self.shadow, r)


class Worker(Unit):
    name = "worker"
    sound = "worker"
    display_name = "Worker"
    size = 20
    speed = 0.03
    blacklist = [0]

    max_health = 20

    def set_task(self, pos: Coords):
        terrain = director.global_data["terrain"]
        pos = isometric.world_to_tile_coords(*pos)
        if terrain[pos[1]][pos[0]] in (2, 5, 6):
            item = {2: "wood", 5: "leaves", 6: "ore"}[terrain[pos[1]][pos[0]]]
            self.task = Gather(pos, item)
        else:
            self.task = None
            self.carrying = None

    def update_task(self):
        match self.task:
            case Gather(pickup=pickup, item=item, mining_time=mining_time):
                if mining_time <= 0:
                    # find the closest dropoff building
                    buildings = director.global_data["buildings"]
                    b_filter = ["nexus", "fungusfarm" if item == "leaves" else ("foundry" if item == "ore" else "lumbermill")]
                    buildings = [b for b in buildings if b.allegiance == self.allegiance and b.name in b_filter]
                    closest_building = min(buildings, key=lambda b: math.dist(self.pos, b.pos) * (3 if b.name == "nexus" else 1))
                    self.task = Dropoff(closest_building, self.task)
                    self.carrying = item

                    # pathfind to it
                    rounded = round(self.pos[0]), round(self.pos[1])
                    path = pathfinding.pathfind(pathfinding.create_walkable_map(director.global_data["terrain"], director.global_data["buildings"], self.blacklist, closest_building), rounded, closest_building.pos)
                    self.set_targets(path)
                else:
                    self.task.mining_time -= 1
            case Dropoff(building=building, redo=redo):
                # add item to inventory
                inventory = "player_inventory" if self.allegiance == Allegiance.Player else "enemy_inventory"
                director.global_data[inventory].add(self.carrying, building.name)
                self.carrying = None

                # redo the gathering task
                self.task = Gather(redo.pickup, redo.item)
                rounded = round(self.pos[0]), round(self.pos[1])
                path = pathfinding.pathfind(pathfinding.create_walkable_map(director.global_data["terrain"], director.global_data["buildings"], self.blacklist, building), rounded, self.task.pickup)
                self.set_targets(path)
            case Build(ghost_building=ghost_building, pos=pos, allegiance=allegiance, returnpos=returnpos):
                building = ghost_building(pos, allegiance, director.global_data["buildings"])
                director.global_data["entities"].add(building)

                rounded = round(self.pos[0]), round(self.pos[1])
                path = pathfinding.pathfind(pathfinding.create_walkable_map(director.global_data["terrain"], director.global_data["buildings"], self.blacklist, building), rounded, returnpos)
                self.set_targets(path)

                self.task = None


class Queen(Unit):
    name = "queen"
    sound = "queen"
    display_name = "Queen"
    size = 20
    speed = 0.02
    blacklist = [0]

    max_health = 15

    def set_task(self, pos: Coords):
        self.task = None
        self.carrying = None

    def update_task(self):
        match self.task:
            case Build(ghost_building=ghost_building, pos=pos, allegiance=allegiance, returnpos=returnpos):
                building = ghost_building(pos, allegiance, director.global_data["buildings"])
                director.global_data["entities"].add(building)

                rounded = round(self.pos[0]), round(self.pos[1])
                path = pathfinding.pathfind(pathfinding.create_walkable_map(director.global_data["terrain"], director.global_data["buildings"], self.blacklist, building), rounded, returnpos)
                self.set_targets(path)

                self.kill(silent=True)


class Combatant(Unit):
    """
    Any unit that fights
    """
    attack_delay = 5
    damage: int

    def __init__(self, pos, allegiance, *groups):
        super().__init__(pos, allegiance, *groups)
        self.delay = 0
    
    def set_task(self, pos: Coords):
        tpos = isometric.world_to_tile_coords(*pos)
        rounded = lambda p: (int(p[0]), int(p[1]))
        opponent_buildings = [b for b in director.global_data["buildings"] if b.allegiance != self.allegiance and b.occupies_tile(tpos)]
        opponent_units = [u for u in director.global_data["units"] if u.allegiance != self.allegiance and rounded(u.pos) == tpos]

        opponent = None
        if opponent_units:
            opponent = opponent_units[0]
        elif opponent_buildings:
            opponent = opponent_buildings[0]

        if opponent is not None:
            self.task = Attack(opponent)
        else:
            self.task = None
            path = pathfinding.pathfind(pathfinding.create_walkable_map(director.global_data["terrain"], director.global_data["buildings"], self.blacklist), rounded(self.pos), tpos)
            if path:
                path[-1] = isometric.world_to_tile_coords(*pos, True)
                self.set_targets(path)

    def update_task(self):
        match self.task:
            case Attack(target=target):
                if isinstance(target, Unit):
                    target_pos = target.pos
                    target_range = 1
                elif isinstance(target, buildings.Building):
                    target_pos = isometric.world_to_tile_coords(*target.get_center(), floating=True)
                    target_range = target.area / 2

                if math.dist(self.pos, target_pos) <= target_range:
                    self.state = State.Attacking
                    if self.delay == 0:
                        target.hurt(self.damage)
                        if target.health <= 0:
                            # find new targets nearby
                            opponent_buildings = [b for b in director.global_data["buildings"] if b.allegiance != self.allegiance and math.dist(b.pos, self.pos) <= 10]
                            opponent_units = [u for u in director.global_data["units"] if u.allegiance != self.allegiance and math.dist(u.pos, self.pos) <= 10]
                            preference = lambda e: 1 if isinstance(e, type(target)) else 0
                            if opponent_units or opponent_buildings:
                                new_target = min(opponent_buildings + opponent_units, key=lambda e: (preference(e), math.dist(e.pos, self.pos)))
                                self.task = Attack(new_target)
                            else:
                                self.task = None
                                self.state = State.Idle
                    else:
                        self.delay += 1
                        if self.delay == 5: self.delay = 0
                else:
                    rounded = round(self.pos[0]), round(self.pos[1])
                    target_pos = int(target_pos[0]), int(target_pos[1])
                    path = pathfinding.pathfind(pathfinding.create_walkable_map(director.global_data["terrain"], director.global_data["buildings"], self.blacklist, target), rounded, target_pos)
                    # path = 
                    self.set_targets(path)


class Soldier(Combatant):
    name = "soldier"
    display_name = "Soldier"
    size = 25
    speed = 0.05
    blacklist = [0]

    max_health = 40
    damage = 3


class Phrag(Combatant):
    name = "phrag"
    display_name = "Phragmotist"
    size = 25
    speed = 0.05
    blacklist = [0]

    max_health = 40
    damage = 4


class Major(Combatant):
    name = "major"
    display_name = "Major"
    size = 25
    speed = 0.05
    blacklist = [0, 2, 5, 6]

    max_health = 40
    damage = 18


class Alate(Combatant):
    name = "alate"
    display_name = "Alate"
    size = 25
    speed = 0.05
    blacklist = []

    max_health = 40
    damage = 200

    def set_task(self, pos: Coords):
        tpos = isometric.world_to_tile_coords(*pos)
        rounded = lambda p: (int(p[0]), int(p[1]))
        opponent_buildings = [b for b in director.global_data["buildings"] if b.allegiance != self.allegiance and b.occupies_tile(tpos)]

        opponent = None
        if opponent_buildings:
            opponent = opponent_buildings[0]

        if opponent is not None:
            self.task = Attack(opponent)
        else:
            self.task = None
            path = pathfinding.pathfind(pathfinding.create_walkable_map(director.global_data["terrain"], director.global_data["buildings"], self.blacklist), rounded(self.pos), tpos)
            if path:
                path[-1] = isometric.world_to_tile_coords(*pos, True)
                self.set_targets(path)

    def update_task(self):
        match self.task:
            case Attack(target=target):
                target_pos = isometric.world_to_tile_coords(*target.get_center(), floating=True)
                target_range = target.area / 2

                if math.dist(self.pos, target_pos) <= target_range:
                    self.state = State.Attacking
                    if self.delay == 0:
                        target.hurt(self.damage)
                        if target.health <= 0:
                            self.kill()
                    else:
                        self.delay += 1
                        if self.delay == 5: self.delay = 0
                else:
                    rounded = round(self.pos[0]), round(self.pos[1])
                    target_pos = int(target_pos[0]), int(target_pos[1])
                    path = pathfinding.pathfind(pathfinding.create_walkable_map(director.global_data["terrain"], director.global_data["buildings"], self.blacklist, target), rounded, target_pos)
                    # path = 
                    self.set_targets(path)
