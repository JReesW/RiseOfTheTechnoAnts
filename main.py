import sys
import pygame
import pygame.freetype

from engine import debug, director
from settings import *

pygame.init()
pygame.freetype.init()


screen = pygame.display.set_mode(
    SCREEN_SIZE,
    pygame.FULLSCREEN | pygame.SCALED
)
pygame.display.set_caption("Rise of the Techno-Ants")


FPS = 60
clock = pygame.time.Clock()
running = True

director.find_scenes()
director.change_scene("Startup")
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

    screen.blit(surface, (0, 0))

    # Draw the surface to the screen
    pygame.display.flip()
