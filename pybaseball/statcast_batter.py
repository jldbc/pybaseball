import io
from typing import Optional, Union

import pandas as pd
import requests

from . import cache
from .utils import sanitize_input, split_request, sanitize_statcast_columns


def statcast_batter(start_dt: Optional[str] = None, end_dt: Optional[str] = None, player_id: Optional[int] = None) -> pd.DataFrame:
    """
    Pulls statcast pitch-level data from Baseball Savant for a given batter.

    ARGUMENTS
        start_dt : YYYY-MM-DD : the first date for which you want a player's statcast data
        end_dt : YYYY-MM-DD : the final date for which you want data
        player_id : INT : the player's MLBAM ID. Find this by calling pybaseball.playerid_lookup(last_name, first_name), 
            finding the correct player, and selecting their key_mlbam.
    """
    start_dt, end_dt, _ = sanitize_input(start_dt, end_dt, player_id)
    
    # sanitize_input will guarantee these are not None
    assert start_dt
    assert end_dt
    assert player_id

    url = 'https://baseballsavant.mlb.com/statcast_search/csv?all=true&hfPT=&hfAB=&hfBBT=&hfPR=&hfZ=&stadium=&hfBBL=&hfNewZones=&hfGT=R%7CPO%7CS%7C=&hfSea=&hfSit=&player_type=batter&hfOuts=&opponent=&pitcher_throws=&batter_stands=&hfSA=&game_date_gt={}&game_date_lt={}&batters_lookup%5B%5D={}&team=&position=&hfRO=&home_road=&hfFlag=&metric_1=&hfInn=&min_pitches=0&min_results=0&group_by=name&sort_col=pitches&player_event_sort=h_launch_speed&sort_order=desc&min_abs=0&type=details&'
    df = split_request(start_dt, end_dt, player_id, url)
    return df

@cache.df_cache()
def statcast_batter_exitvelo_barrels(year: int, minBBE: Union[int, str] = "q") -> pd.DataFrame:
    """
    Retrieves batted ball data for all batters in a given year.

    ARGUMENTS
        year: The year for which you wish to retrieve batted ball data. Format: YYYY.
        minBBE: The minimum number of batted ball events for each player. If a player falls 
            below this threshold, they will be excluded from the results. If no value is specified, 
            only qualified batters will be returned.
    """
    url = f"https://baseballsavant.mlb.com/leaderboard/statcast?type=batter&year={year}&position=&team=&min={minBBE}&csv=true"
    res = requests.get(url, timeout=None).content
    data = pd.read_csv(io.StringIO(res.decode('utf-8')))
    data = sanitize_statcast_columns(data)
    return data

@cache.df_cache()
def statcast_batter_expected_stats(year: int, minPA: Union[int, str] = "q") -> pd.DataFrame:
    """
    Retrieves expected stats based on quality of batted ball contact in a given year.

    ARGUMENTS
        year: The year for which you wish to retrieve expected stats data. Format: YYYY.
        minPA: The minimum number of plate appearances for each player. If a player falls below this threshold, 
            they will be excluded from the results. If no value is specified, only qualified batters will be returned.
    """
    url = f"https://baseballsavant.mlb.com/leaderboard/expected_statistics?type=batter&year={year}&position=&team=&min={minPA}&csv=true"
    res = requests.get(url, timeout=None).content
    data = pd.read_csv(io.StringIO(res.decode('utf-8')))
    data = sanitize_statcast_columns(data)
    return data

@cache.df_cache()
def statcast_batter_percentile_ranks(year: int) -> pd.DataFrame:
    """
    Retrieves percentile ranks for each player in a given year, including batters with at least 2.1 PA per team 
    game and 1.25 for pitchers.

    ARGUMENTS
        year: The year for which you wish to retrieve percentile data. Format: YYYY.
    """
    url = f"https://baseballsavant.mlb.com/leaderboard/percentile-rankings?type=batter&year={year}&position=&team=&csv=true"
    res = requests.get(url, timeout=None).content
    data = pd.read_csv(io.StringIO(res.decode('utf-8')))
    # URL returns a null player with player id 999999, which we want to drop
    return data.loc[data.player_name.notna()].reset_index(drop=True)

@cache.df_cache()
def statcast_batter_pitch_arsenal(year: int, minPA: int = 25) -> pd.DataFrame:
    """
    Retrieves outcome data for batters split by the pitch type in a given year.

    ARGUMENTS
        year: The year for which you wish to retrieve pitch arsenal data. Format: YYYY.
        minPA: The minimum number of plate appearances for each player. If a player falls below this threshold, 
            they will be excluded from the results. If no value is specified, the default number of plate appearances is 25.
    """
    url = f"https://baseballsavant.mlb.com/leaderboard/pitch-arsenal-stats?type=batter&pitchType=&year={year}&team=&min={minPA}&csv=true"
    res = requests.get(url, timeout=None).content
    data = pd.read_csv(io.StringIO(res.decode('utf-8')))
    data = sanitize_statcast_columns(data)
    return data
