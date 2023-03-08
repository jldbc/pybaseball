import io
from datetime import date
from typing import Optional

import pandas as pd
from bs4 import BeautifulSoup

from . import cache
from .utils import most_recent_season, sanitize_date_range
from .datasources.bref import BRefSession

session = BRefSession()


def get_soup(start_dt: date, end_dt: date) -> BeautifulSoup:
    # get most recent standings if date not specified
    # if((start_dt is None) or (end_dt is None)):
    #    print('Error: a date range needs to be specified')
    #    return None
    url = "http://www.baseball-reference.com/leagues/daily.cgi?user_team=&bust_cache=&type=b&lastndays=7&dates=fromandto&fromandto={}.{}&level=mlb&franch=&stat=&stat_value=0".format(start_dt, end_dt)
    s = session.get(url).content
    # a workaround to avoid beautiful soup applying the wrong encoding
    s = str(s).encode()
    return BeautifulSoup(s, features="lxml")


def get_table(soup: BeautifulSoup) -> pd.DataFrame:
    table = soup.find_all('table')[0]
    data = []
    headings = [th.get_text() for th in table.find("tr").find_all("th")][1:]
    headings.append("mlbID")
    data.append(headings)
    table_body = table.find('tbody')
    rows = table_body.find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        row_anchor = row.find("a")
        mlbid = row_anchor["href"].split("mlb_ID=")[-1] if row_anchor else pd.NA  # ID str or nan
        cols = [ele.text.strip() for ele in cols]
        cols.append(mlbid)
        data.append([ele for ele in cols])
    df = pd.DataFrame(data)
    df = df.rename(columns=df.iloc[0])
    df = df.reindex(df.index.drop(0))
    return df


def batting_stats_range(start_dt: Optional[str] = None, end_dt: Optional[str] = None) -> pd.DataFrame:
    """
    Get all batting stats for a set time range. This can be the past week, the
    month of August, anything. Just supply the start and end date in YYYY-MM-DD
    format.
    """
    # make sure date inputs are valid
    start_dt_date, end_dt_date = sanitize_date_range(start_dt, end_dt)
    if start_dt_date.year < 2008:
        raise ValueError("Year must be 2008 or later")
    if end_dt_date.year < 2008:
        raise ValueError("Year must be 2008 or later")
    # retrieve html from baseball reference
    soup = get_soup(start_dt_date, end_dt_date)
    table = get_table(soup)
    table = table.dropna(how='all')  # drop if all columns are NA
    # scraped data is initially in string format.
    # convert the necessary columns to numeric.
    for column in ['Age', '#days', 'G', 'PA', 'AB', 'R', 'H', '2B', '3B',
                    'HR', 'RBI', 'BB', 'IBB', 'SO', 'HBP', 'SH', 'SF', 'GDP',
                    'SB', 'CS', 'BA', 'OBP', 'SLG', 'OPS', 'mlbID']:
        #table[column] = table[column].astype('float')
        table[column] = pd.to_numeric(table[column])
        #table['column'] = table['column'].convert_objects(convert_numeric=True)
    table = table.drop('', axis=1)
    return table


@cache.df_cache()
def batting_stats_bref(season: Optional[int] = None) -> pd.DataFrame:
    """
    Get all batting stats for a set season. If no argument is supplied, gives
    stats for current season to date.
    """
    if season is None:
        season = most_recent_season()
    start_dt = f'{season}-03-01' #opening day is always late march or early april
    end_dt = f'{season}-11-30' #postseason is definitely over by end of November
    return batting_stats_range(start_dt, end_dt)


@cache.df_cache()
def bwar_bat(return_all: bool = False) -> pd.DataFrame:
    """
    Get data from war_daily_bat table. Returns WAR, its components, and a few other useful stats.
    To get all fields from this table, supply argument return_all=True.
    """
    url = "http://www.baseball-reference.com/data/war_daily_bat.txt"
    s = session.get(url).content
    c=pd.read_csv(io.StringIO(s.decode('utf-8')))
    if return_all:
        return c
    else:
        cols_to_keep = ['name_common', 'mlb_ID', 'player_ID', 'year_ID', 'team_ID', 'stint_ID', 'lg_ID',
                        'pitcher','G', 'PA', 'salary', 'runs_above_avg', 'runs_above_avg_off','runs_above_avg_def',
                        'WAR_rep','WAA','WAR']
        return c[cols_to_keep]
