from enum import Enum, unique


@unique
class FanGraphsStatsCategory(Enum):
    NONE     = None
    BATTING  = 'bat'
    FIELDING = 'fld'
    PITCHING = 'pit'
