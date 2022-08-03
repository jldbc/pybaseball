import io
from typing import Optional, Union
import warnings

import pandas as pd
import requests

from . import cache
from .utils import norm_pitch_code, sanitize_input, split_request, sanitize_statcast_columns


def statcast_pitcher(start_dt: Optional[str] = None, end_dt: Optional[str] = None, player_id: Optional[int] = None) -> pd.DataFrame:
    """
    Pulls statcast pitch-level data from Baseball Savant for a given pitcher.

    ARGUMENTS
    start_dt : YYYY-MM-DD : the first date for which you want a player's statcast data
    end_dt : YYYY-MM-DD : the final date for which you want data
    player_id : INT : the player's MLBAM ID. Find this by calling pybaseball.playerid_lookup(last_name, first_name), finding the correct player, and selecting their key_mlbam.
    """
    sanitize_input(start_dt, end_dt, player_id)

    # sanitize_input will guarantee these are not None
    assert start_dt
    assert end_dt
    assert player_id

    url = 'https://baseballsavant.mlb.com/statcast_search/csv?all=true&hfPT=&hfAB=&hfBBT=&hfPR=&hfZ=&stadium=&hfBBL=&hfNewZones=&hfGT=R%7CPO%7CS%7C=&hfSea=&hfSit=&player_type=pitcher&hfOuts=&opponent=&pitcher_throws=&batter_stands=&hfSA=&game_date_gt={}&game_date_lt={}&pitchers_lookup%5B%5D={}&team=&position=&hfRO=&home_road=&hfFlag=&metric_1=&hfInn=&min_pitches=0&min_results=0&group_by=name&sort_col=pitches&player_event_sort=h_launch_speed&sort_order=desc&min_abs=0&type=details&'
    df = split_request(start_dt, end_dt, player_id, url)

    return df

@cache.df_cache()
def statcast_pitcher_exitvelo_barrels(year: int, minBBE: Union[int, str] = "q") -> pd.DataFrame:
    url = f"https://baseballsavant.mlb.com/leaderboard/statcast?type=pitcher&year={year}&position=&team=&min={minBBE}&csv=true"
    res = requests.get(url, timeout=None).content
    data = pd.read_csv(io.StringIO(res.decode('utf-8')))
    data = sanitize_statcast_columns(data)
    return data

@cache.df_cache()
def statcast_pitcher_expected_stats(year: int, minPA: Union[int, str] = "q") -> pd.DataFrame:
    url = f"https://baseballsavant.mlb.com/leaderboard/expected_statistics?type=pitcher&year={year}&position=&team=&min={minPA}&csv=true"
    res = requests.get(url, timeout=None).content
    data = pd.read_csv(io.StringIO(res.decode('utf-8')))
    data = sanitize_statcast_columns(data)
    return data

@cache.df_cache()
def statcast_pitcher_pitch_arsenal(year: int, minP: int = 250, arsenal_type: str = "avg_speed") -> pd.DataFrame:
    arsenals = ["avg_speed", "n_", "avg_spin"]
    if arsenal_type not in arsenals:
        raise ValueError(f"Not a valid arsenal_type. Must be one of {', '.join(arsenals)}.")
    url = f"https://baseballsavant.mlb.com/leaderboard/pitch-arsenals?year={year}&min={minP}&type={arsenal_type}&hand=&csv=true"
    res = requests.get(url, timeout=None).content
    data = pd.read_csv(io.StringIO(res.decode('utf-8')))
    data = sanitize_statcast_columns(data)
    return data

@cache.df_cache()
def statcast_pitcher_arsenal_stats(year: int, minPA: int = 25) -> pd.DataFrame:
    # test to see if pitch types needs to be implemented or if user can subset on their own
    url = f"https://baseballsavant.mlb.com/leaderboard/pitch-arsenal-stats?type=pitcher&pitchType=&year={year}&team=&min={minPA}&csv=true"
    res = requests.get(url, timeout=None).content
    data = pd.read_csv(io.StringIO(res.decode('utf-8')))
    data = sanitize_statcast_columns(data)
    return data

@cache.df_cache()
def statcast_pitcher_pitch_movement(year: int, minP: Union[int, str] = "q", pitch_type: str = "FF") -> pd.DataFrame:
    pitch_type = norm_pitch_code(pitch_type)
    url = f"https://baseballsavant.mlb.com/leaderboard/pitch-movement?year={year}&team=&min={minP}&pitch_type={pitch_type}&hand=&x=pitcher_break_x_hidden&z=pitcher_break_z_hidden&csv=true"
    res = requests.get(url, timeout=None).content
    data = pd.read_csv(io.StringIO(res.decode('utf-8')))
    data = sanitize_statcast_columns(data)
    return data

@cache.df_cache()
def statcast_pitcher_active_spin(year: int, minP: int = 250, _type: str = 'spin-based') -> pd.DataFrame:
    # Statcast supports spin-based for some years, but not others. We'll try to get that first, but if it's empty
    # we'll fall back to the observed. 
    #
    # From Statcast:
    #   Measured active spin uses the 3D spin vector at release; this is only possible with the 2020 season going
    #   forward. (Label is "2020 - Spin-based" and can be read as "Active Spin using the Spin-based method".)
    #   Inferred active spin from movement uses the total amount of movement to estimate the amount of active spin,
    #   if we presumed only magnus was at play; this is a legacy method that can be useful in certain circumstances.
    #   (Label is "2020 - Observed" and can be read as "Active Spin using the Total Observed Movement method".)


    url = f"https://baseballsavant.mlb.com/leaderboard/active-spin?year={year}_{_type}&min={minP}&hand=&csv=true"
    res = requests.get(url, timeout=None).content
    if res and '<html' in res.decode('utf-8'):
        # This did no go as planned. Statcast redirected us back to HTML :(
        if _type == 'spin-based':
            warnings.warn(f'Could not get active spin results for year {year} that are "spin-based". Trying to get the older "observed" results.')
            return statcast_pitcher_active_spin(year, minP, 'observed')
        
        warnings.warn("Statcast did not return any active spin results for the query provided.")
        return pd.DataFrame()

    data = pd.read_csv(io.StringIO(res.decode('utf-8')))
    if _type == 'spin-based' and (data is None or data.empty):
        return statcast_pitcher_active_spin(year, minP, 'observed')

    data = sanitize_statcast_columns(data)
    return data

@cache.df_cache()
def statcast_pitcher_percentile_ranks(year: int) -> pd.DataFrame:
    url = f"https://baseballsavant.mlb.com/leaderboard/percentile-rankings?type=pitcher&year={year}&position=&team=&csv=true"
    res = requests.get(url, timeout=None).content
    data = pd.read_csv(io.StringIO(res.decode('utf-8')))
    # URL returns a null player with player id 999999, which we want to drop
    return data.loc[data.player_name.notna()].reset_index(drop=True)

@cache.df_cache()
def statcast_pitcher_spin_dir_comp(year: int, pitch_a: str = "FF", pitch_b: str = "CH", minP: int = 100, pitcher_pov: bool = True) -> pd.DataFrame:
    pitch_a = norm_pitch_code(pitch_a, to_word=True)
    pitch_b = norm_pitch_code(pitch_b, to_word=True)
    pov = "Pit" if pitcher_pov else "Bat"
    url = f"https://baseballsavant.mlb.com/leaderboard/spin-direction-comparison?year={year}&type={pitch_a} / {pitch_b}&min={minP}&team=&pov={pov}&sort=11&sortDir=asc&csv=true"
    res = requests.get(url, timeout=None).content
    data = pd.read_csv(io.StringIO(res.decode('utf-8')))
    data = sanitize_statcast_columns(data)
    return data    
