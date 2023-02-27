from typing import Optional

import pandas as pd

from . import cache
from .datahelpers import postprocessing
from .datasources.bref import BRefSession
from .utils import most_recent_season

session = BRefSession()

# pylint: disable=line-too-long
_URL = "https://www.baseball-reference.com/leagues/majors/{year}-batting-pitching.shtml#teams_batting_pitching"


def get_team_batting_against(year: int) -> pd.DataFrame:
    url = _URL.format(year=year)
    res = session.get(url, timeout=None)
    if res.ok:
        team_batting_against = pd.read_html(res.content)
        return team_batting_against
    else:
        raise ValueError(res.reason)


@cache.df_cache()
def team_batting_against(season: Optional[int] = None) -> pd.DataFrame:
    if season is None:
        season = most_recent_season()
    team_batting_against = get_team_batting_against(season)
    team_batting_against = pd.concat(team_batting_against)
    team_batting_against = postprocess(team_batting_against)
    return team_batting_against


def postprocess(team_batting_against: pd.DataFrame) -> pd.DataFrame:
    # drop usually empty PA for which data is not known column
    team_batting_against = team_batting_against.drop('PAu', 1)

    # skip league average and duplicative header
    team_batting_against = team_batting_against.iloc[:30]

    # fix numeric conversion now that string values are removed
    postprocessing.convert_numeric(team_batting_against, postprocessing.columns_except(team_batting_against, ['Tm']))
    int_cols = ["G", "PA", "AB", "R", "H", "2B", "3B", "HR", "SB",
                "CS", "BB", "SO", "TB", "GDP", "HBP", "SH", "SF", "IBB", "ROE"]
    team_batting_against.loc[:, int_cols] = team_batting_against.loc[:, int_cols].astype(int)

    return team_batting_against
