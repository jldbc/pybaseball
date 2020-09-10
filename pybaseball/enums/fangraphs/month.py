from enum import Enum, unique


@unique
class FanGraphsMonth(Enum):
    ALL               = 0
    MARCH_APRIL       = 4
    MAY               = 5
    JUNE              = 6
    JULY              = 7
    AUGUST            = 8
    SEPTEMBER_OCTOBER = 9
