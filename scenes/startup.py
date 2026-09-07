import pygame
from engine.scene import Scene
from engine import colors, image, mouse, debug, audio, director

class Startup(Scene):
    def __init__(self, *args, **kwargs):
        self.time = 0
        self.logo = image.load_image("teamlogo").convert_alpha()

        self.state = 0

        self.audio_handler = audio.AudioHandler()
    
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.space_held = not self.space_held
    
    def update(self, dt):
        self.time += dt / 1000

        if self.state == 0 and self.time >= 1:
            self.state = 1
            self.audio_handler.play_music("palmtune 8", loops=0)

        if self.time > 4:
            director.change_scene("Fade", self, "Game")

        debug.debug("time", self.time)
        debug.debug("state", self.state)

    def render(self, surface):
        surface.fill((27, 12, 31))

        if self.state == 0 or self.state == 1:
            logo = self.logo.copy()

            progress = self.time / 2

            debug.debug("progress", progress)

            logo.set_alpha(int(progress * 255))
            # logo.fill(colors.white, special_flags=pygame.BLEND_RGB_ADD)

            surface.blit(logo, logo.get_rect(center=surface.get_rect().center))