"""
Functions to help manage the isometric perspective of the game

Handy info about the different coordinate spaces:
 - tile space is the integer space of the tiles' indices in the 2D terrain array
 - world space is the pixel coordinate on the entire world map
 - screen space is the pixel coordinate on the screen, relative to where the camera is
"""

from engine.scene import Camera
from math import floor


__settings = {
    "dimension": None,
    "tile_width": None,
    "tile_height": None,
    "initialized": False
}


def initialize_isometry(dimension: int, tile_width: int, tile_height: int):
    """
    Initialize the isometry module with the size of the map and the size of the tiles.  
     - dimension    ->  the width/height of the map in tiles (map is square, so only one needed)
     - tile_width   ->  the width of a tile image in pixels
     - tile_height  ->  the height of a tile image in pixels
    """
    __settings["dimension"] = dimension
    __settings["tile_width"] = tile_width
    __settings["tile_height"] = tile_height
    __settings["initialized"] = True


def tile_size() -> tuple[int, int]:
    """
    Return the pixel size of the tiles
    """
    if not __settings["initialized"]:
            raise Exception("Please initialize the isometry settings before using")

    return __settings["tile_width"], __settings["tile_height"]
    

def tile_to_world_coords(x: int, y: int, world_size: tuple[int, int] = None) -> tuple[int, int]:
    """
    Return the center of a tile in world coordinates
    """
    if not __settings["initialized"]:
        raise Exception("Please initialize the isometry settings before using")

    w, _ = get_world_size() if world_size is None else world_size
    px = (w // 2) + (x - y) * 80
    py = 42 + (x + y) * 42
    return px, py


def tile_to_screen_coords(x: int, y: int, camera: Camera) -> tuple[int, int]:
    """
    Return the center of a tile in screen coordinates
    """
    px, py = tile_to_world_coords(x, y)
    return px - camera.rect.left, py - camera.rect.top


def world_to_screen_coords(x: int, y: int, camera: Camera) -> tuple[int, int]:
    """
    Convert world coords to screen coords
    """
    return x - camera.rect.left, y - camera.rect.top


def get_world_size() -> tuple[int, int]:
    """
    Return the world size
    """
    if not __settings["initialized"]:
        raise Exception("Please initialize the isometry settings before using")

    return __settings["dimension"] * __settings["tile_width"], __settings["dimension"] * __settings["tile_height"]


def screen_coords_to_tile(x: int, y: int, camera: Camera) -> tuple[int, int]:
    """
    Return the tile corresponding to the given screen coords
    """
    origin_x = get_world_size()[0] / 2 - camera.rect.left
    origin_y = -camera.rect.top

    x -= origin_x
    y -= origin_y

    tx = (x / 80 + y / 42) / 2
    ty = (y / 42 - x / 80) / 2

    return floor(tx), floor(ty)
