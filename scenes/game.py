import pygame
from engine.scene import Scene, Camera
from engine import colors, image, debug, audio, director
from settings import SCREEN_SIZE, SCREEN_HEIGHT, SCREEN_WIDTH

from game import isometric, maps, entities, buildings, resources, units, pathfinding, overlay, actions
from game.types import *

import random, math, enum
from functools import partial


class EntitySelected(Exception):
    """"""


class CursorState(enum.Enum):
    Select = 0
    Build = 1


terrain = []
with open("resources/output.txt", 'r') as file:
    for line in file.readlines():
        terrain.append([int(c) for c in line.strip()])


class Game(Scene):
    def __init__(self):
        isometric.initialize_isometry(len(terrain), 160, 84)
        self.initialize_actions()

        self.audio = audio.AudioHandler()
        self.audio.set_sfx_volume(0.7)
        
        self.selector_image = image.load_image("technical/selector")
        self.selected1_image = image.load_image("technical/selected1")
        self.selected2_image = image.load_image("technical/selected2")
        self.selected3_image = image.load_image("technical/selected3")
        self.invalid_image = image.load_image("technical/invalid")
        self.marker_image = image.load_image("technical/marker")
        self.selector = (0, 0)
        self.selector_prev = (0, 0)
        self.marker = None
        self.cursor_state = CursorState.Select

        self.ghost_building = None
        self.invalid_tiles = []

        self.map = maps.generate_map(terrain)

        map_w, map_h = isometric.get_world_size()
        self.camera = Camera((7040, 0), screen_size=SCREEN_SIZE, x_bounds=(-540, map_w - SCREEN_WIDTH + 540), y_bounds=(-540, map_h - SCREEN_HEIGHT + 540))
        self.cam_speed = 10

        self.buildings: pygame.sprite.Group[buildings.Building] = pygame.sprite.Group()
        self.resources: pygame.sprite.Group[resources.Resource] = pygame.sprite.Group()
        self.units: pygame.sprite.Group[units.Unit] = pygame.sprite.Group()
        self.entities = entities.Entities(self.camera)
        self.populate_map()
        self.entities.add(
            buildings.Nexus((6, 3), Allegiance.Player, self.buildings),
            buildings.Pod((10, 3), Allegiance.Player, self.buildings),
            buildings.Farm((14, 3), Allegiance.Player, self.buildings),
            buildings.Nexus((3, 6), Allegiance.Enemy, self.buildings),
            buildings.Pod((3, 10), Allegiance.Enemy, self.buildings),
            buildings.Farm((3, 14), Allegiance.Enemy, self.buildings),
            buildings.Tower((7, 10), Allegiance.Enemy, self.buildings),
            units.Worker((21, 22), Allegiance.Player, self.units),
            units.Worker((21, 23), Allegiance.Player, self.units),
            units.Worker((21, 24), Allegiance.Player, self.units),
            units.Worker((22, 22), Allegiance.Player, self.units),
            units.Worker((22, 23), Allegiance.Player, self.units),
            units.Worker((22, 24), Allegiance.Player, self.units),
            units.Worker((11, 11), Allegiance.Enemy, self.units),
            units.Queen((13, 13), Allegiance.Player, self.units),
            units.Queen((14, 14), Allegiance.Enemy, self.units)
        )
        self.selected_entity = None
        director.global_data["entities"] = self.entities
        director.global_data["buildings"] = self.buildings
        director.global_data["units"] = self.units
        director.global_data["terrain"] = terrain

        self.inventory = resources.Inventory(50, 50, 50, Allegiance.Player)
        self.enemy_inventory = resources.Inventory(50, 50, 50, Allegiance.Enemy)
        self.overlay = overlay.Overlay(terrain, self.camera, self.inventory)
        director.global_data["player_inventory"] = self.inventory
        director.global_data["enemy_inventory"] = self.enemy_inventory
    
    def handle_events(self, events):
        mouse = pygame.mouse.get_pos()
        pressed = pygame.key.get_pressed()
        overlay_usurped = self.overlay.handle_events(mouse, events)

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.cursor_state == CursorState.Build:
                        self.cursor_state = CursorState.Select
                        self.ghost_building = None
                    else:
                        director.next_scene = director.get_scene("Pause")(self)
                if event.key == pygame.K_h:
                    if self.selected_entity is not None:
                        self.selected_entity.health -= 5
            if event.type == pygame.MOUSEBUTTONUP and not overlay_usurped:
                if event.button == 1:
                    if self.cursor_state == CursorState.Select:
                        self.select_entity(mouse)
                    elif self.cursor_state == CursorState.Build:
                        self.finish_construction()
            elif event.type == pygame.MOUSEBUTTONDOWN and not overlay_usurped:
                if event.button == 3:
                    self.marker = (*isometric.screen_to_world_coords(*mouse, self.camera), 120)
                    self.check_targeting()

        if mouse[1] > SCREEN_HEIGHT - 20:
            self.camera.move(0, self.cam_speed)
        elif mouse[1] < 20:
            self.camera.move(0, -self.cam_speed)
        if mouse[0] > SCREEN_WIDTH - 20:
            self.camera.move(self.cam_speed, 0)
        elif mouse[0] < 20:
            self.camera.move(-self.cam_speed, 0)

        self.selector_prev = self.selector
        self.selector = isometric.screen_to_tile_coords(*mouse, self.camera)
        if self.selector[0] < 0 or self.selector[0] >= len(terrain[0]) or self.selector[1] < 0 or self.selector[1] >= len(terrain) or overlay_usurped:
            self.selector = None
        debug.debug("selector", self.selector)
        if self.selected_entity is not None:
            debug.debug("health", self.selected_entity.health)
            if isinstance(self.selected_entity, units.Unit):
                debug.debug("task", self.selected_entity.task.__class__.__name__)
                debug.debug("target", self.selected_entity.target)
                
    def update(self, dt):
        self.entities.update(dt)
        self.inventory.update(self.units, self.buildings)
        self.overlay.update(self.selected_entity)

        if self.marker is not None:
            x, y, t = self.marker
            self.marker = (x, y, t-1) if t > 0 else None

        if self.cursor_state == CursorState.Build:
            if self.selector != self.selector_prev and self.selector != None:
                walkmap = pathfinding.create_walkable_map(terrain, self.buildings, buildings.Building.blacklist)
                self.invalid_tiles = buildings.blocked_tiles(walkmap, self.selector, self.ghost_building)

        if self.selected_entity is not None:
            if self.selected_entity.health <= 0:
                self.selected_entity = None

        debug.debug("selected", self.selected_entity.__class__.__name__)

    def render(self, surface):
        surface.fill(colors.black)

        # Draw the map
        for rect, surf in self.map:
            if rect.colliderect(self.camera.rect):
                surface.blit(surf, (rect.left - self.camera.rect.left, rect.top - self.camera.rect.top))

        if self.cursor_state == CursorState.Select:
            # Draw the green indicator showing which entity is selected
            match self.selected_entity:
                case buildings.Building():
                    img = {1: self.selected1_image, 2: self.selected2_image, 3: self.selected3_image}[self.selected_entity.area]
                    r = img.get_rect().move_to(center=isometric.world_to_screen_coords(*self.selected_entity.get_center(), self.camera))
                    surface.blit(img, r)
                case units.Unit():
                    img = image.load_image("technical/selected_unit")
                    px, py = isometric.tile_to_screen_coords(*self.selected_entity.pos, self.camera, True)
                    r = img.get_rect().move_to(center=(px, py+10))
                    surface.blit(img, r)

            # Only draw the selector when in bounds 
            if self.selector is not None and 0 <= self.selector[0] < 100 and 0 <= self.selector[1] < 100:
                px, py = isometric.tile_to_screen_coords(*self.selector, self.camera)
                r = pygame.Rect(0, 0, 160, 84).move_to(center=(px, py))
                surface.blit(self.selector_image, r)
        elif self.cursor_state == CursorState.Build and self.selector is not None:
            ghost = self.ghost_building

            for tile in self.invalid_tiles:
                r = pygame.Rect(0, 0, 160, 84).move_to(center=isometric.tile_to_screen_coords(*tile, self.camera))
                surface.blit(self.invalid_image, r)

            invalid = '' if len(self.invalid_tiles) == 0 else '_invalid'
            img = image.load_image(f"buildings/{ghost.name}_ghost{invalid}")
            r = pygame.Rect(0, 0, *img.size)
            px, py = isometric.tile_to_screen_coords(*self.selector, self.camera)
            ox = 80 if ghost.area == buildings.Area.TwoByTwo else 0
            r = r.move_to(centerx = px + ox, bottom = py + ghost.bottom_offset)
            surface.blit(img, r)

        # if a worker is busy building, show the building's ghost
        for unit in self.units:
            if unit.allegiance == Allegiance.Player and isinstance(unit.task, units.Build):
                ghost = unit.task.ghost_building
                img = image.load_image(f"buildings/{ghost.name}_ghost")
                r = pygame.Rect(0, 0, *img.size)
                px, py = isometric.tile_to_screen_coords(*unit.task.pos, self.camera)
                ox = 80 if ghost.area == buildings.Area.TwoByTwo else 0
                r = r.move_to(centerx = px + ox, bottom = py + ghost.bottom_offset)
                surface.blit(img, r)

        # Draw all entities and their shadows
        self.entities.draw_shadows(surface)
        self.entities.draw(surface)

        # Draw the walking-target marker
        if self.marker is not None:
            x, y, t = self.marker
            px, py = isometric.world_to_screen_coords(x, y, self.camera)
            r = self.marker_image.get_rect().move_to(centerx=px, bottom = py - math.sin(t / 10) * 10)
            self.marker_image.set_alpha(255 if t > 20 else pygame.math.remap(20, 0, 255, 0, t))
            surface.blit(self.marker_image, r)

        self.overlay.render(surface)

    def initialize_actions(self):
        """
        Set all the onclick functions of the actions
        """
        actions.BuildPod.onclick = partial(self.initiate_construction, buildings.Pod)
        actions.BuildFarm.onclick = partial(self.initiate_construction, buildings.Farm)
        actions.BuildFoundry.onclick = partial(self.initiate_construction, buildings.Foundry)
        actions.BuildLumbermill.onclick = partial(self.initiate_construction, buildings.Lumbermill)
        actions.BuildBarracks.onclick = partial(self.initiate_construction, buildings.Barracks)
        actions.BuildSiegery.onclick = partial(self.initiate_construction, buildings.Siegery)
        actions.BuildTower.onclick = partial(self.initiate_construction, buildings.Tower)
        actions.BuildNexus.onclick = partial(self.initiate_construction, buildings.Nexus)

        actions.CreateWorker.onclick = partial(print, "Creating a worker :))))")

    def select_entity(self, mouse: Coords):
        """
        Detect whether a building or unit is selected by a mouse click
        """
        try:
            if self.selector is not None and 0 <= self.selector[0] < 100 and 0 <= self.selector[1] < 100:
                for unit in self.units:
                    screen_pos = isometric.tile_to_screen_coords(*unit.pos, self.camera, True)
                    if math.dist(screen_pos, mouse) < unit.size:
                        self.selected_entity = unit
                        raise EntitySelected
                for building in self.buildings:
                    if building.occupies_tile(self.selector):
                        self.selected_entity = building
                        raise EntitySelected
        except EntitySelected:
            if self.selected_entity is not None and self.selected_entity.sound is not None:
                self.audio.play_sound(self.selected_entity.sound)
        else:
            self.selected_entity = None

    def populate_map(self):
        """
        Add the resource entities to the world
        """
        for y, row in enumerate(terrain):
            for x , cell in enumerate(row):
                if cell == 2:
                    self.entities.add(resources.Tree((x, y), self.resources))
                elif cell == 5:
                    self.entities.add(resources.Bush((x, y), self.resources))
                elif cell == 6:
                    self.entities.add(resources.Ore((x, y), self.resources))

    def check_targeting(self):
        """
        Check whether targeting can be passed onto the selected entity, and do so if it can
        """
        if isinstance(self.selected_entity, units.Unit) and self.selected_entity.allegiance == Allegiance.Player:
            x, y, _ = self.marker
            rounded = round(self.selected_entity.pos[0]), round(self.selected_entity.pos[1])
            path = pathfinding.pathfind(pathfinding.create_walkable_map(terrain, self.buildings, self.selected_entity.blacklist), rounded, isometric.world_to_tile_coords(x, y))
            if path:
                path[-1] = isometric.world_to_tile_coords(x, y, True)
                self.selected_entity.set_targets(path)
                self.selected_entity.set_task((x, y))
            else:
                pass  # TODO: PLAY FAIL SOUND EFFECT

    def initiate_construction(self, building: type[buildings.Building]):
        """
        Setup the building's ghost for construction
        """
        self.cursor_state = CursorState.Build
        self.ghost_building = building
        walkmap = pathfinding.create_walkable_map(terrain, self.buildings, buildings.Building.blacklist)
        selector = (0, 0) if self.selector is None else self.selector
        self.invalid_tiles = buildings.blocked_tiles(walkmap, selector, self.ghost_building)

    def finish_construction(self):
        """
        Place the ghost building
        """
        if len(self.invalid_tiles) == 0:
            rounded = round(self.selected_entity.pos[0]), round(self.selected_entity.pos[1])
            self.selected_entity.task = units.Build(self.ghost_building, self.selector, Allegiance.Player, rounded)
            path = pathfinding.pathfind(pathfinding.create_walkable_map(terrain, self.buildings, self.selected_entity.blacklist), rounded, self.selector)
            self.selected_entity.set_targets(path)

            self.cursor_state = CursorState.Select
            self.selected_entity = None
