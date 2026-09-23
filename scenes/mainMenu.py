import pygame

from engine.scene import Scene
from engine import colors, image, director, text

import sys


class MainMenu(Scene):
    def __init__(self, *args, **kwargs):
        self.logo = image.load_image("teamlogo").convert_alpha()
        self.background = image.load_image("mainmenu").copy()
        self.title = pygame.transform.scale_by(image.load_image("title"), 2)
        self.title_rect = pygame.Rect(0, 0, *self.title.size).move_to(centerx=960, top=150)

        self.buttons = {
            "Start": pygame.Rect(10, 500, 300, 70).move_to(centerx=960),
            "Settings": pygame.Rect(10, 580, 300, 70).move_to(centerx=960),
            "Credits": pygame.Rect(10, 660, 300, 70).move_to(centerx=960),
            "Quit": pygame.Rect(10, 740, 300, 70).move_to(centerx=960)
        }

        for label, button in self.buttons.items():
            pygame.draw.rect(self.background, (26, 17, 46), button)
            surf, rect = text.render(label, colors.white, "Arial", 26)
            rect.center = button.center
            self.background.blit(surf, rect)

        self.mouse = (0,0)

        if "keep_music" not in kwargs:
            director.audio.play_music("antlers")
    
    def handle_events(self, events):
        self.mouse = pygame.mouse.get_pos()
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                for label, button in self.buttons.items():
                    if button.collidepoint(self.mouse):
                        if label == "Start":
                            director.change_scene("HowToPlay")
                        elif label == "Settings":
                            director.change_scene("Settings")
                        elif label == "Credits":
                            director.change_scene("Credits")
                        elif label == "Quit":
                            pygame.quit()
                            sys.exit()
    
    def update(self, dt):
        pass

    def render(self, surface):
        surface.fill((27, 12, 31))
        surface.blit(self.background)
        surface.blit(self.title, self.title_rect)
        
        for button in self.buttons.values():
            if button.collidepoint(self.mouse):
                pygame.draw.rect(surface, (57, 41, 92), button, 3)
        