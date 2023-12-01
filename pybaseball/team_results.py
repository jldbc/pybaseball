from datetime import datetime
from typing import Optional

from bs4 import BeautifulSoup
import numpy as np
import pandas as pd

from pybaseball.utils import get_first_season, most_recent_season

from . import cache
from .datasources.bref import BRefSession

session = BRefSession()

# TODO: retrieve data for all teams? a full season's worth of results

def get_soup(season: Optional[int], team: str) -> BeautifulSoup:
    # get most recent year's schedule if year not specified
    if season is None:
        season = most_recent_season()
    url = "http://www.baseball-reference.com/teams/{}/{}-schedule-scores.shtml".format(team, season)
    print(url)
    s = session.get(url).content
    return BeautifulSoup(s, "lxml")

def get_table(soup: BeautifulSoup, team: str) -> pd.DataFrame:
    try:
        table = soup.find_all('table')[0]
    except:
        raise ValueError("Data cannot be retrieved for this team/year combo. Please verify that your team abbreviation is accurate and that the team existed during the season you are searching for.")
    data = []
    headings = [th.get_text() for th in table.find("tr").find_all("th")]
    headings = headings[1:] # the "gm#" heading doesn't have a <td> element
    headings[3] = "Home_Away"
    data.append(headings)
    table_body = table.find('tbody')
    rows = table_body.find_all('tr')
    for row_index in range(len(rows) - 1): #last row is a description of column meanings
        row = rows[row_index]
        try:
            cols = row.find_all('td')
            #links = row.find_all('a')
            if cols[1].text == "":
                cols[1].string = team # some of the older season don't seem to have team abbreviation on their tables
            if cols[3].text == "":
                cols[3].string = 'Home' # this element only has an entry if it's an away game
            if cols[12].text == "":
                cols[12].string = "None" # tie games won't have a pitcher win or loss
            if cols[13].text == "":
                cols[13].string = "None"
            if cols[14].text == "":
                cols[14].string = "None" # games w/o saves have blank td entry
            if cols[8].text == "":
                cols[8].string = "9" # entry is blank if no extra innings
            if cols[16].text=="":
                cols[16].string = "Unknown"
            if cols[15].text=="":
                cols[15].string = "Unknown"
            if cols[17].text == "":
                cols[17].string = "Unknown" # Unknown if attendance data is missing

            cols = [ele.text.strip() for ele in cols]
            data.append([ele for ele in cols if ele])
        except:
            # two cases will break the above: games that haven't happened yet, and BR's redundant mid-table headers
            # if future games, grab the scheduling info. Otherwise do nothing. 
            if len(cols) > 1:
                cols = [ele.text.strip() for ele in cols][0:5]
                data.append([ele for ele in cols if ele])
    #convert to pandas dataframe. make first row the table's column names and reindex.
    df = pd.DataFrame(data)
    df = df.rename(columns=df.iloc[0])
    df = df.reindex(df.index.drop(0))
    df = df.drop('', axis=1) #not a useful column
    df['Attendance'].replace(r'^Unknown$', np.nan, regex=True, inplace = True) # make this a NaN so the column can benumeric
    return df

def process_win_streak(data: pd.DataFrame) -> pd.DataFrame:
    """
    Convert "+++"/"---" formatted win/loss streak column into a +/- integer column
    """
    #only do this if there are non-NANs in the column
    if data['Streak'].count() > 0:
        data['Streak2'] = data['Streak'].str.len()
        data.loc[data['Streak'].str[0]=='-','Streak2'] = -data['Streak2']
        data['Streak'] = data['Streak2']
        data = data.drop(columns="Streak2")
    return data

def make_numeric(data: pd.DataFrame) -> pd.DataFrame:
    # first remove commas from attendance values
    # skip if column is all NA (not sure if everyone kept records in the early days)
    if data['Attendance'].count() > 0:
        data['Attendance'] = data['Attendance'].str.replace(',','')
        #data[num_cols] = data[num_cols].astype(float)
    else:
        data['Attendance'] = np.nan

    # now make everything numeric
    num_cols = ["R", "RA", "Inn", "Rank", "Attendance"]#,'Streak']
    data[num_cols] = data[num_cols].astype(float) #not int because of NaNs
    return data

@cache.df_cache()
def schedule_and_record(season: int, team: str) -> pd.DataFrame:
    """ 
    Retrieve a team's game-level results for a given season, including win/loss/tie result, score, attendance, 
    and winning/losing/saving pitcher. If the season is incomplete, it will provide scheduling information for 
    future games.

    ARGUMENTS
        season: Integer. The season for which you want a team's record data.
        team: String. The abbreviation of the team for which you are requesting data (e.g. "PHI", "BOS", "LAD").
    """
    # retrieve html from baseball reference
    # sanatize input
    team = team.upper()
    try:
        first_season = get_first_season(team)
        if first_season is None or season < first_season:
            m = "Season cannot be before first year of a team's existence"
            raise ValueError(m)
    # ignore validation if team isn't found in dictionary
    except KeyError:
        pass
    if season > datetime.now().year:
        raise ValueError('Season cannot be after current year')

    soup = get_soup(season, team)
    table = get_table(soup, team)
    table = process_win_streak(table)
    table = make_numeric(table)
    return table
