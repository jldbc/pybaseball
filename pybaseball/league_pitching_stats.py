import requests
import pandas as pd
import numpy as np
import io
from bs4 import BeautifulSoup
import datetime

def validate_datestring(date_text):
    try:
        datetime.datetime.strptime(date_text, '%Y-%m-%d')
    except ValueError:
        raise ValueError("Incorrect data format, should be YYYY-MM-DD")

def sanitize_input(start_dt, end_dt):
    # if no dates are supplied, assume they want yesterday's data
    # send a warning in case they wanted to specify
    if start_dt is None and end_dt is None:
        today = datetime.datetime.today()
        start_dt = (today - datetime.timedelta(1)).strftime("%Y-%m-%d")
        end_dt = today.strftime("%Y-%m-%d")
        print("Warning: no date range supplied. Returning yesterday's data. For a different date range, try pitching_stats_range(start_dt, end_dt) or pitching_stats(season).")

    #if only one date is supplied, assume they only want that day's stats
    #query in this case is from date 1 to date 1
    if start_dt is None:
        start_dt = end_dt
    if end_dt is None:
        end_dt = start_dt
    #if end date occurs before start date, swap them 
    if end_dt < start_dt:
        temp = start_dt
        start_dt = end_dt
        end_dt = temp
        
    # now that both dates are not None, make sure they are valid date strings
    validate_datestring(start_dt)
    validate_datestring(end_dt)
    return start_dt, end_dt

def get_soup(start_dt, end_dt):
    # get most recent standings if date not specified
    if((start_dt is None) or (end_dt is None)):
        print('Error: a date range needs to be specified')
        return None
    url = "http://www.baseball-reference.com/leagues/daily.cgi?user_team=&bust_cache=&type=p&lastndays=7&dates=fromandto&fromandto={}.{}&level=mlb&franch=&stat=&stat_value=0".format(start_dt, end_dt)
    s = requests.get(url).content
    return BeautifulSoup(s, "lxml")


def get_table(soup):
    table = soup.find_all('table')[0]
    data = []
    headings = [th.get_text() for th in table.find("tr").find_all("th")][1:]
    data.append(headings)
    table_body = table.find('tbody')
    rows = table_body.find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        data.append([ele for ele in cols])
    data = pd.DataFrame(data)
    data = data.rename(columns=data.iloc[0])
    data = data.reindex(data.index.drop(0))
    return data


def pitching_stats_range(start_dt=None, end_dt=None):
    """
    Get all pitching stats for a set time range. This can be the past week, the 
    month of August, anything. Just supply the start and end date in YYYY-MM-DD 
    format. 
    """
    # ensure valid date strings, perform necessary processing for query
    start_dt, end_dt = sanitize_input(start_dt, end_dt)
    if datetime.datetime.strptime(start_dt, "%Y-%m-%d").year < 2008:
        raise ValueError("Year must be 2008 or later")
    if datetime.datetime.strptime(end_dt, "%Y-%m-%d").year < 2008:
        raise ValueError("Year must be 2008 or later")
    # retrieve html from baseball reference
    soup = get_soup(start_dt, end_dt)
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

    table = table.drop('',1)
    return table

def pitching_stats_bref(season=None):
    """
    Get all pitching stats for a set season. If no argument is supplied, gives stats for 
    current season to date. 
    """
    if season is None:
        season = datetime.datetime.today().strftime("%Y")
    season = str(season)
    start_dt = season + '-03-01' #opening day is always late march or early april
    end_dt = season + '-11-01' #season is definitely over by November 
    return(pitching_stats_range(start_dt, end_dt))


def bwar_pitch(return_all=False):
    """
    Get data from war_daily_pitch table. Returns WAR, its components, and a few other useful stats. 
    To get all fields from this table, supply argument return_all=True.  
    """
    url = "http://www.baseball-reference.com/data/war_daily_pitch.txt"
    s = requests.get(url).content
    c=pd.read_csv(io.StringIO(s.decode('utf-8')))
    if return_all:
        return c
    else:
        cols_to_keep = ['name_common', 'mlb_ID', 'player_ID', 'year_ID', 'team_ID', 'stint_ID', 'lg_ID',
                        'G', 'GS', 'RA','xRA', 'BIP', 'BIP_perc','salary', 'ERA_plus', 'WAR_rep', 'WAA',
                        'WAA_adj','WAR']
        return c[cols_to_keep]
