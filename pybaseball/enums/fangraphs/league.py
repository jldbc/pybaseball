from enum import Enum, unique


@unique
class FangraphsLeague(Enum):
    ALL = 'all'
    AL  = 'al'
    FL  = 'fl'
    NL  = 'nl'
