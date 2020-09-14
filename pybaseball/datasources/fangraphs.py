from abc import ABC
from enum import Enum, unique
from typing import Callable, Iterable, List, Optional, Type, Union

import lxml
import pandas as pd
import requests

from pybaseball.datahelpers import postprocessing
from pybaseball.datahelpers.column_mapper import BattingStatsColumnMapper, GenericColumnMapper, ColumnListMapperFunction
from pybaseball.datasources.html_table_processor import HTMLTableProcessor
from pybaseball.enums.fangraphs import (FanGraphsStat, FanGraphsBattingStat, FanGraphsFieldingStat, FanGraphsLeague, FanGraphsMonth,
                                        FanGraphsPitchingStat, FanGraphsPositions, FanGraphsStatTypes)

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
    DEFAULT_TYPES: FanGraphsStat = None
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

    def _validate(self, data: pd.DataFrame) -> pd.DataFrame:
        return data

    def fetch(self, start_season: int, end_season: Optional[int] = None, types: FanGraphsStat = None,
              league: FanGraphsLeague = FanGraphsLeague.ALL, qual: Optional[int] = None, split_seasons: bool = True,
              month: FanGraphsMonth = FanGraphsMonth.ALL, on_active_roster: bool = False, minimum_age: int = MIN_AGE,
              maximum_age: int = MAX_AGE, team: str = '0', _filter: str = '', players: str = '',
              position: FanGraphsPositions = FanGraphsPositions.ALL, max_results: int = 1000000,) -> pd.DataFrame:

        types = self.DEFAULT_TYPES if types is None else types

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
            'type': types,
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
    DEFAULT_TYPES: FanGraphsStat = FanGraphsBattingStat.ALL()
    COLUMN_NAME_MAPPER: ColumnListMapperFunction = BattingStatsColumnMapper().map_list
    KNOWN_PERCENTAGES: List[str] = ["GB/FB"]

    def _postprocess(self, data: pd.DataFrame) -> pd.DataFrame:
        return data.sort_values(["WAR", "OPS"], ascending=False)

class FanGraphsPitchingDataTable(FanGraphsDataTable):
    STATS: FanGraphsStatTypes = FanGraphsStatTypes.PITCHING
    DEFAULT_TYPES: FanGraphsStat = FanGraphsPitchingStat.ALL()

    def _postprocess(self, data: pd.DataFrame) -> pd.DataFrame:
        columns = data.columns.tolist()
        columns.insert(7, columns.pop(columns.index("WAR")))
        return data.reindex(columns=columns).sort_values(["WAR", "W"], ascending=False)

class FanGraphsTeamBattingDataTable(FanGraphsDataTable):
    STATS: FanGraphsStatTypes = FanGraphsStatTypes.BATTING
    DEFAULT_TYPES: FanGraphsStat = FanGraphsBattingStat.ALL()
    COLUMN_NAME_MAPPER: ColumnListMapperFunction = BattingStatsColumnMapper().map_list
    TEAM_DATA: bool = True

class FanGraphsTeamFieldingDataTable(FanGraphsDataTable):
    STATS: FanGraphsStatTypes = FanGraphsStatTypes.FIELDING
    DEFAULT_TYPES: FanGraphsStat = FanGraphsFieldingStat.ALL()
    TEAM_DATA: bool = True

class FanGraphsTeamPitchingDataTable(FanGraphsDataTable):
    STATS: FanGraphsStatTypes = FanGraphsStatTypes.PITCHING
    DEFAULT_TYPES: FanGraphsStat = FanGraphsPitchingStat.ALL()
    TEAM_DATA: bool = True

fg_batting_data = FanGraphsBattingDataTable().fetch
fg_pitching_data = FanGraphsPitchingDataTable().fetch
fg_team_batting_data = FanGraphsTeamBattingDataTable().fetch
fg_team_fielding_data = FanGraphsTeamFieldingDataTable().fetch
fg_team_pitching_data = FanGraphsTeamPitchingDataTable().fetch
