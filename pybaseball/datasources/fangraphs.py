from typing import Callable, List, Union

import lxml
import pandas as pd
import requests

from pybaseball.datahelpers import postprocessing
from pybaseball.datasources.html_table import HTMLTable

_ROOT_URL = 'https://www.fangraphs.com'
_TABLE_XPATH = '//table[@class="rgMasterTable"]'
_HEADINGS_XPATH = f"({_TABLE_XPATH}/thead//th[contains(@class, 'rgHeader')])[position()>1]/descendant-or-self::*/text()"
_DATA_ROWS_XPATH = f"({_TABLE_XPATH}/tbody//tr)"
_DATA_CELLS_XPATH = 'td[position()>1]/descendant-or-self::*/text()'

# TODO: update url to include more stats
_FG_BATTING_LEADERS_TYPES = "c,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120,121,122,123,124,125,126,127,128,129,130,131,132,133,134,135,136,137,138,139,140,141,142,143,144,145,146,147,148,149,150,151,152,153,154,155,156,157,158,159,160,161,162,163,164,165,166,167,168,169,170,171,172,173,174,175,176,177,178,179,180,181,182,183,184,185,186,187,188,189,190,191,192,193,194,195,196,197,198,199,200,201,202,203,204,205,206,207,208,209,210,211,212,213,214,215,216,217,218,219,220,221,222,223,224,225,226,227,228,229,230,231,232,233,234,235,236,237,238,239,240,241,242,243,244,245,246,247,248,249,250,251,252,253,254,255,256,257,258,259,260,261,262,263,264,265,266,267,268,269,270,271,272,273,274,275,276,277,278,279,280,281,282,283,284,285,286,-1"
_FG_BATTING_LEADERS_URL = "/leaders.aspx?pos=all&stats=bat&lg={league}&qual={qual}&type={types}&season={end_season}&month=0&season1={start_season}&ind={ind}&team=&rost=&age=&filter=&players=&page=1_100000"

_FG_PITCHING_LEADERS_TYPES = "c,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120,121,122,123,124,125,126,127,128,129,130,131,132,133,134,135,136,137,138,139,140,141,142,143,144,145,146,147,148,149,150,151,152,153,154,155,156,157,158,159,160,161,162,163,164,165,166,167,168,169,170,171,172,173,174,175,176,177,178,179,180,181,182,183,184,185,186,187,188,189,190,191,192,193,194,195,196,197,198,199,200,201,202,203,204,205,206,207,208,209,210,211,212,213,214,215,216,217,218,219,220,221,222,223,224,225,226,227,228,229,230,231,232,233,234,235,236,237,238,239,240,241,242,243,244,245,246,247,248,249,250,251,252,253,254,255,256,257,258,259,260,261,262,263,264,265,266,267,268,269,270,271,272,273,274,275,276,277,278,279,280,281,282,283,284,285,286,287,288,289,290,291,292,293,294,295,296,297,298,299,-1"
_FG_PITCHING_LEADERS_URL = "/leaders.aspx?pos=all&stats=pit&lg={league}&qual={qual}&type={types}&season={end_season}&month=0&season1={start_season}&ind={ind}&team=&rost=&age=&filter=&players=&page=1_100000"

_FG_TEAM_BATTING_URL = "/leaders.aspx?pos=all&stats=bat&lg={league}&qual=0&type=8&season={end_season}&month=0&season1={start_season}&ind={ind}&team=0,ts&rost=0&age=0&filter=&players=0&page=1_100000"

_FG_TEAM_FIELDING_URL = "/leaders.aspx?pos=all&stats=fld&lg={league}&qual=0&type=1&season={end_season}&month=0&season1={start_season}&ind={ind}&team=0,ts&rost=0&age=0&filter=&players=0&startdate=&enddate=&page=1_100000"

_FG_TEAM_PITCHING_TYPES = "c,4,5,11,7,8,13,-1,24,36,37,40,43,44,48,51,-1,6,45,62,-1,59"
_FG_TEAM_PITCHING_URL = "/leaders.aspx?pos=all&stats=pit&lg={league}&qual=0&type={types}&season={end_season}&month=0&season1={start_season}&ind={ind}&team=0,ts&rost=0&age=0&filter=&players=0&page=1_100000"


class FanGraphs(HTMLTable):
    def __init__(self):
        super().__init__(
            root_url=_ROOT_URL,
            headings_xpath=_HEADINGS_XPATH,
            data_rows_xpath=_DATA_ROWS_XPATH,
            data_cell_xpath=_DATA_CELLS_XPATH
        )

    
    def batting_stats(self, start_season: int, end_season: int = None, league: str = 'all', qual: int = 1,
                      ind: int = 1) -> pd.DataFrame:
        """
        Get season-level batting data from FanGraphs.

        ARGUMENTS:
        start_season : int      : first season you want data for
                                  (or the only season if you do not specify an end_season)
        end_season   : int      : final season you want data for
        league       : str      : "all", "nl", or "al"
        qual         : int, str : minimum number of plate appearances to be included in the data (integer).
                                  Use the string 'y' for fangraphs default.
        ind          : int      : 1 if you want individual season-level data
                                  0 if you want a player's aggreagate data over all seasons in the query
        """
        if start_season is None:
            raise ValueError(
                "You need to provide at least one season to collect data for. " +
                "Try batting_leaders(season) or batting_leaders(start_season, end_season)."
            )
        if end_season is None:
            end_season = start_season

        column_mapper = BattingStatsColumnMapper()

        fg_data = self.get_tabular_data_from_url(
            _FG_BATTING_LEADERS_URL.format(
                league=league,
                qual=qual,
                types=_FG_BATTING_LEADERS_TYPES,
                end_season=end_season,
                start_season=start_season,
                ind=ind
            ),
            column_name_mapper=column_mapper.map,
            known_percentages = ['GB/FB']
        )

        print(fg_data)

        return fg_data.sort_values(['WAR', 'OPS'], ascending=False)

    def pitching_stats(self, start_season: int, end_season: int = None, league: str = 'all', qual: Union[int, str] = 1,
                       ind: int = 1) -> pd.DataFrame:
        """
        Get season-level pitching data from FanGraphs.

        ARGUMENTS:
        start_season : int      : first season you want data for
                                  (or the only season if you do not specify an end_season)
        end_season   : int      : final season you want data for
        league       : str      : "all", "nl", or "al"
        qual         : int, str : minimum number of pitches thrown to be included in the data (integer).
                                  Use the string 'y' for fangraphs default.
        ind          : int      : 1 if you want individual season-level data
                                  0 if you want a player's aggreagate data over all seasons in the query
        """

        if start_season is None:
            raise ValueError(
                "You need to provide at least one season to collect data for. " +
                "Try pitching_leaders(season) or pitching_leaders(start_season, end_season)."
            )
        if end_season is None:
            end_season = start_season

        data = self.get_tabular_data_from_url(
            _FG_PITCHING_LEADERS_URL.format(
                league=league,
                qual=qual,
                end_season=end_season,
                start_season=start_season,
                ind=ind,
                types=_FG_PITCHING_LEADERS_TYPES
            )
        )

        # Sort by WAR and wins so best players float to the top
        data = data.sort_values(['WAR', 'W'], ascending=False)

        # Put WAR at the end because it looks better
        cols = data.columns.tolist()
        cols.insert(7, cols.pop(cols.index('WAR')))
        data = data.reindex(columns=cols)

        return data

    def team_batting(self, start_season: int, end_season: int = None, league: str = 'all', ind: int = 1) -> pd.DataFrame:
        """
        Get season-level batting data aggregated by team.

        ARGUMENTS:
        start_season    : int : first season you want data for (or the only season if you do not specify an end_season)
        end_season      : int : final season you want data for
        league          : str : "all", "nl", or "al"
        ind             : int : 1 if you want individual season level data
                                0 if you want a team's aggreagate data over all seasons in the query
        """
        if start_season is None:
            raise ValueError(
                "You need to provide at least one season to collect data for. " +
                "Try team_batting(season) or team_batting(start_season, end_season)."
            )
        if end_season is None:
            end_season = start_season

        fg_data = self.get_tabular_data_from_url(
            _FG_TEAM_BATTING_URL.format(start_season=start_season, end_season=end_season, league=league, ind=ind)
        )

        return fg_data

    def team_fielding(self, start_season: int, end_season: int = None, league: str = 'all', ind: int = 1):
        """
        Get season-level fielding data aggregated by team.

        ARGUMENTS:
        start_season    : int : first season you want data for (or the only season if you do not specify an end_season)
        end_season      : int : final season you want data for
        league          : str : "all", "nl", or "al"
        ind             : int : 1 if you want individual season level data,
                                0 if you want a team's aggregate data over all seasons in the query
        """

        if start_season is None:
            raise ValueError(
                "You need to provide at least one season to collect data for. " +
                "Try team_fielding(season) or team_fielding(start_season, end_season)."
            )
        if end_season is None:
            end_season = start_season

        fg_data = self.get_tabular_data_from_url(
            _FG_TEAM_FIELDING_URL.format(start_season=start_season, end_season=end_season, league=league, ind=ind)
        )

        return fg_data

    def team_pitching(self, start_season: int, end_season: int = None, league: str = 'all', ind: int = 1):
        """
        Get season-level pitching data aggregated by team.

        ARGUMENTS:
        start_season    : int : first season you want data for (or the only season if you do not specify an end_season)
        end_season      : int : final season you want data for
        league          : str : "all", "nl", or "al"
        ind             : int : 1 if you want individual season level data
                                0 if you want a team'ss aggreagate data over all seasons in the query
        """
        if start_season is None:
            raise ValueError(
                "You need to provide at least one season to collect data for. Try team_pitching(season) or team_pitching(start_season, end_season)."
            )
        if end_season is None:
            end_season = start_season

        fg_data = self.get_tabular_data_from_url(
            _FG_TEAM_PITCHING_URL.format(
                start_season=start_season,
                end_season=end_season,
                league=league,
                ind=ind,
                types=_FG_TEAM_PITCHING_TYPES)
        )

        return fg_data


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
