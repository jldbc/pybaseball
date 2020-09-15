from typing import Union

from .batting_data_enum import FangraphsBattingStats
from .fielding_data_enum import FangraphsFieldingStats
from .league import FangraphsLeague
from .month import FangraphsMonth
from .pitching_data_enum import FangraphsPitchingStats
from .positions import FangraphsPositions
from .fangraphs_stats_category import FangraphsStatsCategory
from.fangraphs_data_enum_base import type_list_to_str

FangraphsDataType = Union[FangraphsBattingStats, FangraphsFieldingStats, FangraphsPitchingStats]
