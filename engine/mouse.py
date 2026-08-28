import pygame


def mousepos() -> tuple[int, int]:
    """
    Get a properly scaled mousepos
    """
    w, h = pygame.display.get_window_size()
    x, y = pygame.mouse.get_pos()
    mx = int(pygame.math.remap(0, w, 0, 1920, x))
    my = int(pygame.math.remap(0, h, 0, 1080, y))
    return mx, my
