from enum import unique

from ..enum_base import EnumBase


@unique
class FangraphsLeague(EnumBase):
    ALL = 'all'
    AL  = 'al'
    FL  = 'fl'
    NL  = 'nl'
    MNL = 'mnl' # All Negro Leagues
    NNL = 'nnl' # Negro National League I
    ECL = 'ecl' # Eastern Colored League
    ANL = 'anl' # American Negro League
    EWL = 'ewl' # East-West League
    NSL = 'nsl' # Negro Southern League
    NN2 = 'nn2' # Negro National League II
    NAL = "nal" # Negro American League