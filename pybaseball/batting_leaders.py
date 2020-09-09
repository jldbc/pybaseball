import warnings

import pandas as pd

from pybaseball.datasources.fangraphs import FanGraphs, FanGraphsLeague


def batting_stats(start_season: int, end_season: int = None, league: str = 'all', qual: int = 1,
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

    warnings.warn("batting_stats is deprecated in favor of FanGraphs().batting_stats", DeprecationWarning)

    return FanGraphs().batting_stats(
        start_season,
        end_season=end_season,
        league=FanGraphsLeague(league),
        qual=qual,
        split_seasons=(ind=='1')
    )
