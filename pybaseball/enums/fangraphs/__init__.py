from typing import Dict, List, Type, Union

from .batting_data_enum import FangraphsBattingStats
from .fangraphs_stats_category import FangraphsStatsCategory
from .fielding_data_enum import FangraphsFieldingStats
from .league import FangraphsLeague
from .month import FangraphsMonth
from .pitching_data_enum import FangraphsPitchingStats
from .positions import FangraphsPositions

from. fangraphs_stats_base import stat_list_to_str

FangraphsStatColumn = Union[FangraphsBattingStats, FangraphsFieldingStats, FangraphsPitchingStats]

_category_enum_map: Dict[FangraphsStatsCategory, Type[FangraphsStatColumn]] = {
    FangraphsStatsCategory.BATTING: FangraphsBattingStats,
    FangraphsStatsCategory.FIELDING: FangraphsFieldingStats,
    FangraphsStatsCategory.PITCHING: FangraphsPitchingStats,
}

def stat_list_from_str(stat_category: FangraphsStatsCategory, values: Union[str, List[str]]) -> List:
    if not values:
        return []

    if isinstance(values, str):
        values = [values]

    obj_type = _category_enum_map[stat_category]

    if 'ALL' in values:
        return obj_type.ALL()

    for value in values:
        if value not in obj_type.__members__.keys(): # type: ignore
            raise ValueError(f"Invalid stat column of {value} was used. Stat columns must be a valid member of the enum: {obj_type.__name__}")

    stat_list = [obj_type[x] for x in values]
    
    return stat_list
