import pygame
import pygame.freetype
from engine.scene import Scene
from engine import colors, director, image, text
from game import saveSystem

class Credits(Scene):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        centerx = 1920/2

        self.background = image.load_image("mainmenu")

        self.backRect = pygame.Rect(100, 900, 500, 100)
        self.backRect.centerx = centerx

        self.mouse = (0, 0)

        self.jreesw_s, self.jreesw_r = text.render("JReesW", colors.white, "Arial", 60, True)
        self.jreesw_r.topleft = (150, 100)
        self.jreesw_ds, self.jreesw_dr = text.render("Project lead, design, gameplay, sound effects", colors.white, "Arial", 40)
        self.jreesw_dr.topleft = self.jreesw_r.left, self.jreesw_r.bottom + 15

        self.curyde_s, self.curyde_r = text.render("Curyde", colors.white, "Arial", 60, True)
        self.curyde_r.topright = (1770, 250)
        self.curyde_ds, self.curyde_dr = text.render("Artwork", colors.white, "Arial", 40)
        self.curyde_dr.topright = self.curyde_r.right, self.curyde_r.bottom + 10

        self.mondmar_s, self.mondmar_r = text.render("Mondfuch-Marjulie", colors.white, "Arial", 60, True)
        self.mondmar_r.topleft = (150, 400)
        self.mondmar_ds, self.mondmar_dr = text.render("Soundtrack", colors.white, "Arial", 40)
        self.mondmar_dr.topleft = self.mondmar_r.left, self.mondmar_r.bottom + 10

        self.rds_s, self.rds_r = text.render("RDS", colors.white, "Arial", 60, True)
        self.rds_r.topright = (1770, 550)
        self.rds_ds, self.rds_dr = text.render("Additional programming", colors.white, "Arial", 40)
        self.rds_dr.topright = self.rds_r.right, self.rds_r.bottom + 10

    def is_in_rect(self, rect : pygame.Rect, pos):
        return (rect.x + rect.w > pos[0]) and (rect.x < pos[0]) and (rect.y + rect.h > pos[1]) and (rect.y < pos[1])
    
    def handle_events(self, events):
        self.mouse = pygame.mouse.get_pos()
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.backRect.collidepoint(self.mouse):
                    director.change_scene("MainMenu", keep_music=True)

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    director.change_scene("MainMenu", keep_music=True)
    
    def update(self, dt):
        pass
    
    def render(self, surface):
        surface.fill((27, 12, 31))
        surface.blit(self.background)

        font = pygame.freetype.SysFont("Arial", 26)

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

        surface.blit(self.jreesw_s, self.jreesw_r)
        surface.blit(self.curyde_s, self.curyde_r)
        surface.blit(self.mondmar_s, self.mondmar_r)
        surface.blit(self.rds_s, self.rds_r)
        surface.blit(self.jreesw_ds, self.jreesw_dr)
        surface.blit(self.curyde_ds, self.curyde_dr)
        surface.blit(self.mondmar_ds, self.mondmar_dr)
        surface.blit(self.rds_ds, self.rds_dr)

        surface.blit(backTextSurface, backTextRect)