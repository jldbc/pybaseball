import numpy as np
import pandas as pd
from bs4 import BeautifulSoup, Comment
import requests


def get_soup(start_season, end_season, league, ind):
    url = f"https://www.fangraphs.com/leaders.aspx?pos=all&stats=fld&lg={league}&qual=0&type=1&season={end_season}&month=0&season1={start_season}&ind={ind}&team=0,ts&rost=0&age=0&filter=&players=0&startdate=&enddate=&page=1_100000"
    s = requests.get(url).content
    # print(s)
    return BeautifulSoup(s, "lxml")


def get_table(soup, ind):
    table = soup.find('table', {'class': 'rgMasterTable'})
    data = []

    table_head = table.find('thead')
    th_cols = table_head.find_all('th', {'class': 'rgHeader'})

    # Extract the headers, drop the # header
    headings = [x.text.strip() for x in th_cols][1:]

    data.append(headings)
    table_body = table.find('tbody')
    rows = table_body.find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        data.append([ele for ele in cols[1:]])
    data = pd.DataFrame(data)
    data = data.rename(columns=data.iloc[0])
    data = data.reindex(data.index.drop(0))
    return data


def postprocessing(data):
    # fill missing values with NaN
    data.replace(r'^\s*$', np.nan, regex=True, inplace=True)
    data.replace(r'^null$', np.nan, regex=True, inplace=True)

    # convert percent strings to float values
    percentages = ['CS%', 'lgCS%']
    for col in percentages:
        # skip if column is all NA (happens for some of the more obscure stats + in older seasons)
        if col in data.columns and data[col].count() > 0:
            data[col] = data[col].str.strip(' %')
            data[col] = data[col].str.strip('%')
            data[col] = data[col].astype(float)/100.
        else:
            # print(col)
            pass

    # convert columns to numeric
    not_numeric = ['Team', 'Name', 'Pos\xa0Summary']
    numeric_cols = [col for col in data.columns if col not in not_numeric]

    # data[numeric_cols] = data[numeric_cols].astype(float)
    # Ideally we'd do it the pandas way ^, but it's barfing when some columns have no data
    for col in numeric_cols:
        data[col] = data[col].astype(float)

    return data


def team_fielding(start_season, end_season=None, league='all', ind=1):
    """
    Get season-level fielding data aggregated by team. 

    ARGUMENTS:
    start_season    : int : first season you want data for (or the only season if you do not specify an end_season)
    end_season      : int : final season you want data for 
    league          : str : "all", "nl", or "al"
    ind             : int : =1 if you want individual season level data, =0 if you want a team's
                            aggreagate data over all seasons in the query
    """

    if start_season is None:
        raise ValueError(
            "You need to provide at least one season to collect data for. " +
            "Try team_fielding(season) or team_fielding(start_season, end_season)."
        )
    if end_season is None:
        end_season = start_season
    soup = get_soup(
        start_season=start_season,
        end_season=end_season,
        league=league,
        ind=ind
    )
    table = get_table(soup, ind)
    table = postprocessing(table)
    return table


def team_fielding_bref(team, start_season, end_season=None):
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

    data = []
    headings = None
    for season in range(start_season, end_season+1):
        stats_url = "{}/{}-fielding.shtml".format(url, season)
        response = requests.get(stats_url)
        soup = BeautifulSoup(response.content, 'html.parser')

        fielding_div = soup.find('div', {'id': 'all_standard_fielding'})
        comment = fielding_div.find(
            string=lambda text: isinstance(text, Comment))

        fielding_hidden = BeautifulSoup(comment.extract(), 'html.parser')

        table = fielding_hidden.find('table')

        thead = table.find('thead')

        if headings is None:
            headings = [row.text.strip()
                        for row in thead.find_all('th')]

        rows = table.find('tbody').find_all('tr')
        for row in rows:
            cols = row.find_all(['td', 'th'])
            cols = [ele.text.strip() for ele in cols]
            # Removes '*' and '#' from some names
            cols = [col.replace('*', '').replace('#', '') for col in cols]
            # Removes Team Totals and other rows
            cols = [
                col for col in cols if 'Team Runs' not in col
            ]
            cols.insert(2, season)
            data.append(cols)

    headings.insert(2, "Year")
    data = pd.DataFrame(data=data, columns=headings)
    data = data.dropna()  # Removes Row of All Nones
    data = postprocessing(data)

    return data
