from enum import unique

from ..enum_base import EnumBase


@unique
class FangraphsPositions(EnumBase):
    ALL               = 'all'
    PITCHER           = 'p'
    CATCHER           = 'c'
    FIRST_BASE        = '1b'
    SECOND_BASE       = '2b'
    SHORT_STOP        = 'ss'
    THIRD_BASE        = '3b'
    RIGHT_FIELD       = 'rf'
    CENTER_FIELD      = 'cf'
    LEFT_FIELD        = 'lf'
    OUT_FIELD         = 'of'
    DESIGNATED_HITTER = 'dh'
    NO_POSITION       = 'np'
