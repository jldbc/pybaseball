from datetime import date, timedelta
from typing import List, Optional, Union
import warnings

import pandas as pd

import pybaseball.datasources.statcast as statcast_ds

from .utils import sanitize_date_range, date_range
from . import cache

_SC_SINGLE_GAME_REQUEST = "/statcast_search/csv?all=true&type=details&game_pk={game_pk}"
# pylint: disable=line-too-long
_SC_SMALL_REQUEST = "/statcast_search/csv?all=true&hfPT=&hfAB=&hfBBT=&hfPR=&hfZ=&stadium=&hfBBL=&hfNewZones=&hfGT=R%7CPO%7CS%7C=&hfSea=&hfSit=&player_type=pitcher&hfOuts=&opponent=&pitcher_throws=&batter_stands=&hfSA=&game_date_gt={start_dt}&game_date_lt={end_dt}&team={team}&position=&hfRO=&home_road=&hfFlag=&metric_1=&hfInn=&min_pitches=0&min_results=0&group_by=name&sort_col=pitches&player_event_sort=h_launch_speed&sort_order=desc&min_abs=0&type=details&"
_MAX_SC_RESULTS = 40000

@cache.df_cache(expires=365)
def small_request(start_dt: date, end_dt: date, team: Optional[str] = None, verbose: bool = False) -> pd.DataFrame:
    data = statcast_ds.get_statcast_data_from_csv_url(
        _SC_SMALL_REQUEST.format(start_dt=str(start_dt), end_dt=str(end_dt), team=team if team else '')
    )
    if data is not None and not data.empty:
        data = data.sort_values(
            ['game_date', 'game_pk', 'at_bat_number', 'pitch_number'],
            ascending=False
        )
        if verbose:
            print(f"Completed sub-query from {start_dt} to {end_dt} ({len(data)} results)")
        

    return data

def check_warning(start_dt: date, end_dt: date) -> None:
    if not cache.config.enabled and (end_dt - start_dt).days >= 42:
        warnings.warn(
            '''That's a nice request you got there. It'd be a shame if something were to happen to it.
            We strongly recommend that you enable caching before running this. It's as simple as `pybaseball.cache.enable()`.
            Since the Statcast requests can take a really long time to run, if something happens, like a disconnect,
            gremlins, electronic interference from banging on metal trash cans, etc., you could lose a lot of progress. Enabling
            caching will allow you to immediately recover all the successful subqueries in such an event.''')


def large_request(start_dt: date, end_dt: date, step: int, verbose: bool,
                  team: Optional[str] = None) -> pd.DataFrame:
    """
    Fulfill the request in sensible increments.
    """

    check_warning(start_dt, end_dt)

    dataframe_list = []

    if verbose:
        print("This is a large query, it may take a moment to complete")

    for subq_start, subq_end in date_range(start_dt, end_dt, step, verbose):
        data = small_request(subq_start, subq_end, team=team, verbose=verbose)

        # Append to list of dataframes if not empty or failed
        # (failed requests have one row saying "Error: Query Timeout")
        if data is not None and not data.empty:
            dataframe_list.append(data)

    # Concatenate all dataframes into final result set
    if dataframe_list:
        final_data = pd.concat(dataframe_list, axis=0).convert_dtypes(convert_string=False)
    else:
        final_data = pd.DataFrame()
    return final_data


def statcast(start_dt: str = None, end_dt: str = None, team: str = None, verbose: bool = True) -> pd.DataFrame:
    """
    Pulls statcast play-level data from Baseball Savant for a given date range.

    INPUTS:
    start_dt: YYYY-MM-DD : the first date for which you want statcast data
    end_dt: YYYY-MM-DD : the last date for which you want statcast data
    team: optional (defaults to None) : city abbreviation of the team you want data for (e.g. SEA or BOS)

    If no arguments are provided, this will return yesterday's statcast data.
    If one date is provided, it will return that date's statcast data.
    """

    start_dt_date, end_dt_date = sanitize_date_range(start_dt, end_dt)

    # small_query_threshold days or less -> a quick one-shot request.
    # this is handled by the iterator in large_request just doing the one thingy otherwise.
    # Greater than small_query_threshold days -> break it into multiple smaller queries
    # The reason 7 is chosen here is because statcast will return at most 40000 rows.
    # 7 seems to be the largest number of days that will guarantee no dropped rows.
    small_query_threshold = 7

    return large_request(start_dt_date, end_dt_date, step=small_query_threshold, verbose=verbose, team=team)


def statcast_single_game(game_pk: Union[str, int]) -> pd.DataFrame:
    """
    Pulls statcast play-level data from Baseball Savant for a single game,
    identified by its MLB game ID (game_pk in statcast data)

    INPUTS:
    game_pk : 6-digit integer MLB game ID to retrieve
    """

    data = statcast_ds.get_statcast_data_from_csv_url(
        _SC_SINGLE_GAME_REQUEST.format(game_pk=game_pk)
    )

    return data.sort_values(
        ['game_date', 'game_pk', 'at_bat_number', 'pitch_number'],
        ascending=False
    )
