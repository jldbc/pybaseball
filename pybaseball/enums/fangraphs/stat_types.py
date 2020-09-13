from enum import Enum, unique


@unique
class FanGraphsStatTypes(Enum):
    NONE     = None
    BATTING  = 'bat'
    FIELDING = 'fld'
    PITCHING = 'pit'
