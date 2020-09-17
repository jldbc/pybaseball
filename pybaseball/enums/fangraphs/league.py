from enum import unique

from ..enum_base import EnumBase


@unique
class FangraphsLeague(EnumBase):
    ALL = 'all'
    AL  = 'al'
    FL  = 'fl'
    NL  = 'nl'
