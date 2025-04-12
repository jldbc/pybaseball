from typing import Optional

import pandas as pd
from bs4 import BeautifulSoup

from . import cache
from .utils import most_recent_season
from .datasources.bref import BRefSession

session = BRefSession()

def get_soup(year: int) -> BeautifulSoup:
    url = f'https://www.baseball-reference.com/leagues/majors/{year}-appearances-fielding.shtml'
    s = session.get(url).content
    return BeautifulSoup(s, "lxml")

def get_tables(soup: BeautifulSoup, season: int) -> pd.DataFrame:
    data = []

    # get player appearances table
    table = soup.find(id='appearances')
    headings = [th.get_text() for th in table.find("tr").find_all("th")]

    # remove the Rk header, it's unnecessary
    headings.pop(0)

    # pull in data rows
    table_body = table.find('tbody')
    rows = table_body.find_all('tr')
    for row in rows:
        if not row.find_all('a'):
            continue
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        data.append([ele for ele in cols])

    # use headings for column names
    return pd.DataFrame(data, columns=headings)


@cache.df_cache()
def appearances_bref(season:Optional[int] = None) -> pd.DataFrame:
    """
    Returns a pandas DataFrame of the defensive appearances for a given MLB season, or
    appearances for the current / most recent season if the date is not specified.

    ARGUMENTS
        season (int): the year of the season
    """
    # get most recent standings if date not specified
    if season is None:
        season = most_recent_season()
    if season < 1871:
        raise ValueError(
            "This query currently only returns appearances until the 1871 season. "
            "Try looking at years from 1871 to present."
        )

    # retrieve html from baseball reference
    soup = get_soup(season)
    df = get_tables(soup, season)
    return df
