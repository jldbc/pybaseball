from enum import Enum, unique


@unique
class FanGraphsStat(Enum):
    NONE     = None
    BATTING  = 'bat'
    FIELDING = 'fld'
    PITCHING = 'pit'
