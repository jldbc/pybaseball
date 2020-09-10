from enum import Enum, unique


@unique
class FanGraphsLeague(Enum):
    ALL = 'all'
    AL  = 'al'
    FL  = 'fl'
    NL  = 'nl'
