from typing import Union

from .batting_data_enum import FanGraphsBattingData
from .fielding_data_enum import FanGraphsFieldingData
from .league import FanGraphsLeague
from .month import FanGraphsMonth
from .pitching_data_enum import FanGraphsPitchingData
from .positions import FanGraphsPositions
from .fangraphs_stats_category import FanGraphsStatsCategory
from.fangraphs_data_enum_base import type_list_to_str

FanGraphsDataType = Union[FanGraphsBattingData, FanGraphsFieldingData, FanGraphsPitchingData]
