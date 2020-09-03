import pandas as pd
import requests
from bs4 import BeautifulSoup

import pybaseball.datasources.fangraphs as fangraphs

_FG_TEAM_BATTING_URL = "/leaders.aspx?pos=all&stats=bat&lg={league}&qual=0&type=8&season={end_season}&month=0&season1={start_season}&ind={ind}&team=0,ts&rost=0&age=0&filter=&players=0&page=1_100000"

def team_batting(start_season: int, end_season: int = None, league: str = 'all', ind: int = 1):
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
            "You need to provide at least one season to collect data for. Try team_batting(season) or team_batting(start_season, end_season)."
        )
    if end_season is None:
        end_season = start_season

    fg_data = fangraphs.get_fangraphs_tabular_data_from_url(
        _FG_TEAM_BATTING_URL.format(start_season=start_season, end_season=end_season, league=league, ind=ind)
    )

    return fg_data

def team_batting_bref(team, start_season, end_season=None):
    """
    Get season-level Batting Statistics for Specific Team (from Baseball-Reference)

    ARGUMENTS:
    team : str : The Team Abbreviation (i.e. 'NYY' for Yankees) of the Team you want data for
    start_season : int : first season you want data for (or the only season if you do not specify an end_season)
    end_season : int : final season you want data for
    """
    if start_season is None:
        raise ValueError(
            "You need to provide at least one season to collect data for. Try team_batting_bref(season) or team_batting_bref(start_season, end_season)."
        )
    if end_season is None:
        end_season = start_season

    url = "https://www.baseball-reference.com/teams/{}".format(team)

    data = []
    headings = None
    for season in range(start_season, end_season+1):
        print("Getting Batting Data: {} {}".format(season, team))
        stats_url = "{}/{}.shtml".format(url, season)
        response = requests.get(stats_url)
        soup = BeautifulSoup(response.content, 'html.parser')

        table = soup.find_all('table', {'class': 'sortable stats_table'})[0]

        if headings is None:
            headings = [row.text.strip() for row in table.find_all('th')[1:28]]

        rows = table.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            cols = [ele.text.strip() for ele in cols]
            cols = [col.replace('*', '').replace('#', '') for col in cols]  # Removes '*' and '#' from some names
            cols = [col for col in cols if 'Totals' not in col and 'NL teams' not in col and 'AL teams' not in col]  # Removes Team Totals and other rows
            cols.insert(2, season)
            data.append([ele for ele in cols[0:]])

    headings.insert(2, "Year")
    data = pd.DataFrame(data=data, columns=headings) # [:-5]  # -5 to remove Team Totals and other rows
    data = data.dropna()  # Removes Row of All Nones

    return data
