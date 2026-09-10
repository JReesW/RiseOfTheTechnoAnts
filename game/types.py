import enum


type Tilemap = list[list[int]]
type Coords = tuple[int, int]


class Allegiance(enum.Enum):
    Player = 0
    Enemy = 1
    Nature = 2
