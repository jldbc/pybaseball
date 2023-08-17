from abc import ABC
from typing import Any, List, Optional, Union

import lxml
import pandas as pd

from .. import cache
from ..datahelpers.column_mapper import BattingStatsColumnMapper, ColumnListMapperFunction, GenericColumnMapper
from ..enums.fangraphs import (FangraphsBattingStats, FangraphsFieldingStats, FangraphsLeague, FangraphsMonth,
                               FangraphsPitchingStats, FangraphsPositions, FangraphsStatColumn, FangraphsStatsCategory,
                               stat_list_from_str, stat_list_to_str)
from .html_table_processor import HTMLTableProcessor, RowIdFunction

_FG_LEADERS_URL = "/leaders-legacy.aspx"

MIN_AGE = 0
MAX_AGE = 100

def extract_id_from_row(fg_row: lxml.etree.Element, param_name: str) -> Optional[int]:
    try:
        anchor_tags = fg_row.xpath('td//a')
        for anchor_tag in anchor_tags:
            href = anchor_tag.get('href')
            if href and '?' in href:
                qs_params = href.split('?')[1].split('&')
                values = [qs_param.split('=')[1] for qs_param in qs_params if qs_param.split('=')[0].lower() == param_name]
                if values:
                    return int(values[0])
    except:
        pass
    return None

def team_row_id_func(self: Any, fg_row: lxml.etree.Element) -> Optional[int]:
    return extract_id_from_row(fg_row, 'team')

def player_row_id_func(self: Any, fg_row: lxml.etree.Element) -> Optional[int]:
    return extract_id_from_row(fg_row, 'playerid')

class FangraphsDataTable(ABC):
    ROOT_URL: str = "https://www.fangraphs.com"
    TABLE_CLASS: str = "rgMasterTable"
    HEADINGS_XPATH: str = "({TABLE_XPATH}/thead//th[contains(@class, 'rgHeader')])[position()>1]/descendant-or-self::*/text()"
    DATA_ROWS_XPATH: str = "({TABLE_XPATH}/tbody//tr)"
    DATA_CELLS_XPATH: str = "td[position()>1]/descendant-or-self::*/text()"
    QUERY_ENDPOINT: str = _FG_LEADERS_URL
    STATS_CATEGORY: FangraphsStatsCategory = FangraphsStatsCategory.NONE
    DEFAULT_STAT_COLUMNS: List[FangraphsStatColumn] = []
    KNOWN_PERCENTAGES: List[str] = []
    ROW_ID_FUNC: RowIdFunction = None
    ROW_ID_NAME: Optional[str] = None
    TEAM_DATA: bool = False
    COLUMN_NAME_MAPPER: ColumnListMapperFunction = GenericColumnMapper().map_list

    def __init__(self) -> None:
        self.html_accessor = HTMLTableProcessor(
            root_url=self.ROOT_URL,
            headings_xpath=self.HEADINGS_XPATH,
            data_cell_xpath=self.DATA_CELLS_XPATH,
            data_rows_xpath=self.DATA_ROWS_XPATH,
            table_class=self.TABLE_CLASS,
        )

    def _postprocess(self, data: pd.DataFrame) -> pd.DataFrame:
        return data

    def _sort(self, data: pd.DataFrame, columns: List[str], ascending: bool = True) -> pd.DataFrame:
        known_columns = [x for x in columns if x in data.columns]
        if known_columns == []:
            return data

        return data.sort_values(columns, ascending=ascending)

    def _validate(self, data: pd.DataFrame) -> pd.DataFrame:
        return data

    def fetch(self, start_season: int, end_season: Optional[int] = None, league: str = 'ALL', ind: int = 1,
              stat_columns: Union[str, List[str]] = 'ALL', qual: Optional[int] = None, split_seasons: bool = True,
              month: str = 'ALL', on_active_roster: bool = False, minimum_age: int = MIN_AGE,
              maximum_age: int = MAX_AGE, team: str = '', _filter: str = '', players: str = '',
              position: str = 'ALL', max_results: int = 1000000,) -> pd.DataFrame:

        """
        Get leaderboard data from Fangraphs.

        ARGUMENTS:
        start_season       : int              : First season to return data for
        end_season         : int              : Last season to return data for
                                                Default = start_season
        league             : str              : League to return data for: ALL, AL, FL, NL
                                                Default = ALL
        ind                : int              : DEPRECATED. ONLY FOR BACKWARDS COMPATIBILITY. USE split_seasons INSTEAD
                                                1 if you want individual season-level data
                                                0 if you want a player's aggreagate data over all seasons in the query
        stat_columns       : str or List[str] : The columns of data to return
                                                Default = ALL
        qual               : Optional[int]    : Minimum number of plate appearances to be included.
                                                If None is specified, the Fangraphs default ('y') is used.
                                                Default = None
        split_seasons      : bool             : True if you want individual season-level data
                                                False if you want aggregate data over all seasons.
                                                Default = False
        month              : str              : Month to filter data by. 'ALL' to not filter by month.
                                                Default = 'ALL'
        on_active_roster   : bool             : Only include active roster players.
                                                Default = False
        minimum_age        : int              : Minimum player age.
                                                Default = 0
        maximum_age        : int              : Maximum player age.
                                                Default = 100
        team               : str              : Team to filter data by.
                                                Specify "0,ts" to get aggregate team data.
        position           : str              : Position to filter data by.
                                                Default = ALL
        max_results        : int              : The maximum number of results to return.
                                                Default = 1000000 (In effect, all results)
        """

        stat_columns_enums = stat_list_from_str(self.STATS_CATEGORY, stat_columns)

        if start_season is None:
            raise ValueError(
                "You need to provide at least one season to collect data for. " +
                "Try specifying start_season or start_season and end_season."
            )

        if end_season is None:
            end_season = start_season

        assert self.STATS_CATEGORY is not None

        if league is None:
            raise ValueError("parameter 'league' cannot be None.")

        url_options = {
            'pos': FangraphsPositions.parse(position).value,
            'stats': self.STATS_CATEGORY.value,
            'lg': FangraphsLeague.parse(league.upper()).value,
            'qual': qual if qual is not None else 'y',
            'type': stat_list_to_str(stat_columns_enums),
            'season': end_season,
            'month': FangraphsMonth.parse(month).value,
            'season1': start_season,
            'ind': ind if ind == 0 and split_seasons else int(split_seasons),
            'team':  f'{team or 0},ts' if self.TEAM_DATA else team,
            'rost': int(on_active_roster),
            'age': f"{minimum_age},{maximum_age}",
            'filter': _filter,
            'players': players,
            'page': f'1_{max_results}'
        }

        return self._validate(
            self._postprocess(
                self.html_accessor.get_tabular_data_from_options(
                    self.QUERY_ENDPOINT,
                    query_params=url_options,
                    # TODO: Remove the type: ignore after this is fixed: https://github.com/python/mypy/issues/5485
                    column_name_mapper=self.COLUMN_NAME_MAPPER, # type: ignore
                    known_percentages=self.KNOWN_PERCENTAGES,
                    row_id_func=self.ROW_ID_FUNC,
                    row_id_name=self.ROW_ID_NAME,
                )
            )
        )

class FangraphsBattingStatsTable(FangraphsDataTable):
    STATS_CATEGORY: FangraphsStatsCategory = FangraphsStatsCategory.BATTING
    DEFAULT_STAT_COLUMNS: List[FangraphsStatColumn] = FangraphsBattingStats.ALL()
    COLUMN_NAME_MAPPER: ColumnListMapperFunction = BattingStatsColumnMapper().map_list
    KNOWN_PERCENTAGES: List[str] = ["GB/FB"]
    ROW_ID_FUNC: RowIdFunction = player_row_id_func
    ROW_ID_NAME = 'IDfg'

    @cache.df_cache()
    def fetch(self, *args, **kwargs):
        return super().fetch(*args, **kwargs)

    def _postprocess(self, data: pd.DataFrame) -> pd.DataFrame:
        return self._sort(data, ["WAR", "OPS"], ascending=False)

class FangraphsFieldingStatsTable(FangraphsDataTable):
    STATS_CATEGORY: FangraphsStatsCategory = FangraphsStatsCategory.FIELDING
    DEFAULT_STAT_COLUMNS: List[FangraphsStatColumn] = FangraphsFieldingStats.ALL()
    # KNOWN_PERCENTAGES: List[str] = ["GB/FB"]
    ROW_ID_FUNC: RowIdFunction = player_row_id_func
    ROW_ID_NAME = 'IDfg'

    @cache.df_cache()
    def fetch(self, *args, **kwargs):
        return super().fetch(*args, **kwargs)

    def _postprocess(self, data: pd.DataFrame) -> pd.DataFrame:
        return self._sort(data, ["DEF"], ascending=False)

class FangraphsPitchingStatsTable(FangraphsDataTable):
    STATS_CATEGORY: FangraphsStatsCategory = FangraphsStatsCategory.PITCHING
    DEFAULT_STAT_COLUMNS: List[FangraphsStatColumn] = FangraphsPitchingStats.ALL()
    ROW_ID_FUNC: RowIdFunction = player_row_id_func
    ROW_ID_NAME = 'IDfg'

    @cache.df_cache()
    def fetch(self, *args, **kwargs):
        return super().fetch(*args, **kwargs)

    def _postprocess(self, data: pd.DataFrame) -> pd.DataFrame:
        if "WAR" in data.columns:
            new_position = min(7, len(data.columns) - 1)
            columns = data.columns.tolist()
            columns.insert(new_position, columns.pop(columns.index("WAR")))
            data = data.reindex(columns=columns)
        return self._sort(data, ["WAR", "W"], ascending=False)

class FangraphsTeamBattingDataTable(FangraphsDataTable):
    STATS_CATEGORY: FangraphsStatsCategory = FangraphsStatsCategory.BATTING
    DEFAULT_STAT_COLUMNS: List[FangraphsStatColumn] = FangraphsBattingStats.ALL()
    COLUMN_NAME_MAPPER: ColumnListMapperFunction = BattingStatsColumnMapper().map_list
    TEAM_DATA: bool = True
    ROW_ID_FUNC: RowIdFunction = team_row_id_func
    ROW_ID_NAME = 'teamIDfg'

class FangraphsTeamFieldingDataTable(FangraphsDataTable):
    STATS_CATEGORY: FangraphsStatsCategory = FangraphsStatsCategory.FIELDING
    DEFAULT_STAT_COLUMNS: List[FangraphsStatColumn] = FangraphsFieldingStats.ALL()
    TEAM_DATA: bool = True
    ROW_ID_FUNC: RowIdFunction = team_row_id_func
    ROW_ID_NAME = 'teamIDfg'

class FangraphsTeamPitchingDataTable(FangraphsDataTable):
    STATS_CATEGORY: FangraphsStatsCategory = FangraphsStatsCategory.PITCHING
    DEFAULT_STAT_COLUMNS: List[FangraphsStatColumn] = FangraphsPitchingStats.ALL()
    TEAM_DATA: bool = True
    ROW_ID_FUNC: RowIdFunction = team_row_id_func
    ROW_ID_NAME = 'teamIDfg'

fg_batting_data = FangraphsBattingStatsTable().fetch
fg_fielding_data = FangraphsFieldingStatsTable().fetch
fg_pitching_data = FangraphsPitchingStatsTable().fetch
fg_team_batting_data = FangraphsTeamBattingDataTable().fetch
fg_team_fielding_data = FangraphsTeamFieldingDataTable().fetch
fg_team_pitching_data = FangraphsTeamPitchingDataTable().fetch
