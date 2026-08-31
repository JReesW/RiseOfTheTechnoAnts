import sys
from pathlib import Path
import pygame

from engine import debug, director, mouse
from engine.util import get_path

pygame.init()
pygame.freetype.init()


display_info = pygame.display.Info()

SCREEN_SIZE = SCREEN_WIDTH, SCREEN_HEIGHT = (1920, 1080)
SCALED_SIZE = SCALED_WIDTH, SCALED_HEIGHT = (display_info.current_w, display_info.current_h)
SCALE = pygame.Vector2(SCALED_WIDTH / SCREEN_WIDTH, SCALED_HEIGHT / SCREEN_HEIGHT)


screen = pygame.display.set_mode(
    SCALED_SIZE,
    # pygame.FULLSCREEN
)
pygame.display.set_caption("Pygame project")


FPS = 60
clock = pygame.time.Clock()
running = True

director.find_scenes()
director.change_scene("Game")
director._set_scene()

surface = pygame.Surface(SCREEN_SIZE, pygame.SRCALPHA)

while running:
    dt = clock.tick(FPS)

    surface.fill((0, 0, 0, 0))

    events = pygame.event.get()

    for event in events:
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_q and (event.mod & pygame.KMOD_CTRL)):
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_BACKQUOTE:
            debug.disable() if debug.is_active() else debug.enable()

    # Call the necessary scene functions of the active scene
    director.scene.handle_events(events)
    director.scene.update(dt)
    director.scene.render(surface)

    if director.next_scene is not None:
        director._set_scene()

    if debug.is_active():
        debug.render(surface)

    screen.blit(pygame.transform.scale(surface, SCALED_SIZE), (0, 0))

    # Draw the surface to the screen
    pygame.display.flip()
