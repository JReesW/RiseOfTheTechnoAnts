import pygame


from engine.scene import Scene
from engine import director, colors, text


class Pause(Scene):
    def __init__(self, game_scene: Scene):
        self.game_scene = game_scene

        self.rect = pygame.Rect(0, 0, 600, 400).move_to(center=(960, 540))
        self.pause_menu = pygame.Surface((600, 400), pygame.SRCALPHA)
        pygame.draw.rect(self.pause_menu, colors.dark_slate_blue, (0, 0, 600, 400), border_radius=35)
        pygame.draw.rect(self.pause_menu, colors.slate_blue, (0, 0, 600, 400), 3, border_radius=35)
        self.text, self.text_rect = text.render("GAME PAUSED", colors.white, "Arial", 48, True)
        self.text_rect.top, self.text_rect.centerx = 420, 960

        self.button_rect = pygame.Rect(0, 0, 450, 100).move_to(centerx=960, bottom=700)
        self.button = pygame.Surface((450, 100), pygame.SRCALPHA)
        pygame.draw.rect(self.button, colors.dark_slate_blue, (0, 0, 450, 100), border_radius=15)
        pygame.draw.rect(self.button, colors.slate_blue, (0, 0, 450, 100), 3, border_radius=15)
        self.button_hover = pygame.Surface((450, 100), pygame.SRCALPHA)
        pygame.draw.rect(self.button_hover, colors.alter(colors.dark_slate_blue, 0.8), (0, 0, 450, 100), border_radius=15)
        pygame.draw.rect(self.button_hover, colors.slate_blue, (0, 0, 450, 100), 3, border_radius=15)
        self.button_label, self.label_rect = text.render("QUIT", colors.white, "Arial", 36, True)
        self.label_rect.center = self.button_rect.center
        self.hovering = False

    def handle_events(self, events: list[pygame.event.Event]):
        mouse = pygame.mouse.get_pos()

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    director.next_scene = self.game_scene
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self.button_rect.collidepoint(mouse):
                        director.quit()

        self.hovering = self.button_rect.collidepoint(mouse)

    def update(self, dt):
        pass

    def render(self, surface):
        self.game_scene.render(surface)

        surface.blit(self.pause_menu, self.rect)
        surface.blit(self.text, self.text_rect)
        button = self.button_hover if self.hovering else self.button
        surface.blit(button, self.button_rect)
        surface.blit(self.button_label, self.label_rect)

