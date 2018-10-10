import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import requests

def get_soup():
    url = 'https://www.fangraphs.com/guts.aspx?type=cn'
    s=requests.get(url).content
    return BeautifulSoup(s, "lxml")

def get_soup_pf(season, handed=False):
    type_pf = 'pfh' if handed else 'pf'
    url = 'https://www.fangraphs.com/guts.aspx?type={}&season={}&teamid=0'
    url = url.format(type_pf, season)
    s=requests.get(url).content
    return BeautifulSoup(s, "lxml")

def get_table(soup):
    tables = soup.find_all('table')
    table = tables[3]
    data = []
    # pull heading names from the fangraphs tables
    headings = [row.text.strip() for row in table.find_all('th')]
    # rename the second occurrence of 'FB%' to 'FB% (Pitch)'
    table_body = table.find('tbody')
    rows = table_body.find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        data.append([ele for ele in cols])

    data = pd.DataFrame(data=data, columns=headings)
    #replace empty strings with NaN
    data.replace(r'^\s*$', np.nan, regex=True, inplace = True)
    cols_to_numeric = [col for col in data.columns if col not in ['Name', 'Team', 'Age Rng', 'Dol']]
    data[cols_to_numeric] = data[cols_to_numeric].astype(float)
    return data

def constants():
    soup = get_soup()
    table = get_table(soup)
    return table

def park_factors(season):
    if season is None:
        raise ValueError("You need to provide a season to collect data for. Try park_factors(season).")
    soup = get_soup_pf(season)
    table = get_table(soup)
    return table

def handedness_park_factors(season):
    if season is None:
        raise ValueError("You need to provide a season to collect data for. Try park_factors(season).")
    soup = get_soup_pf(season, True)
    table = get_table(soup)
    return table