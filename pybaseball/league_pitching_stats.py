import requests
import pandas as pd
import numpy as np
import io
import warnings
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
    url = f"https://www.fangraphs.com/leaders.aspx?pos=all&stats=pit&lg=all&qual=1&type=c,4,5,6,7,8,9,10,11,114,12,13,14,15,16,17,18,19,20,21,22,23,24,36,37,38,40,120,121,217,41,42,43,44,117,118,119,45,124,62,122,229,240,251,262,273,230,241,252,263,274,231,242,253,264,275,234,245,256,267,278,226,237,248,259,270,235,246,257,268,279,228,239,250,261,272,227,238,249,260,271,232,243,254,265,276,233,244,255,266,277,236,247,258,269,280,63,64,65,66,67,68,69,70,71,72,73,74,115,116,212,213,214,215,58,59,60,54,55,56,57,29,30,31,292,293,294,295,296,297,298,299&season={start_dt[:4]}&month=0&season1={end_dt[:4]}&ind=0&team=0&rost=0&age=0&filter=&players=0&startdate={start_dt}&enddate={end_dt}&page=1_1500"
    s = requests.get(url).content
    return BeautifulSoup(s, "lxml")


def get_table(soup):
    warnings.warn("\nPlease consider supporting FanGraphs\nhttps://plus.fangraphs.com/product/fangraphs-membership/", Warning)
    table = soup.find_all('table')[16]
    data = []
    headings = [th.get_text() for th in table.find_all("th")]
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
    # retrieve html from fangraphs 
    soup = get_soup(start_dt, end_dt)
    table = get_table(soup)
    table = table.dropna(how='all')  # drop if all columns are NA
    # scraped data is initially in string format.
    # convert the necessary columns to numeric.
    for column in ['#', 'W', 'L', 'ERA', 'G', 'GS', 'CG', 'ShO', 'SV',
           'HLD', 'BS', 'IP', 'TBF', 'H', 'R', 'ER', 'HR', 'BB', 'IBB', 'HBP',
           'WP', 'BK', 'SO', 'K/9', 'BB/9', 'K/BB', 'HR/9', 'AVG', 'WHIP', 'BABIP', 
           'ERA-', 'FIP-', 'xFIP-',
           'FIP', 'E-F', 'xFIP', 'SIERA', 'vFA (pi)', 'FA-X (pi)',
           'FA-Z (pi)', 'wFA (pi)', 'vFC (pi)', 'FC-X (pi)',
           'FC-Z (pi)', 'wFC (pi)', 'vFS (pi)', 'FS-X (pi)',
           'FS-Z (pi)', 'wFS (pi)', 'vSI (pi)', 'SI-X (pi)',
           'SI-Z (pi)', 'wSI (pi)', 'vCH (pi)', 'CH-X (pi)',
           'CH-Z (pi)', 'wCH (pi)', 'vSL (pi)', 'SL-X (pi)',
           'SL-Z (pi)', 'wSL (pi)', 'vCU (pi)', 'CU-X (pi)',
           'CU-Z (pi)', 'wCU (pi)', 'vCS (pi)', 'CS-X (pi)',
           'CS-Z (pi)', 'wCS (pi)', 'vKN (pi)', 'KN-X (pi)',
           'KN-Z (pi)', 'wKN (pi)', 'vSB (pi)', 'SB-X (pi)',
           'SB-Z (pi)', 'wSB (pi)', 'vXX (pi)', 'XX-X (pi)',
           'XX-Z (pi)', 'wXX (pi)', 'WPA', '-WPA', '+WPA', 'RE24', 'REW',
           'pLI', 'inLI', 'gmLI', 'exLI', 'Pulls', 'WPA/LI', 'Clutch', 'SD',
           'MD', 'RA9-WAR', 'BIP-Wins', 'LOB-Wins', 'FDP-Wins', 'RAR', 'WAR',
           'Starting', 'Start-IP', 'Relieving', 'Relief-IP',
           'Balls', 'Strikes', 'Pitches', 'Pace (pi)']:
        #table[column] = table[column].astype('float')
        table[column] = pd.to_numeric(table[column])
        #table['column'] = table['column'].convert_objects(convert_numeric=True)
    table = table.reset_index(drop=True)
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
