
from typing import Union

import pandas as pd
import requests

# test id box_score(565997)

ROOT_URL = "https://statsapi.mlb.com/api/"

_STATS_BOX_SCORE_REQUEST = "v1/game/{game_pk}/boxscore"

def box_score(game_pk: Union[str, int]):
    """
    Pulls in statsapi MLB box score data identified by its MLB game ID
    (game_pk in statcast data)

    INPUTS:
    game_pk : 6-digit integer MLB game ID to retrieve
    """
    result = requests.get(ROOT_URL + _STATS_BOX_SCORE_REQUEST.format(game_pk=game_pk)
)
    return format_box_score(result.json())

def format_box_score(data):

    home_df = pd.DataFrame(data['teams']['home']['players'].values())
    home_df['team'] = 'home'
    away_df = pd.DataFrame(data['teams']['away']['players'].values())
    away_df['team'] = 'away'

    home_df = home_df.loc[:, ['team', 'person', 'jerseyNumber', 'position', 'stats']]
    home_df['person'] = home_df['person'].apply(lambda x: x['fullName'])
    home_df['position'] = home_df['position'].apply(lambda x: x['name'])
    stats_df = pd.json_normalize(home_df['stats'], sep='_')
    home_df.drop('stats', axis=1, inplace=True)
    home_df = pd.concat([home_df, stats_df], axis=1)
    home_df = home_df[home_df['batting_gamesPlayed'] == 1]

    away_df = away_df.loc[:, ['team', 'person', 'jerseyNumber', 'position', 'stats']]
    away_df['person'] = away_df['person'].apply(lambda x: x['fullName'])
    away_df['position'] = away_df['position'].apply(lambda x: x['name'])
    stats_df = pd.json_normalize(away_df['stats'], sep='_')
    away_df.drop('stats', axis=1, inplace=True)
    away_df = pd.concat([away_df, stats_df], axis=1)
    away_df = away_df[away_df['batting_gamesPlayed'] == 1]

    joined_df = pd.concat([home_df, away_df])

    return joined_df