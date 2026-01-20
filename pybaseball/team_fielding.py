from typing import List, Optional

import pandas as pd
from bs4 import BeautifulSoup, Comment

from . import cache
from .datahelpers import postprocessing
from .datasources.fangraphs import fg_team_fielding_data
from .datasources.bref import BRefSession

session = BRefSession()

# This is just a pass through for the new, more configurable function
team_fielding = fg_team_fielding_data


@cache.df_cache()
def team_fielding_bref(team: str, start_season: int, end_season: Optional[int]=None) -> pd.DataFrame:
    """
    Get season-level Fielding Statistics for Specific Team (from Baseball-Reference)

    ARGUMENTS:
    team            : str : The Team Abbreviation (i.e., 'NYY' for Yankees) of the Team you want data for
    start_season    : int : first season you want data for (or the only season if you do not specify an end_season)
    end_season      : int : final season you want data for
    """

    if start_season is None:
        raise ValueError(
            "You need to provide at least one season to collect data for. " +
            "Try team_fielding_bref(season) or team_fielding_bref(start_season, end_season)."
        )
    if end_season is None:
        end_season = start_season

    url = "https://www.baseball-reference.com/teams/{}".format(team)

    raw_data = []
    headings: Optional[List[str]] = None
    for season in range(start_season, end_season+1):
        stats_url = "{}/{}-fielding.shtml".format(url, season)
        response = session.get(stats_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        table = soup.find_all('table', {'id': 'players_standard_fielding'})[0]

        if headings is None:
            over_header = [row.text.strip() for row in table.find_all('th', {'class': 'over_header'})[1:]]
            headings = [row.text.strip() for row in table.find_all('th')[1:36]]
            headings = [col for col in headings if col not in over_header]

        rows = table.find('tbody').find_all('tr')
        for row in rows:
            cols = row.find_all(['td', 'th'])
            cols = [ele.text.strip() for ele in cols]
            # Removes '*' and '#' from some names
            cols = [col.replace('*', '').replace('#', '') for col in cols]
            cols.insert(2, season)
            # Removes Non-Shift Infield Positioning and other rows
            if 'Non-Shift Infield Positioning' not in cols and 'Infield Shifts' not in cols and 'Outfield Positioning' not in cols:
                raw_data.append(cols)

    assert headings is not None
    headings.insert(2, "Year")
    data = pd.DataFrame(data=raw_data, columns=headings)
    data = data.dropna()  # Removes Row of All Nones

    postprocessing.coalesce_nulls(data)
    postprocessing.convert_percentages(data, ['CS%', 'lgCS%'])
    postprocessing.convert_numeric(
        data,
        postprocessing.columns_except(
            data,
            ['Awards', 'Player', 'Pos']
        )
    )

    return data
