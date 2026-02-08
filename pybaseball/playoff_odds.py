from io import StringIO
from typing import List, Optional

import pandas as pd
from bs4 import BeautifulSoup, Comment, PageElement, ResultSet

from . import cache
from .utils import most_recent_season
from .datasources.bref import BRefSession

session = BRefSession()


def playoff_odds(season):

    if season >= 2020:
        session = BRefSession()
        url = f'https://www.baseball-reference.com/leagues/majors/{season}-playoff-odds.shtml'
        s = session.get(url).content
        soup = BeautifulSoup(s, "lxml")
        # Find the specific table by id
        table = soup.find('table', {'id': 'playoff_prob_mlb'})
        
        if table is None:
            print(f"Table with id 'playoff_scenarios_mlb' not found for season {season}")
            df = None
        
        # Use pandas' read_html for easier parsing
        df = pd.read_html(StringIO(str(table)))[0]
        df = df.iloc[:, [1, 2, 20, 21, 22, 23, 24, 25]]
        df = df.reset_index(drop=True)

        division_names = ['NL East', 'NL Central', 'NL West', 'AL East', 'AL Central', 'AL West', 'Tm']
        new_df = pd.DataFrame(columns=df.columns)
        
        for index, row in df.iterrows():
            # Check if first column (index 0) does not contain division names
            if row.iloc[0] not in division_names:
                new_df = pd.concat([new_df, row.to_frame().T], ignore_index=True)
        new_df = new_df.dropna()
        #there is a BYE column in the most current season
        new_df.columns = ['Tm', 'Lg', 'WC', 'Div', 'LDS', 'LCS', 'Pennant', 'Win WS']
 
    else:
        new_df = None
        print(f"Playoff odds not found for {season}")
        
    return new_df



