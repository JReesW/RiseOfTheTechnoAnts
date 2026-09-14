import pygame
import pygame.freetype
import sys
from engine.scene import Scene
from engine import colors, image, mouse, debug, audio, director

class MainMenu(Scene):
    def __init__(self, *args, **kwargs):
        self.logo = image.load_image("teamlogo").convert_alpha()
        self.background = image.load_image("mainmenu")
        self.title = pygame.transform.scale_by(image.load_image("title"), 2)
        self.title_rect = pygame.Rect(0, 0, *self.title.size).move_to(centerx=960, top=150)

        self.buttons: list[pygame.Rect] = []
        centerx = 1920/2
        #start, settings, credits?, quit
        self.startButton = pygame.Rect((10, 500, 300, 70))
        self.startButton.centerx = centerx
        self.buttons.append(self.startButton)

        self.settingsButton = pygame.Rect((10, 580, 300, 70))
        self.settingsButton.centerx = centerx
        self.buttons.append(self.settingsButton)

        self.creditsButton = pygame.Rect((10, 660, 300, 70))
        self.creditsButton.centerx = centerx
        self.buttons.append(self.creditsButton)

        self.quitButton = pygame.Rect((10, 740, 300, 70))
        self.quitButton.centerx = centerx
        self.buttons.append(self.quitButton)

        self.mouse = (0,0)

        if "keep_music" not in kwargs:
            director.audio.play_music("antlers")
    
    def handle_events(self, events):
        self.mouse = pygame.mouse.get_pos()
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                for button in self.buttons:
                    if button.collidepoint(self.mouse):
                        if button == self.startButton:
                            director.change_scene("Loading")
                        elif button == self.settingsButton:
                            director.change_scene("Settings")
                        elif button == self.creditsButton:
                            director.change_scene("Credits")
                        elif button == self.quitButton:
                            pygame.quit()
                            sys.exit()
    
    def update(self, dt):
        pass

    def is_in_rect(self, rect : pygame.Rect, pos):
        return (rect.x + rect.w > pos[0]) and (rect.x < pos[0]) and (rect.y + rect.h > pos[1]) and (rect.y < pos[1])

    def render(self, surface):
        surface.fill((27, 12, 31))
        surface.blit(self.background)
        surface.blit(self.title, self.title_rect)

        #pygame.draw.rect(surface, colors.red, self.logoRect)
        
        for button in self.buttons:
            hovered = button.collidepoint(self.mouse)

            if hovered:
                outline = pygame.Surface((button.width + 6, button.height + 6))
                outlineRect = outline.get_rect(center=button.center)

                outline.fill((57, 41, 92))

                surface.blit(outline, outlineRect)
            
            pygame.draw.rect(surface, (26, 17, 46), button)

            if button == self.startButton:
                font = pygame.freetype.SysFont("Arial", 26)
                textSurface, textRect = font.render("Start", colors.white)
                textRect.center = button.center

                surface.blit(textSurface, textRect)
            elif button == self.settingsButton:
                font = pygame.freetype.SysFont("Arial", 26)
                textSurface, textRect = font.render("Settings", colors.white)
                textRect.center = button.center

                surface.blit(textSurface, textRect)
            elif button == self.creditsButton:
                font = pygame.freetype.SysFont("Arial", 26)
                textSurface, textRect = font.render("Credits", colors.white)
                textRect.center = button.center

                surface.blit(textSurface, textRect)
            elif button == self.quitButton:
                font = pygame.freetype.SysFont("Arial", 26)
                textSurface, textRect = font.render("Quit", colors.white)
                textRect.center = button.center

                surface.blit(textSurface, textRect)