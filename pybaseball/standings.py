from typing import List, Optional

import pandas as pd
import requests
from bs4 import BeautifulSoup, Comment

from . import cache
from .utils import most_recent_season


def get_soup(year: int) -> BeautifulSoup:
    url = f'http://www.baseball-reference.com/leagues/MLB/{year}-standings.shtml'
    s = requests.get(url).content
    return BeautifulSoup(s, "lxml")

def get_tables(soup: BeautifulSoup, season: int) -> List[pd.DataFrame]:
    datasets = []
    if season >= 1969:
        tables = soup.find_all('table')
        if season == 1981:
            # For some reason BRef has 1981 broken down by halves and overall
            # https://www.baseball-reference.com/leagues/MLB/1981-standings.shtml
            tables = [x for x in tables if 'overall' in x.get('id', '')]
        for table in tables:
            data = []
            headings = [th.get_text() for th in table.find("tr").find_all("th")]
            data.append(headings)
            table_body = table.find('tbody')
            rows = table_body.find_all('tr')
            for row in rows:
                cols = row.find_all('td')
                cols = [ele.text.strip() for ele in cols]
                cols.insert(0,row.find_all('a')[0]['title']) # team name
                data.append([ele for ele in cols if ele])
            datasets.append(data)
    else:
        data = []
        table = soup.find('table')
        headings = [th.get_text() for th in table.find("tr").find_all("th")]
        headings[0] = "Name"
        if season >= 1930:
            for _ in range(15):
                headings.pop()
        elif season >= 1876:
            for _ in range(14):
                headings.pop()
        else:
            for _ in range(16):
                headings.pop()
        data.append(headings)
        table_body = table.find('tbody')
        rows = table_body.find_all('tr')
        for row in rows:
            if row.find_all('a') == []:
                continue
            cols = row.find_all('td')
            if season >= 1930:
                for _ in range(15):
                    cols.pop()
            elif season >= 1876:
                for _ in range(14):
                    cols.pop()
            else:
                for _ in range(16):
                    cols.pop()
            cols = [ele.text.strip() for ele in cols]
            cols.insert(0,row.find_all('a')[0]['title']) # team name
            data.append([ele for ele in cols if ele])
        datasets.append(data)
    #convert list-of-lists to dataframes
    for idx in range(len(datasets)):
        datasets[idx] = pd.DataFrame(datasets[idx])
    return datasets #returns a list of dataframes


@cache.df_cache()
def standings(season:Optional[int] = None) -> pd.DataFrame:
    # get most recent standings if date not specified
    if season is None:
        season = most_recent_season()
    if season < 1871:
        raise ValueError(
            "This query currently only returns standings until the 1871 season. "
            "Try looking at years from 1871 to present."
        )

    # retrieve html from baseball reference
    soup = get_soup(season)
    if season >= 1969:
        raw_tables = get_tables(soup, season)
    else:
        t = [x for x in soup.find_all(string=lambda text:isinstance(text,Comment)) if 'expanded_standings_overall' in x]
        code = BeautifulSoup(t[0], "lxml")
        raw_tables = get_tables(code, season)
    tables = [pd.DataFrame(table) for table in raw_tables]
    for idx in range(len(tables)):
        tables[idx] = tables[idx].rename(columns=tables[idx].iloc[0])
        tables[idx] = tables[idx].reindex(tables[idx].index.drop(0))
    return tables
