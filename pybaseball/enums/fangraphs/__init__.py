from typing import Optional, Union

from .batting_stats import FanGraphsBattingStat
from .fielding_stats import FanGraphsFieldingStat
from .league import FanGraphsLeague
from .month import FanGraphsMonth
from .pitching_stats import FanGraphsPitchingStat
from .positions import FanGraphsPositions
from .stat_types import FanGraphsStatTypes

FanGraphsStat = Union[Optional[str], FanGraphsBattingStat, FanGraphsFieldingStat, FanGraphsPitchingStat]
