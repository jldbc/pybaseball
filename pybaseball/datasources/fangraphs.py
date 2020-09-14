from abc import ABC
from enum import Enum, unique
from typing import Callable, Iterable, List, Optional, Type, Union

import lxml
import pandas as pd
import requests

from pybaseball.datahelpers import postprocessing
from pybaseball.datahelpers.column_mapper import BattingStatsColumnMapper, ColumnListMapperFunction, GenericColumnMapper
from pybaseball.datasources.html_table_processor import HTMLTableProcessor
from pybaseball.enums.fangraphs import (FanGraphsBattingStat, FanGraphsFieldingStat, FanGraphsLeague, FanGraphsMonth,
                                        FanGraphsPitchingStat, FanGraphsPositions, FanGraphsStat, FanGraphsStatTypes,
                                        type_list_to_str)

_FG_LEADERS_URL = "/leaders.aspx"

MIN_AGE = 0
MAX_AGE = 100

class FanGraphsDataTable(ABC):
    ROOT_URL: str = "https://www.fangraphs.com"
    TABLE_CLASS: str = "rgMasterTable"
    HEADINGS_XPATH: str = "({TABLE_XPATH}/thead//th[contains(@class, 'rgHeader')])[position()>1]/descendant-or-self::*/text()"
    DATA_ROWS_XPATH: str = "({TABLE_XPATH}/tbody//tr)"
    DATA_CELLS_XPATH: str = "td[position()>1]/descendant-or-self::*/text()"
    QUERY_ENDPOINT: str = _FG_LEADERS_URL
    STATS: FanGraphsStatTypes = FanGraphsStatTypes.NONE
    DEFAULT_TYPES: List[FanGraphsStat] = []
    KNOWN_PERCENTAGES: List[str] = []
    TEAM_DATA: bool = False
    COLUMN_NAME_MAPPER: ColumnListMapperFunction = GenericColumnMapper().map_list

    def __init__(self):
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

    def fetch(self, start_season: int, end_season: Optional[int] = None, types: List[FanGraphsStat] = [],
              league: FanGraphsLeague = FanGraphsLeague.ALL, qual: Optional[int] = None, split_seasons: bool = True,
              month: FanGraphsMonth = FanGraphsMonth.ALL, on_active_roster: bool = False, minimum_age: int = MIN_AGE,
              maximum_age: int = MAX_AGE, team: str = '0', _filter: str = '', players: str = '',
              position: FanGraphsPositions = FanGraphsPositions.ALL, max_results: int = 1000000,) -> pd.DataFrame:

        """
        Get leaderboard data from FanGraphs.

        ARGUMENTS:
        start_season       : int                : First season to return data for
        end_season         : int                : Last season to return data for
                                                  Default = start_season
        types              : str                : The columns of data to return
        league             : FanGraphsLeague    : League to return data for: ALL, AL, FL, NL
                                                  Default = FanGraphsLeague.ALL
        qual               : Optional[int]      : Minimum number of plate appearances to be included.
                                                  If None is specified, the FanGraphs default ('y') is used.
                                                  Default = None
        split_seasons      : bool               : True if you want individual season-level data
                                                  False if you want aggregate data over all seasons.
                                                  Default = False
        month              : FanGraphsMonth     : Month to filter data by. FanGraphsMonth.ALL to not filter by month.
                                                  Default = FanGraphsMonth.ALL
        on_active_roster   : bool               : Only include active roster players.
                                                  Default = False
        minimum_age        : int                : Minimum player age.
                                                  Default = 0
        maximum_age        : int                : Maximum player age.
                                                  Default = 100
        team               : str                : Team to filter data by.
                                                  Specify "0,ts" to get aggregate team data.
        position           : FanGraphsPositions : Position to filter data by.
                                                  Default = FanGraphsPositions.ALL
        max_results        : int                : The maximum number of results to return.
                                                  Default = 1000000 (In effect, all results)
        """

        types = self.DEFAULT_TYPES if not types else types

        if start_season is None:
            raise ValueError(
                "You need to provide at least one season to collect data for. " +
                "Try specifying start_season or start_season and end_season."
            )

        if end_season is None:
            end_season = start_season

        assert self.STATS is not None

        url_options = {
            'pos': position.value,
            'stats': self.STATS.value,
            'lg': league.value,
            'qual': qual if qual is not None else 'y',
            'type': type_list_to_str(types),
            'season': end_season,
            'month': month.value,
            'season1': start_season,
            'ind': int(split_seasons),
            'team': team + ',ts' if self.TEAM_DATA else '',
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
                )
            )
        )

class FanGraphsBattingDataTable(FanGraphsDataTable):
    STATS: FanGraphsStatTypes = FanGraphsStatTypes.BATTING
    DEFAULT_TYPES: List[FanGraphsStat] = FanGraphsBattingStat.ALL()
    COLUMN_NAME_MAPPER: ColumnListMapperFunction = BattingStatsColumnMapper().map_list
    KNOWN_PERCENTAGES: List[str] = ["GB/FB"]

    def _postprocess(self, data: pd.DataFrame) -> pd.DataFrame:
        return self._sort(data, ["WAR", "OPS"], ascending=False)

class FanGraphsPitchingDataTable(FanGraphsDataTable):
    STATS: FanGraphsStatTypes = FanGraphsStatTypes.PITCHING
    DEFAULT_TYPES: List[FanGraphsStat] = FanGraphsPitchingStat.ALL()

    def _postprocess(self, data: pd.DataFrame) -> pd.DataFrame:
        if "WAR" in data.columns:
            new_position = min(7, len(data.columns) - 1)
            columns = data.columns.tolist()
            columns.insert(new_position, columns.pop(columns.index("WAR")))
            data = data.reindex(columns=columns)
        return self._sort(data, ["WAR", "W"], ascending=False)

class FanGraphsTeamBattingDataTable(FanGraphsDataTable):
    STATS: FanGraphsStatTypes = FanGraphsStatTypes.BATTING
    DEFAULT_TYPES: List[FanGraphsStat] = FanGraphsBattingStat.ALL()
    COLUMN_NAME_MAPPER: ColumnListMapperFunction = BattingStatsColumnMapper().map_list
    TEAM_DATA: bool = True

class FanGraphsTeamFieldingDataTable(FanGraphsDataTable):
    STATS: FanGraphsStatTypes = FanGraphsStatTypes.FIELDING
    DEFAULT_TYPES: List[FanGraphsStat] = FanGraphsFieldingStat.ALL()
    TEAM_DATA: bool = True

class FanGraphsTeamPitchingDataTable(FanGraphsDataTable):
    STATS: FanGraphsStatTypes = FanGraphsStatTypes.PITCHING
    DEFAULT_TYPES: List[FanGraphsStat] = FanGraphsPitchingStat.ALL()
    TEAM_DATA: bool = True

fg_batting_data = FanGraphsBattingDataTable().fetch
fg_pitching_data = FanGraphsPitchingDataTable().fetch
fg_team_batting_data = FanGraphsTeamBattingDataTable().fetch
fg_team_fielding_data = FanGraphsTeamFieldingDataTable().fetch
fg_team_pitching_data = FanGraphsTeamPitchingDataTable().fetch
