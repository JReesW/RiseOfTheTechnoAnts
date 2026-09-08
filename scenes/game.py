import pygame
from engine.scene import Scene, Camera
from engine import colors, image, debug
from settings import SCREEN_SIZE, SCREEN_HEIGHT, SCREEN_WIDTH

from game import isometric, maps, entities, buildings, resources, units

import random, math


class EntitySelected(Exception):
    """"""


terrain = []
with open("resources/output.txt", 'r') as file:
    for line in file.readlines():
        terrain.append([int(c) for c in line.strip()])


class Game(Scene):
    def __init__(self):
        isometric.initialize_isometry(len(terrain), 160, 84)
        
        self.selector_image = image.load_image("selector")
        self.selected1_image = image.load_image("selected1")
        self.selected2_image = image.load_image("selected2")
        self.selected3_image = image.load_image("selected3")
        self.marker_image = image.load_image("marker")
        self.selector = (0, 0)
        self.marker = None

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
            buildings.Nexus((3, 3), self.buildings),
            buildings.Nexus((90, 90), self.buildings),
            buildings.Pod((3, 8), self.buildings),
            buildings.Farm((3, 13), self.buildings),
            buildings.Barracks((7, 9), self.buildings),
            buildings.Siegery((7, 13), self.buildings),
            buildings.Farm((10, 37), self.buildings),
            buildings.Nexus((20, 35), self.buildings),
            units.Worker((6, 3), self.units)
        )
        self.selected_entity = None
    
    def handle_events(self, events):
        mouse = pygame.mouse.get_pos()
        pressed = pygame.key.get_pressed()

        for event in events:
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.select_entity(mouse)
            elif event.type == pygame.MOUSEBUTTONDOWN:
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

        self.selector = isometric.screen_coords_to_tile(*mouse, self.camera)
        debug.debug("selector", self.selector)
                
    def update(self, dt):
        self.entities.update(dt)

        if self.marker is not None:
            x, y, t = self.marker
            self.marker = (x, y, t-1) if t > 0 else None

        for unit in self.units:
            debug.debug("ant pos", (unit.pos))
            debug.debug("ant spos", isometric.tile_to_screen_coords(*unit.pos, self.camera))
        debug.debug("selected", self.selected_entity.__class__.__name__)

    def render(self, surface):
        surface.fill(colors.black)

        # Draw the map
        for rect, surf in self.map:
            if rect.colliderect(self.camera.rect):
                surface.blit(surf, (rect.left - self.camera.rect.left, rect.top - self.camera.rect.top))

        # Draw the green indicator showing which entity is selected
        match self.selected_entity:
            case buildings.Building():
                img = {1: self.selected1_image, 2: self.selected2_image, 3: self.selected3_image}[self.selected_entity.area]
                r = img.get_rect().move_to(center=isometric.world_to_screen_coords(*self.selected_entity.get_center(), self.camera))
                surface.blit(img, r)
            case units.Unit():
                img = image.load_image("selected_unit")
                px, py = isometric.tile_to_screen_coords(*self.selected_entity.pos, self.camera, True)
                r = img.get_rect().move_to(center=(px, py+10))
                surface.blit(img, r)

        # Only draw the selector when in bounds 
        if 0 <= self.selector[0] < 100 and 0 <= self.selector[1] < 100:
            px, py = isometric.tile_to_screen_coords(*self.selector, self.camera)
            r = pygame.Rect(0, 0, 160, 84).move_to(center=(px, py))
            surface.blit(self.selector_image, r)

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

    def select_entity(self, mouse: tuple[int, int]):
        """
        Detect whether a building or unit is selected by a mouse click
        """
        try:
            if 0 <= self.selector[0] < 100 and 0 <= self.selector[1] < 100:
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
            pass
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

    def check_targeting(self):
        """
        Check whether targeting can be passed onto the selected entity, and do so if it can
        """
        if isinstance(self.selected_entity, units.Unit):
            x, y, _ = self.marker
            self.selected_entity.set_target(isometric.world_coords_to_tile(x, y, True))
