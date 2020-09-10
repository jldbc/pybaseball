from enum import Enum, unique


@unique
class FanGraphsStatTypes(Enum):
    BATTING  = 'bat'
    FIELDING = 'fld'
    PITCHING = 'pit'
