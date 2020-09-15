from enum import Enum, unique


@unique
class FangraphsStatsCategory(Enum):
    NONE     = None
    BATTING  = 'bat'
    FIELDING = 'fld'
    PITCHING = 'pit'
