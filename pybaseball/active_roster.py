from typing import Optional

import pandas as pd
from bs4 import BeautifulSoup, Comment

from . import cache
from .utils import most_recent_season, get_bref_id_from_player_link, ACTIVE_TEAMS
from .datasources.bref import BRefSession

session = BRefSession()

def get_soup(team: str) -> BeautifulSoup:
    url = f'https://www.baseball-reference.com/teams/{team}/{most_recent_season()}.shtml'
    s = session.get(url).content
    return  BeautifulSoup(s, "lxml")

def get_tables(soup: BeautifulSoup) -> pd.DataFrame:
    data = []

    # find commented 40-man roster table and parse that
    all_the40man = soup.find(id='all_the40man')
    comment = all_the40man.find(text=lambda text: isinstance(text, Comment))
    table_wrapper = BeautifulSoup(comment, 'lxml')
    table = table_wrapper.find(id='the40man')

    headings = [th.get_text() for th in table.find("tr").find_all("th")]

    # remove the Rk header, it's unnecessary
    headings.pop(0)

    # add ID column name
    headings.append('player_ID')
    headings.append('Alt URL')

    # pull in data rows
    table_body = table.find('tbody')
    rows = table_body.find_all('tr')
    for row in rows:
        player_link = row.find('a')
        if not player_link:
            continue
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]

        player_link = player_link.get('href')

        # determine whether the player has reached the majors and has a bref ID
        if player_link.startswith('/players/'):
            # player has played in majors and has an id
            cols.append(get_bref_id_from_player_link(player_link))
            cols.append('')
        else:
            # player has not reached the majors, give them an alternate url
            cols.append('')
            cols.append(player_link)

        data.append([ele for ele in cols])

    # use headings for column names
    return pd.DataFrame(data, columns=headings)


@cache.df_cache()
def active_roster(team: str) -> pd.DataFrame:
    """
    Returns a pandas DataFrame of the 40-man roster for a given MLB team

    ARGUMENTS
        team (str): the three-letter bref abbreviation for an active MLB team
    """
    # make sure specified team is active
    if team not in ACTIVE_TEAMS:
        raise ValueError(
            "Team must be the three-letter abbreviation of an active MLB team."
        )

    # retrieve html from baseball reference
    soup = get_soup(team)

    df = get_tables(soup)
    return df
