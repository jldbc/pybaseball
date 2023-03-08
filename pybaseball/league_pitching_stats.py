from datetime import date
import io
from typing import Optional, Union

import numpy as np
import pandas as pd
from bs4 import BeautifulSoup

from . import cache
from .utils import most_recent_season, sanitize_date_range
from .datasources.bref import BRefSession

session = BRefSession()


def get_soup(start_dt: Optional[Union[date, str]], end_dt: Optional[Union[date, str]]) -> BeautifulSoup:
    # get most recent standings if date not specified
    if((start_dt is None) or (end_dt is None)):
        print('Error: a date range needs to be specified')
        return None
    url = "http://www.baseball-reference.com/leagues/daily.cgi?user_team=&bust_cache=&type=p&lastndays=7&dates=fromandto&fromandto={}.{}&level=mlb&franch=&stat=&stat_value=0".format(start_dt, end_dt)
    s = session.get(url).content
    # a workaround to avoid beautiful soup applying the wrong encoding
    s = str(s).encode()
    return BeautifulSoup(s, features="lxml")


def get_table(soup: BeautifulSoup) -> pd.DataFrame:
    table = soup.find_all('table')[0]
    raw_data = []
    headings = [th.get_text() for th in table.find("tr").find_all("th")][1:]
    headings.append("mlbID")
    raw_data.append(headings)
    table_body = table.find('tbody')
    rows = table_body.find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        row_anchor = row.find("a")
        mlbid = row_anchor["href"].split("mlb_ID=")[-1] if row_anchor else pd.NA  # ID str or nan
        cols = [ele.text.strip() for ele in cols]
        cols.append(mlbid)
        raw_data.append([ele for ele in cols])
    data = pd.DataFrame(raw_data)
    data = data.rename(columns=data.iloc[0])
    data = data.reindex(data.index.drop(0))
    return data


@cache.df_cache()
def pitching_stats_range(start_dt: Optional[str]=None, end_dt: Optional[str]=None) -> pd.DataFrame:
    """
    Get all pitching stats for a set time range. This can be the past week, the
    month of August, anything. Just supply the start and end date in YYYY-MM-DD
    format.
    """
    # ensure valid date strings, perform necessary processing for query
    start_dt_date, end_dt_date = sanitize_date_range(start_dt, end_dt)
    if start_dt_date.year < 2008:
        raise ValueError("Year must be 2008 or later")
    if end_dt_date.year < 2008:
        raise ValueError("Year must be 2008 or later")
    # retrieve html from baseball reference
    soup = get_soup(start_dt_date, end_dt_date)
    table = get_table(soup)
    table = table.dropna(how='all') # drop if all columns are NA
    #fix some strange formatting for percentage columns
    table = table.replace('---%', np.nan)
    #make sure these are all numeric
    for column in ['Age', '#days', 'G', 'GS', 'W', 'L', 'SV', 'IP', 'H',
                    'R', 'ER', 'BB', 'SO', 'HR', 'HBP', 'ERA', 'AB', '2B',
                    '3B', 'IBB', 'GDP', 'SF', 'SB', 'CS', 'PO', 'BF', 'Pit',
                    'WHIP', 'BAbip', 'SO9', 'SO/W']:
        table[column] = pd.to_numeric(table[column])
    #convert str(xx%) values to float(0.XX) decimal values
    for column in ['Str', 'StL', 'StS', 'GB/FB', 'LD', 'PU']:
        table[column] = table[column].replace('%','',regex=True).astype('float')/100

    table = table.drop('', axis=1)
    return table

def pitching_stats_bref(season: Optional[int]=None) -> pd.DataFrame:
    """
    Get all pitching stats for a set season. If no argument is supplied, gives stats for
    current season to date.
    """
    if season is None:
        season = most_recent_season()
    str_season = str(season)
    start_dt = str_season + '-03-01' #opening day is always late march or early april
    end_dt = str_season + '-11-30' #postseason is definitely over by end of November
    return(pitching_stats_range(start_dt, end_dt))


def bwar_pitch(return_all: bool=False) -> pd.DataFrame:
    """
    Get data from war_daily_pitch table. Returns WAR, its components, and a few other useful stats.
    To get all fields from this table, supply argument return_all=True.
    """
    url = "http://www.baseball-reference.com/data/war_daily_pitch.txt"
    s = session.get(url).content
    c = pd.read_csv(io.StringIO(s.decode('utf-8')))
    if return_all:
        return c
    else:
        cols_to_keep = ['name_common', 'mlb_ID', 'player_ID', 'year_ID', 'team_ID', 'stint_ID', 'lg_ID',
                        'G', 'GS', 'RA','xRA', 'BIP', 'BIP_perc','salary', 'ERA_plus', 'WAR_rep', 'WAA',
                        'WAA_adj','WAR']
        return c[cols_to_keep]
