import pygame
import pygame.freetype
from engine.scene import Scene
from engine import colors, director, image
from game import saveSystem

class Settings(Scene):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        saveSystem.load_save_data()

        centerx = 1920/2

        self.background = image.load_image("mainmenu")

        self.soundRect = pygame.Rect(100, 100, 500, 100)
        self.soundRect.centerx = centerx
        self.soundVolume = saveSystem.saveData["soundVolume"]
        self.editingSound = False

        self.musicRect = pygame.Rect(100, 230, 500, 100)
        self.musicRect.centerx = centerx
        self.musicVolume = saveSystem.saveData["musicVolume"]
        self.editingMusic = False

        self.backRect = pygame.Rect(100, 800, 500, 100)
        self.backRect.centerx = centerx

        self.mouse = (0, 0)

    def is_in_rect(self, rect : pygame.Rect, pos):
        return (rect.x + rect.w > pos[0]) and (rect.x < pos[0]) and (rect.y + rect.h > pos[1]) and (rect.y < pos[1])
    
    def updateSoundVolume(self):
        self.soundVolume = max(0, min(1, (self.mouse[0] - self.soundRect.left) / (self.soundRect.right - self.soundRect.left)))
        saveSystem.saveData["soundVolume"] = self.soundVolume
        saveSystem.save_save_data(saveSystem.saveData)
        director.audio.set_sfx_volume(self.soundVolume)
    
    def updateMusicVolume(self):
        self.musicVolume = max(0, min(1, (self.mouse[0] - self.musicRect.left) / (self.musicRect.right - self.musicRect.left)))
        saveSystem.saveData["musicVolume"] = self.musicVolume
        saveSystem.save_save_data(saveSystem.saveData)
        director.audio.set_music_volume(self.musicVolume)
    
    def resetSettings(self):
        self.soundVolume = saveSystem.saveData["soundVolume"]
        self.musicVolume = saveSystem.saveData["musicVolume"]

    def handle_events(self, events):
        self.mouse = pygame.mouse.get_pos()
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.is_in_rect(self.soundRect, self.mouse) and abs(self.mouse[1] - self.soundRect.centery) < 5:
                    self.editingSound = True
                    self.updateSoundVolume()
                if self.is_in_rect(self.musicRect, self.mouse) and abs(self.mouse[1] - self.musicRect.centery) < 5:
                    self.editingMusic = True
                    self.updateMusicVolume()
                if self.backRect.collidepoint(self.mouse):
                    director.change_scene("MainMenu", keep_music=True)

            elif event.type == pygame.MOUSEBUTTONUP:
                self.editingSound = False
                self.editingMusic = False
            elif event.type == pygame.MOUSEMOTION:
                if self.editingSound:
                    self.updateSoundVolume()
                if self.editingMusic:
                    self.updateMusicVolume()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    director.change_scene("MainMenu", keep_music=True)
    
    def update(self, dt):
        pass
    
    def render(self, surface):
        surface.fill((27, 12, 31))
        surface.blit(self.background)

        font = pygame.freetype.SysFont("Arial", 26)

        soundTitleSurface, soundTitleRect = font.render("Sound Volume", colors.white)

        soundTitleRect.centerx = self.soundRect.centerx
        soundTitleRect.top = self.soundRect.top + 5

        #light_grey
        backgroundColor = (26, 17, 46, 255)

        backgroundRect = pygame.Rect(self.soundRect)
        backgroundRect.width += 130
        backgroundRect.centery = self.soundRect.centery
        backgroundRect.right = self.soundRect.right + 50

        pygame.draw.rect(surface, backgroundColor, backgroundRect)

        surface.blit(soundTitleSurface, soundTitleRect)

        pygame.draw.line(surface, colors.gray, self.soundRect.midleft, self.soundRect.midright, 5)

        circleX = pygame.math.lerp(self.soundRect.left, self.soundRect.right, self.soundVolume)

        pygame.draw.circle(surface, colors.white_smoke, (circleX, self.soundRect.centery), 5)
        pygame.draw.circle(surface, colors.slate_gray, (circleX, self.soundRect.centery), 3)

        soundVolumeTextSurface, soundVolumeTextRect = font.render(f"{self.soundVolume:.0%}", colors.white)

        soundVolumeTextRect.right = self.soundRect.left - 10
        soundVolumeTextRect.centery = self.soundRect.centery

        surface.blit(soundVolumeTextSurface, soundVolumeTextRect)

        #music
        musicTitleSurface, musicTitleRect = font.render("Music Volume", colors.white)

        musicTitleRect.centerx = self.musicRect.centerx
        musicTitleRect.top = self.musicRect.top + 5

        #light_grey
        backgroundColor = (26, 17, 46, 255)

        backgroundRect = pygame.Rect(self.musicRect)
        backgroundRect.width += 130
        backgroundRect.centery = self.musicRect.centery
        backgroundRect.right = self.musicRect.right + 50

        pygame.draw.rect(surface, backgroundColor, backgroundRect)

        surface.blit(musicTitleSurface, musicTitleRect)

        pygame.draw.line(surface, colors.gray, self.musicRect.midleft, self.musicRect.midright, 5)

        circleX = pygame.math.lerp(self.musicRect.left, self.musicRect.right, self.musicVolume)

        pygame.draw.circle(surface, colors.white_smoke, (circleX, self.musicRect.centery), 5)
        pygame.draw.circle(surface, colors.slate_gray, (circleX, self.musicRect.centery), 3)

        musicVolumeTextSurface, musicVolumeTextRect = font.render(f"{self.musicVolume:.0%}", colors.white)

        musicVolumeTextRect.right = self.musicRect.left - 10
        musicVolumeTextRect.centery = self.musicRect.centery

        surface.blit(musicVolumeTextSurface, musicVolumeTextRect)

        #back button
        hovered = self.backRect.collidepoint(self.mouse)
        
        if hovered:
            outline = pygame.Surface((self.backRect.width + 6, self.backRect.height + 6))
            outlineRect = outline.get_rect(center=self.backRect.center)

            outline.fill((57, 41, 92))
            surface.blit(outline, outlineRect)

        backgroundColor = (26, 17, 46, 255)
        pygame.draw.rect(surface, backgroundColor, self.backRect)

        backTextSurface, backTextRect = font.render("Back", colors.white)
        backTextRect.center = self.backRect.center

        surface.blit(backTextSurface, backTextRect)