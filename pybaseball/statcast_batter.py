from pybaseball.utils import sanitize_input, split_request


def statcast_batter(start_dt=None, end_dt=None, player_id=None):
    """
    Pulls statcast pitch-level data from Baseball Savant for a given batter.

    ARGUMENTS
    start_dt : YYYY-MM-DD : the first date for which you want a player's statcast data
    end_dt : YYYY-MM-DD : the final date for which you want data
    player_id : INT : the player's MLBAM ID. Find this by calling pybaseball.playerid_lookup(last_name, first_name), finding the correct player, and selecting their key_mlbam.
    """
    start_dt, end_dt, player_id = sanitize_input(start_dt, end_dt, player_id)
    # inputs are valid if either both or zero dates are supplied. Not valid of only one given.
    if start_dt and end_dt:
        url = 'https://baseballsavant.mlb.com/statcast_search/csv?all=true&hfPT=&hfAB=&hfBBT=&hfPR=&hfZ=&stadium=&hfBBL=&hfNewZones=&hfGT=R%7CPO%7CS%7C=&hfSea=&hfSit=&player_type=batter&hfOuts=&opponent=&pitcher_throws=&batter_stands=&hfSA=&game_date_gt={}&game_date_lt={}&batters_lookup%5B%5D={}&team=&position=&hfRO=&home_road=&hfFlag=&metric_1=&hfInn=&min_pitches=0&min_results=0&group_by=name&sort_col=pitches&player_event_sort=h_launch_speed&sort_order=desc&min_abs=0&type=details&'
        df = split_request(start_dt, end_dt, player_id, url)
        return df
