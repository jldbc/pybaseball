from enum import Enum, unique
from typing import Callable, List, Optional, Union

import lxml
import pandas as pd
import requests

from pybaseball.datahelpers import postprocessing
from pybaseball.datasources.html_table import HTMLTable
from pybaseball.enums.fangraphs import (
    FanGraphsBattingStat, FanGraphsFieldingStat, FanGraphsLeague,
    FanGraphsMonth, FanGraphsPitchingStat, FanGraphsPositions,
    FanGraphsStatTypes)

_ROOT_URL = 'https://www.fangraphs.com'
_TABLE_XPATH = '//table[@class="rgMasterTable"]'
_HEADINGS_XPATH = f"({_TABLE_XPATH}/thead//th[contains(@class, 'rgHeader')])[position()>1]/descendant-or-self::*/text()"
_DATA_ROWS_XPATH = f"({_TABLE_XPATH}/tbody//tr)"
_DATA_CELLS_XPATH = 'td[position()>1]/descendant-or-self::*/text()'

_FG_LEADERS_URL = "/leaders.aspx"

MIN_AGE = 0
MAX_AGE = 100


class FanGraphs(HTMLTable):
    def __init__(self):
        super().__init__(
            root_url=_ROOT_URL,
            headings_xpath=_HEADINGS_XPATH,
            data_rows_xpath=_DATA_ROWS_XPATH,
            data_cell_xpath=_DATA_CELLS_XPATH
        )

    def _leaders(self, start_season: int, stats: FanGraphsStatTypes, types: str, end_season: int = None,
                 league: FanGraphsLeague = FanGraphsLeague.ALL, qual: Optional[int] = None, split_seasons: bool = True,
                 month: FanGraphsMonth = FanGraphsMonth.ALL, on_active_roster: bool = False,
                 minimum_age: int = MIN_AGE, maximum_age: int = MAX_AGE, team: str = '', _filter: str = '',
                 players: str = '', position: FanGraphsPositions = FanGraphsPositions.ALL,
                 max_results: int = 1000000, column_name_mapper: Callable = None,
                 known_percentages: List[str] = []) -> pd.DataFrame:
        """
        Get leaderboard data from FanGraphs.

        ARGUMENTS:
        start_season       : int                : First season to return data for
        stats              : FanGraphsStatTypes : The type of data to return (BATTING, FIELDING, PITCHING)
        types              : str                : The columns of data to return
        end_season         : int                : Last season to return data for
                                                  Default = start_season
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
        position           : FanGraphsPositions : Position to filter data by.
                                                  Default = FanGraphsPositions.ALL
        max_results        : int                : The maximum number of results to return.
                                                  Default = 1000000 (In effect, all results)
        column_name_mapper : Callable           : A function to pass to get_tabular_data_from_url to map column names.
                                                  Default = None
        known_percentages  : List[str]          : A list of columns that are known to be percentages that the default
                                                  percentage discovery mechanism may miss.
                                                  Default = []
        """
        if start_season is None:
            raise ValueError(
                "You need to provide at least one season to collect data for. " +
                "Try specifying start_season or start_season and end_season."
            )
        if end_season is None:
            end_season = start_season

        leaders_url = self._create_url(_FG_LEADERS_URL,
            {
                'pos': position.value,
                'stats': stats.value,
                'lg': league.value,
                'qual': qual if qual is not None else 'y',
                'type': types,
                'season': end_season,
                'month': month.value,
                'season1': start_season,
                'ind': '1' if split_seasons else '0',
                'team': team,
                'rost': '1' if on_active_roster else '0',
                'age': f"{minimum_age},{maximum_age}",
                'filter': _filter,
                'players': players,
                'page': f'1_{max_results}'
            }
        )

        return self.get_tabular_data_from_url(
            leaders_url,
            column_name_mapper=column_name_mapper,
            known_percentages=known_percentages
        )        

    def batting_stats(self, start_season: int, end_season: int = None, league: FanGraphsLeague = FanGraphsLeague.ALL,
                      qual: Optional[int] = None, split_seasons: bool = True,
                      month: FanGraphsMonth = FanGraphsMonth.ALL, on_active_roster: bool = False,
                      minimum_age: int = MIN_AGE, maximum_age: int = MAX_AGE,
                      position: FanGraphsPositions = FanGraphsPositions.ALL) -> pd.DataFrame:
        """
        Get season-level batting data from FanGraphs.

        ARGUMENTS:
        start_season     : int                : First season to return data for
        end_season       : int                : Last season to return data for
                                                Default = start_season
        league           : FanGraphsLeague    : League to return data for: ALL, AL, FL, NL
                                                Default = FanGraphsLeague.ALL
        qual             : Optional[int]      : Minimum number of plate appearances to be included.
                                                If None is specified, the FanGraphs default ('y') is used.
                                                Default = None
        split_seasons    : bool               : True if you want individual season-level data
                                                False if you want aggregate data over all seasons.
                                                Default = False
        month            : FanGraphsMonth     : Month to filter data by. FanGraphsMonth.ALL to not filter by month.
                                                Default = FanGraphsMonth.ALL
        on_active_roster : bool               : Only include active roster players.
                                                Default = False
        minimum_age      : int                : Minimum player age.
                                                Default = 0
        maximum_age      : int                : Maximum player age.
                                                Default = 100
        position         : FanGraphsPositions : Position to filter data by.
                                                Default = FanGraphsPositions.ALL
        """

        fg_data = self._leaders(
            start_season,
            stats=FanGraphsStatTypes.BATTING,
            types=FanGraphsBattingStat.ALL(),
            end_season=end_season,
            league=league,
            qual=qual,
            split_seasons=split_seasons,
            month=month,
            on_active_roster=on_active_roster,
            minimum_age=minimum_age,
            maximum_age=maximum_age,
            position=position,
            column_name_mapper=BattingStatsColumnMapper().map,
            known_percentages = ['GB/FB'],
        )

        return fg_data.sort_values(['WAR', 'OPS'], ascending=False)

    def pitching_stats(self, start_season: int, end_season: int = None, league: FanGraphsLeague = FanGraphsLeague.ALL,
                      qual: Optional[int] = None, split_seasons: bool = True,
                      month: FanGraphsMonth = FanGraphsMonth.ALL, on_active_roster: bool = False,
                      minimum_age: int = MIN_AGE, maximum_age: int = MAX_AGE) -> pd.DataFrame:
        """
        Get season-level pitching data from FanGraphs.

        ARGUMENTS:
        start_season     : int                : First season to return data for
        end_season       : int                : Last season to return data for
                                                Default = start_season
        league           : FanGraphsLeague    : League to return data for: ALL, AL, FL, NL
                                                Default = FanGraphsLeague.ALL
        qual             : Optional[int]      : Minimum number of plate appearances to be included.
                                                If None is specified, the FanGraphs default ('y') is used.
                                                Default = None
        split_seasons    : bool               : True if you want individual season-level data
                                                False if you want aggregate data over all seasons.
                                                Default = False
        month            : FanGraphsMonth     : Month to filter data by. FanGraphsMonth.ALL to not filter by month.
                                                Default = FanGraphsMonth.ALL
        on_active_roster : bool               : Only include active roster players.
                                                Default = False
        minimum_age      : int                : Minimum player age.
                                                Default = 0
        maximum_age      : int                : Maximum player age.
                                                Default = 100
        """

        data = self._leaders(
            start_season,
            stats=FanGraphsStatTypes.PITCHING,
            types=FanGraphsPitchingStat.ALL(),
            end_season=end_season,
            league=league,
            qual=qual,
            split_seasons=split_seasons,
            month=month,
            on_active_roster=on_active_roster,
            minimum_age=minimum_age,
            maximum_age=maximum_age,
            column_name_mapper=GenericColumnMapper().map
        )

        # Sort by WAR and wins so best players float to the top
        data = data.sort_values(['WAR', 'W'], ascending=False)

        # Put WAR at the end because it looks better
        cols = data.columns.tolist()
        cols.insert(7, cols.pop(cols.index('WAR')))
        data = data.reindex(columns=cols)

        return data

    def team_batting(self, start_season: int, end_season: int = None, league: FanGraphsLeague = FanGraphsLeague.ALL,
                      qual: Optional[int] = None, split_seasons: bool = True,
                      month: FanGraphsMonth = FanGraphsMonth.ALL, on_active_roster: bool = False,
                      minimum_age: int = MIN_AGE, maximum_age: int = MAX_AGE,
                      position: FanGraphsPositions = FanGraphsPositions.ALL) -> pd.DataFrame:
        """
        Get season-level batting data aggregated by team.

        ARGUMENTS:
        start_season     : int                : First season to return data for
        end_season       : int                : Last season to return data for
                                                Default = start_season
        league           : FanGraphsLeague    : League to return data for: ALL, AL, FL, NL
                                                Default = FanGraphsLeague.ALL
        qual             : Optional[int]      : Minimum number of plate appearances to be included.
                                                If None is specified, the FanGraphs default ('y') is used.
                                                Default = None
        split_seasons    : bool               : True if you want individual season-level data
                                                False if you want aggregate data over all seasons.
                                                Default = False
        month            : FanGraphsMonth     : Month to filter data by. FanGraphsMonth.ALL to not filter by month.
                                                Default = FanGraphsMonth.ALL
        on_active_roster : bool               : Only include active roster players.
                                                Default = False
        minimum_age      : int                : Minimum player age.
                                                Default = 0
        maximum_age      : int                : Maximum player age.
                                                Default = 100
        position         : FanGraphsPositions : Position to filter data by.
                                                Default = FanGraphsPositions.ALL
        """
        data = self._leaders(
            start_season,
            stats=FanGraphsStatTypes.BATTING,
            types=FanGraphsBattingStat.ALL(),
            end_season=end_season,
            league=league,
            qual=qual,
            split_seasons=split_seasons,
            month=month,
            on_active_roster=on_active_roster,
            minimum_age=minimum_age,
            maximum_age=maximum_age,
            position=position,
            team='0,ts',
            players='0',
            column_name_mapper=GenericColumnMapper().map
        )

        return data

    def team_fielding(self, start_season: int, end_season: int = None, league: FanGraphsLeague = FanGraphsLeague.ALL,
                      qual: Optional[int] = None, split_seasons: bool = True,
                      month: FanGraphsMonth = FanGraphsMonth.ALL, on_active_roster: bool = False,
                      minimum_age: int = MIN_AGE, maximum_age: int = MAX_AGE,
                      position: FanGraphsPositions = FanGraphsPositions.ALL) -> pd.DataFrame:
        """
        Get season-level fielding data aggregated by team.

        ARGUMENTS:
        start_season     : int                : First season to return data for
        end_season       : int                : Last season to return data for
                                                Default = start_season
        league           : FanGraphsLeague    : League to return data for: ALL, AL, FL, NL
                                                Default = FanGraphsLeague.ALL
        qual             : Optional[int]      : Minimum number of plate appearances to be included.
                                                If None is specified, the FanGraphs default ('y') is used.
                                                Default = None
        split_seasons    : bool               : True if you want individual season-level data
                                                False if you want aggregate data over all seasons.
                                                Default = False
        month            : FanGraphsMonth     : Month to filter data by. FanGraphsMonth.ALL to not filter by month.
                                                Default = FanGraphsMonth.ALL
        on_active_roster : bool               : Only include active roster players.
                                                Default = False
        minimum_age      : int                : Minimum player age.
                                                Default = 0
        maximum_age      : int                : Maximum player age.
                                                Default = 100
        position         : FanGraphsPositions : Position to filter data by.
                                                Default = FanGraphsPositions.ALL
        """

        data = self._leaders(
            start_season,
            stats=FanGraphsStatTypes.FIELDING,
            types=FanGraphsFieldingStat.ALL(),
            end_season=end_season,
            league=league,
            qual=qual,
            split_seasons=split_seasons,
            month=month,
            on_active_roster=on_active_roster,
            minimum_age=minimum_age,
            maximum_age=maximum_age,
            position=position,
            team='0,ts',
            players='0',
            column_name_mapper=GenericColumnMapper().map
        )

        return data

    def team_pitching(self, start_season: int, end_season: int = None, league: FanGraphsLeague = FanGraphsLeague.ALL,
                      qual: Optional[int] = None, split_seasons: bool = True,
                      month: FanGraphsMonth = FanGraphsMonth.ALL, on_active_roster: bool = False,
                      minimum_age: int = MIN_AGE, maximum_age: int = MAX_AGE) -> pd.DataFrame:
        """
        Get season-level pitching data aggregated by team.

        ARGUMENTS:
        start_season     : int                : First season to return data for
        end_season       : int                : Last season to return data for
                                                Default = start_season
        league           : FanGraphsLeague    : League to return data for: ALL, AL, FL, NL
                                                Default = FanGraphsLeague.ALL
        qual             : Optional[int]      : Minimum number of plate appearances to be included.
                                                If None is specified, the FanGraphs default ('y') is used.
                                                Default = None
        split_seasons    : bool               : True if you want individual season-level data
                                                False if you want aggregate data over all seasons.
                                                Default = False
        month            : FanGraphsMonth     : Month to filter data by. FanGraphsMonth.ALL to not filter by month.
                                                Default = FanGraphsMonth.ALL
        on_active_roster : bool               : Only include active roster players.
                                                Default = False
        minimum_age      : int                : Minimum player age.
                                                Default = 0
        maximum_age      : int                : Maximum player age.
                                                Default = 100
        """
        
        data = self._leaders(
            start_season,
            stats=FanGraphsStatTypes.PITCHING,
            types=FanGraphsPitchingStat.ALL(),
            end_season=end_season,
            league=league,
            qual=qual,
            split_seasons=split_seasons,
            month=month,
            team='0,ts',
            players='0',
            on_active_roster=on_active_roster,
            minimum_age=minimum_age,
            maximum_age=maximum_age,
            column_name_mapper=GenericColumnMapper().map
        )

        return data


class GenericColumnMapper:
    def __init__(self):
        self.call_counts = {}

    def map(self, column_name: str) -> str:
        self.call_counts[column_name] = self.call_counts.get(column_name, 0) + 1
        # First time around use the actual column name
        if self.call_counts[column_name] == 1:
            return column_name

        # Just tack on a number for other calls
        return column_name + " " + str(self.call_counts[column_name])


class BattingStatsColumnMapper:
    def __init__(self):
        self.call_counts = {}

    def map(self, column_name: str) -> str:
        self.call_counts[column_name] = self.call_counts.get(column_name, 0) + 1
        # First time around use the actual column name
        if self.call_counts[column_name] == 1:
            return column_name

        # Rename the second FB% column
        if column_name == 'FB%' and self.call_counts[column_name] == 2:
            return 'FB% (Pitch)'

        # Just tack on a number for other calls
        return column_name + " " + str(self.call_counts[column_name])
