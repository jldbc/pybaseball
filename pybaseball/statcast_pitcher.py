from typing import Optional

import pandas as pd

from pybaseball.utils import sanitize_input, split_request


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
