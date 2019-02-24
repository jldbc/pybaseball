import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import requests

def get_soup(start_season, end_season, league, ind):
    url = "http://www.fangraphs.com/leaders.aspx?pos=all&stats=pit&lg={}&qual=0&type=c,4,5,11,7,8,13,-1,24,36,37,40,43,44,48,51,-1,6,45,62,-1,59&season={}&month=0&season1={}&ind={}&team=0,ts&rost=0&age=0&filter=&players=0&page=1_100000"
    url = url.format(league, end_season, start_season, ind)
    s=requests.get(url).content
    #print(s)
    return BeautifulSoup(s, "lxml")

def get_table(soup, ind):
    #doesn't work yet
    tables = soup.find_all('table')
    table = tables[11]
    data = []
    # couldn't find these in the table, hardcoding for now
    if ind == 0:
        headings = ["Team", "W","L","SV","G","GS","IP","SO","K/9","BB/9","HR/9","BABIP","LOB%","GB%","HR/FB","ERA","FIP","xFIP","WAR"]
    else:
        headings = ["Season","Team","W","L","SV","G","GS","IP","SO","K/9","BB/9","HR/9","BABIP","LOB%","GB%","HR/FB","ERA","FIP","xFIP","WAR"]

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
    data.replace(r'^\s*$', np.nan, regex=True, inplace = True)
    data.replace(r'^null$', np.nan, regex=True, inplace = True)

    # convert percent strings to float values
    percentages = ['GB%', 'HR/FB', 'LOB%']
    for col in percentages:
        # skip if column is all NA (happens for some of the more obscure stats + in older seasons)
        if data[col].count()>0:
            data[col] = data[col].str.strip(' %')
            data[col] = data[col].str.strip('%')
            data[col] = data[col].astype(float)/100.
        else:
            #print(col)
            pass

    # convert columns to numeric
    not_numeric = ['Team']
    numeric_cols = [col for col in data.columns if col not in not_numeric]
    data[numeric_cols] = data[numeric_cols].astype(float)
    return data


def team_pitching(start_season, end_season=None, league='all', ind=1):
    """
    Get season-level pitching data aggregated by team. 

    ARGUMENTS:
    start_season : int : first season you want data for (or the only season if you do not specify an end_season)
    end_season : int : final season you want data for 
    league : "all", "nl", or "al"
    ind : int : =1 if you want individual season level data, =0 if you want a team'ss aggreagate data over all seasons in the query
    """
    if start_season is None:
        raise ValueError("You need to provide at least one season to collect data for. Try team_pitching(season) or team_pitching(start_season, end_season).")
    if end_season is None:
        end_season = start_season
    soup = get_soup(start_season=start_season, end_season=end_season, league=league, ind=ind)
    table = get_table(soup, ind)
    table = postprocessing(table)
    return table

def team_pitching_bref(team, start_season, end_season=None):
    """
    Get season-level Pitching Statistics for Specific Team (from Baseball-Reference)

    ARGUMENTS:
    team : str : The Team Abbreviation (i.e. 'NYY' for Yankees) of the Team you want data for
    start_season : int : first season you want data for (or the only season if you do not specify an end_season)
    end_season : int : final season you want data for
    """
    if start_season is None:
        raise ValueError("You need to provide at least one season to collect data for. Try team_pitching_bref(season) or team_pitching_bref(start_season, end_season).")
    if end_season is None:
        end_season = start_season

    url = "https://www.baseball-reference.com/teams/{}".format(team)

    data = []
    headings = None
    for season in range(start_season, end_season+1):
        print("Getting Pitching Data: {} {}".format(season, team))
        stats_url = "{}/{}.shtml".format(url, season)
        response = requests.get(stats_url)
        soup = BeautifulSoup(response.content, 'html.parser')

        table = soup.find_all('table', {'id': 'team_pitching'})[0]

        if headings is None:
            headings = [row.text.strip() for row in table.find_all('th')[1:34]]

        rows = table.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            cols = [ele.text.strip() for ele in cols]
            cols = [col.replace('*', '').replace('#', '') for col in cols]  # Removes '*' and '#' from some names
            cols = [col for col in cols if 'Totals' not in col and 'NL teams' not in col and 'AL teams' not in col]  # Removes Team Totals and other rows
            cols.insert(2, season)
            data.append([ele for ele in cols[0:]])

    headings.insert(2, "Year")
    data = pd.DataFrame(data=data, columns=headings) # [:-5]  # -5 to remove Team Totals and other rows (didn't work in multi-year queries)
    data = data.dropna()  # Removes Row of All Nones

    return data
