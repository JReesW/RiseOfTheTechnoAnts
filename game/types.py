"""
Collection of custom types
"""


import enum


type Tilemap = list[list[int]]
type Coords = tuple[int, int]


class Allegiance(enum.Enum):
    """
    Indicates to which party something belongs
    """
    Player = 0
    Enemy = 1
    Nature = 2


class Area(enum.IntEnum):
    """
    The side length of the area occupied by a building
    """
    OneByOne = 1
    TwoByTwo = 2
    ThreeByThree = 3


class UnitState(enum.IntEnum):
    """
    What a unit is currently doing
    """
    Idle = 0
    Walking = 1
    Building = 2
    Gathering = 3
    Attacking = 4


class Direction(enum.StrEnum):
    """
    Directions one can move on the map
    """
    East = "X"
    South = "XF"
    West = "YF"
    North = "Y"
