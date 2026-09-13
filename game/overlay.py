import pygame

from game import isometric, maps, resources, entities, units, buildings, actions
from game.types import *
from engine.scene import Camera
from engine import colors, image, text


actions_dictionary = {
    # buildings
    "nexus": [actions.CreateWorker, actions.CreateQueen],
    "barracks": [actions.CreateSoldier, actions.CreatePhrag],
    "siegery": [actions.CreateAlate, actions.CreateMajor],
    # units
    "worker": [actions.BuildPod, actions.BuildFarm, actions.BuildLumbermill, actions.BuildFoundry, actions.BuildBarracks, actions.BuildSiegery, actions.BuildTower],
    "queen": [actions.BuildNexus]
}


class Overlay:
    """
    Overlay manager for the actions menu, resources, minimap, and unit selection
    """

    def __init__(self, terrain: Tilemap, camera: Camera, inventory: resources.Inventory):
        # minimap
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

        # resources inventory
        self.inventory = inventory
        self.inventory_tab_rect = pygame.Rect(0, 0, 800, 52)
        self.inventory_tab = pygame.Surface(self.inventory_tab_rect.size)
        self.inventory_tab.fill(colors.dark_slate_blue)
        pygame.draw.rect(self.inventory_tab, colors.slate_blue, self.inventory_tab_rect, 3)
        images = ["wood", "metal", "food", "population"]
        for n in range(4):
            rb = pygame.Rect(200*n + 42, 10, 150, 32)
            rt = pygame.Rect(200*n + 9, 10, 182, 32)
            ri = pygame.Rect(200*n + 9, 10, 32, 32)
            pygame.draw.rect(self.inventory_tab, colors.light_steel_blue, rb)
            pygame.draw.rect(self.inventory_tab, colors.slate_gray, ri)
            pygame.draw.rect(self.inventory_tab, colors.black, rt, 1)
            self.inventory_tab.blit(image.load_image(f"icons/{images[n]}"), ri)

        # actions menu
        self.selected_label = None
        self.actions_menu_rect = pygame.Rect(0, 0, 260, 180).move_to(bottomleft=(0, 1080))
        self.actions_menu = pygame.Surface((260, 180))
        self.actions_menu.fill(colors.dark_slate_blue)
        pygame.draw.rect(self.actions_menu, colors.slate_blue, self.actions_menu.get_rect(), 3)
        self.selected_entity = None
        self.actions_rects = [pygame.Rect(n % 4 * 60 + 10, (n // 4) * 80 + 910, 60, 80) for n in range(8)]

        self.tooltips = {}
        self.current_tooltip = None
        self.generate_tooltips()
        self.mouse = (0, 0)

    def handle_events(self, mouse: Coords, events: list[pygame.event.Event]) -> bool:
        """
        Return whether the overlay has usurped the events
        """
        self.mouse = mouse
        self.current_tooltip = None

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
        elif self.inventory_tab_rect.collidepoint(mouse):
            materials = ["wood", "metal", "food", "population"]
            for n in range(4):
                rect = pygame.Rect(200*n + 9, 10, 182, 32)
                if rect.collidepoint(mouse):
                    self.current_tooltip = materials[n]
            return True
        elif self.selected_entity is not None and self.actions_menu_rect.collidepoint(mouse):
            if self.selected_entity.name in actions_dictionary:  # TODO: is name in dictionary check necessary at the end?
                for n, action in enumerate(actions_dictionary[self.selected_entity.name]):
                    if self.actions_rects[n].collidepoint(mouse):
                        for event in events:
                            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                                action.onclick()
                        if action.name in self.tooltips:
                            self.current_tooltip = action.name
            return True
        
        return False

    def update(self, selected: entities.Entity):
        # draw the name label if an entity just got selected
        if selected is not None and self.selected_entity is not selected:
            surf, rect = text.render(selected.display_name, colors.white, "Arial", 20, True)
            label_rect = pygame.Rect(0, 0, rect.width + 10, rect.height + 10)
            self.selected_label = pygame.Surface(label_rect.size, pygame.SRCALPHA)
            self.selected_label.fill(colors.dark_slate_blue)
            pygame.draw.rect(self.selected_label, colors.slate_blue, label_rect, 3)
            self.selected_label.blit(surf, rect.move_to(centery=label_rect.centery, left=5))

        self.selected_entity = selected

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

        # inventory tab
        surface.blit(self.inventory_tab, self.inventory_tab_rect)
        surf, rect = text.render(str(self.inventory.wood), colors.black, "Arial", 28, True)
        rect.centery, rect.right = self.inventory_tab_rect.centery, 185
        surface.blit(surf, rect)
        surf, rect = text.render(str(self.inventory.metal), colors.black, "Arial", 28, True)
        rect.centery, rect.right = self.inventory_tab_rect.centery, 385
        surface.blit(surf, rect)
        surf, rect = text.render(str(self.inventory.food), colors.black, "Arial", 28, True)
        rect.centery, rect.right = self.inventory_tab_rect.centery, 585
        surface.blit(surf, rect)
        color = colors.black if self.inventory.population <= self.inventory.population_cap else colors.red
        surf, rect = text.render(f"{self.inventory.population}/{self.inventory.population_cap}", color, "Arial", 28, True)
        rect.centery, rect.right = self.inventory_tab_rect.centery, 785
        surface.blit(surf, rect)

        # actions menu
        if self.selected_entity is not None and self.selected_entity.allegiance == Allegiance.Player:
            surface.blit(self.actions_menu, self.actions_menu_rect)

            if self.selected_entity.name in actions_dictionary:
                for n, action in enumerate(actions_dictionary[self.selected_entity.name]):
                    img = image.load_image(f"actions/{action.name}")
                    surface.blit(img, self.actions_rects[n])
            surface.blit(self.selected_label, self.selected_label.get_rect(bottomleft=self.actions_menu_rect.topleft))

        if self.current_tooltip is not None:
            tooltip, bottomleft = self.tooltips[self.current_tooltip]
            if bottomleft:
                surface.blit(tooltip, tooltip.get_rect(bottomleft=self.mouse))
            else:
                surface.blit(tooltip, tooltip.get_rect(topleft=self.mouse))

    def generate_tooltips(self):
        """
        Create pairings of surfaces and booleans, bools are for whether the tooltip should use topleft (False) or bottomleft (True) as anchor
        """
        self.tooltips["wood"] = (simple_tooltip("Wood"), False)
        self.tooltips["metal"] = (simple_tooltip("Metal"), False)
        self.tooltips["food"] = (simple_tooltip("Food"), False)
        self.tooltips["population"] = (simple_tooltip("Population"), False)

        self.tooltips["pod"] = (costly_tooltip("Pod", (50, 20, 0), "Housing that increases population cap"), True)
        self.tooltips["fungusfarm"] = (costly_tooltip("Farm", (100, 50, 30), "Turns collected leaves into food"), True)
        self.tooltips["lumbermill"] = (costly_tooltip("Lumbermill", (100, 50, 30), "Dropoff point for collected wood"), True)
        self.tooltips["foundry"] = (costly_tooltip("Foundry", (100, 50, 30), "Turns collected ore into metal"), True)
        self.tooltips["nexus"] = (costly_tooltip("Nexus", (100, 50, 30), "Creates workers and queens. You lose when your last Nexus is destroyed"), True)
        self.tooltips["barracks"] = (costly_tooltip("Barracks", (100, 50, 30), "Creates soldier ants"), True)
        self.tooltips["siegery"] = (costly_tooltip("Siegery", (100, 50, 30), "Creates stronger mechanical ants"), True)
        self.tooltips["tower"] = (costly_tooltip("Tower", (100, 50, 30), "Attacks nearby enemies"), True)

        self.tooltips["worker"] = (costly_tooltip("Worker", (100, 50, 30), "Collects resources and builds structures"), True)
        self.tooltips["queen"] = (costly_tooltip("Queen", (100, 50, 30), "Capable of creating a new Nexus"), True)
        self.tooltips["soldier"] = (costly_tooltip("Soldier", (100, 50, 30), "Basic foot soldier"), True)
        self.tooltips["phrag"] = (costly_tooltip("Phragmotist", (100, 50, 30), "Soldier with a shielded head, granting extra defence"), True)
        self.tooltips["alate"] = (costly_tooltip("Alate", (100, 50, 30), "Jet-powered, low-flying kamikaze that deals a ton of damage to buildings"), True)
        self.tooltips["major"] = (costly_tooltip("Major", (100, 50, 30), "Large, technologically enhanced soldier. Has trouble walking through forests"), True)


def simple_tooltip(txt: str) -> pygame.Surface:
    """
    Create a tooltip consisting of a single label
    """
    surf, rect = text.render(txt, colors.white, "Arial", 18, True)
    tooltip = pygame.Surface((rect.width + 20, rect.height + 10), pygame.SRCALPHA)
    tooltip.fill((0, 0, 0, 150))
    tt_rect = tooltip.get_rect()
    tooltip.blit(surf, rect.move_to(centery=tt_rect.centery, left=15))
    return tooltip


def costly_tooltip(title: str, cost: tuple[int, int, int], description: str):
    """
    Create a tooltip for something with a label, material costs, and a description
    """
    backdrop = image.load_image("technical/costly_tooltip")
    name_s, _ = text.render(title, colors.white, "Arial", 18, True)
    wood_s, _ = text.render(str(cost[0]), colors.white, "Arial", 18, True)
    metal_s, _ = text.render(str(cost[1]), colors.white, "Arial", 18, True)
    food_s, _ = text.render(str(cost[2]), colors.white, "Arial", 18, True)
    desc_s, desc_r = text.render(description, colors.white, "Arial", 18)
    surface = pygame.Surface((desc_r.width + 10, backdrop.get_rect().height), pygame.SRCALPHA)

    surface.blit(backdrop)
    surface.blit(name_s, (5, 5))
    surface.blit(wood_s, (32, 32))
    surface.blit(metal_s, (32, 55))
    surface.blit(food_s, (32, 77))
    surface.blit(desc_s, (5, 102))
    return surface
