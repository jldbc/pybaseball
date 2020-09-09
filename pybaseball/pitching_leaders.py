import warnings
from typing import Union

import pandas as pd

from pybaseball.datasources import fangraphs


def pitching_stats(start_season: int, end_season: int = None, league: str = 'all', qual: Union[int, str] = 1,
                   ind: int = 1) -> pd.DataFrame:
    """
    Get season-level pitching data from FanGraphs.

    ARGUMENTS:
    start_season : int      : first season you want data for (or the only season if you do not specify an end_season)
    end_season   : int      : final season you want data for
    league       : str      : "all", "nl", or "al"
    qual         : int, str : minimum number of pitches thrown to be included in the data (integer).
                              Use the string 'y' for fangraphs default.
    ind          : int      : 1 if you want individual season-level data
                              0 if you want a player's aggreagate data over all seasons in the query
    """

    warnings.warn("pitching_stats is deprecated in favor of FanGraphs().pitching_stats", DeprecationWarning)

    return fangraphs.FanGraphs().pitching_stats(start_season, end_season=end_season, league=league, qual=qual, ind=ind)
