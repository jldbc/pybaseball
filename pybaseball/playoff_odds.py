from io import StringIO
from typing import List, Optional

import pandas as pd
from bs4 import BeautifulSoup, Comment, PageElement, ResultSet

from . import cache
from .utils import most_recent_season
from .datasources.bref import BRefSession

session = BRefSession()

def playoff_odds(season):
    if season < 2020:
        print(f"Playoff odds not found for {season}")
        return None

    session = BRefSession()
    url = f'https://www.baseball-reference.com/leagues/majors/{season}-playoff-odds.shtml'
    s = session.get(url).content
    soup = BeautifulSoup(s, "lxml")

    # Find the specific table by id
    table = soup.find('table', {'id': 'playoff_prob_mlb'})
    if table is None:
        print(f"Table with id 'playoff_prob_mlb' not found for season {season}")
        return None

    # HTML → DataFrame
    df = pd.read_html(StringIO(str(table)))[0]

    # DataFrame → JSON string
    json_str = df.to_json(orient="records")

    # JSON string → DataFrame
    new_df = pd.read_json(StringIO(json_str))

    cols = [
        ('Unnamed: 1_level_0', 'Tm'),
        ('Unnamed: 2_level_0', 'Lg'),
        ('Unnamed: 20_level_0', 'WC'),
        ('Unnamed: 21_level_0', 'Div'),
        ('Unnamed: 22_level_0', 'LDS'),
        ('Unnamed: 23_level_0', 'LCS'),
        ('Unnamed: 24_level_0', 'Pennant'),
        ('Unnamed: 25_level_0', 'Win WS')
    ]

    df_filtered = df[cols].dropna()

    # Remove division header rows
    division_names = [
        'NL East', 'NL Central', 'NL West',
        'AL East', 'AL Central', 'AL West', 'Tm'
    ]

    mask = ~df_filtered.iloc[:, 0].isin(division_names)
    new_df = df_filtered[mask].reset_index(drop=True)

    # Clean column names
    new_df.columns = ['Tm', 'Lg', 'WC', 'Div', 'LDS', 'LCS', 'Pennant', 'Win WS']

    return new_df


