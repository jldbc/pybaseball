from datetime import date, timedelta, datetime
import io
import warnings
from typing import Optional, Tuple, Union

import numpy as np
import pandas as pd
import requests

from .datahelpers import caching
from .datasources import statcast as statcast_ds

from .utils import sanitize_date_range

_SC_SINGLE_GAME_REQUEST = "/statcast_search/csv?all=true&type=details&game_pk={game_pk}"
_SC_SMALL_REQUEST = "/statcast_search/csv?all=true&hfPT=&hfAB=&hfBBT=&hfPR=&hfZ=&stadium=&hfBBL=&hfNewZones=&hfGT=R%7CPO%7CS%7C=&hfSea=&hfSit=&player_type=pitcher&hfOuts=&opponent=&pitcher_throws=&batter_stands=&hfSA=&game_date_gt={start_dt}&game_date_lt={end_dt}&team={team}&position=&hfRO=&home_road=&hfFlag=&metric_1=&hfInn=&min_pitches=0&min_results=0&group_by=name&sort_col=pitches&player_event_sort=h_launch_speed&sort_order=desc&min_abs=0&type=details&"


def small_request(start_dt: date, end_dt: date, team: Optional[str] = None) -> pd.DataFrame:
    data = statcast_ds.get_statcast_data_from_csv_url(
        _SC_SMALL_REQUEST.format(start_dt=str(start_dt), end_dt=str(end_dt), team=team if team else '')
    )
    if data is not None and not data.empty:
        data = data.sort_values(
            ['game_date', 'game_pk', 'at_bat_number', 'pitch_number'],
            ascending=False
        )

    return data

def large_request(start_dt_date: date, end_dt_date: date, step: int, verbose: bool,
                  team: Optional[str] = None) -> pd.DataFrame:
    """
    Break start and end date into smaller increments, collecting all data in small chunks
    and appending all results to a common dataframe start_date_date and end_date_date
    are date objects for first and last day of query, for doing date math a third date
    object (d) will be used to increment over time for the several intermediate queries.
    """

    # Count failed requests. If > X, break
    error_counter = 0

    # A flag for passing over the success message of requests are failing
    no_success_msg_flag = False

    dataframe_list = []

    d1 = start_dt_date
    d2 = end_dt_date

    print("This is a large query, it may take a moment to complete")

    # Number of days per mini-query
    # (test this later to see how large I can make this without losing data)

    # While intermediate query end_dt <= global query end_dt, keep looping
    d = d1 + timedelta(days=step)
    while d <= d2: 
        # Dates before 3/15 and after 11/15 will always be offseason.
        # If these dates are detected, check if the next season is within the user's query.
        # If yes, fast-forward to the next season to avoid empty requests
        # If no, break the loop. all useful data has been pulled.
        if (d.month == 3 and d.day < 15) or d.month <= 2:
            print('Skipping offseason dates')
            d1 = d1.replace(month=3, day=15, year=d1.year)
            d = d1 + timedelta(days=step+1)
        elif (d1.month == 11 and d1.day > 14) or d1.month > 11:
            if d2.year > d.year:
                print('Skipping offseason dates')
                d1 = d1.replace(month=3, day=15, year=d1.year+1)
                d = d1 + timedelta(days=step+1)
            else:
                break

        data = small_request(d1, d, team=team)
        
        # Append to list of dataframes if not empty or failed
        # (failed requests have one row saying "Error: Query Timeout")
        if data.shape[0] > 1:
            dataframe_list.append(data)
        else:
            # If it failed, retry up to three times
            success = 0
            while success == 0:
                data = small_request(d1, d, team=team)
                if data.shape[0] > 1:
                    dataframe_list.append(data)
                    success = 1
                else:
                    error_counter += 1
                if error_counter > 2:
                    # This request is probably too large. Cut a day off of this request
                    # and make that its own separate request. For each, append to
                    # dataframe list if successful, skip and print error message if failed.
                    tmp_end = d - timedelta(days=1)
                    smaller_data_1 = small_request(d1, tmp_end, team=team)
                    smaller_data_2 = small_request(d, d, team=team)
                    if smaller_data_1.shape[0] > 1:
                        dataframe_list.append(smaller_data_1)
                        print(f"Completed sub-query from {d1} to {tmp_end}")
                    else:
                        print(f"Query unsuccessful for data from {d} to {tmp_end}. Skipping these dates.")
                    if smaller_data_2.shape[0] > 1:
                        dataframe_list.append(smaller_data_2)
                        print(f"Completed sub-query from {d} to {d}")
                    else:
                        print(f"Query unsuccessful for data from {d} to {d}. Skipping these dates.")

                    # Flag for passing over the success message since this request failed
                    no_success_msg_flag = True

                    # Reset counter
                    error_counter = 0
                    break


        if verbose:
            if no_success_msg_flag is False:
                print(f"Completed sub-query from {d1} to {d}")
            else:
                no_success_msg_flag = False # if failed, reset this flag so message will send again next iteration

        # Increment dates
        d1 = d + timedelta(days=1)
        d = d + timedelta(days=step+1)

    # If start date > end date after being incremented,
    # the loop captured each date's data
    if d1 > d2:
        pass
    else:
        # If start date <= end date, then there are a few leftover dates to grab data for.
        # start_dt from the earlier loop will work,
        # but instead of d we now want the original end_dt
        data = small_request(d1, end_dt_date, team=team)
        dataframe_list.append(data)
        if verbose:
            print(f"Completed sub-query from {d1} to {end_dt_date}")

    # Concatenate all dataframes into final result set
    final_data = pd.concat(dataframe_list, axis=0)
    return final_data


def statcast(start_dt: str = None, end_dt: str = None, team: str = None, verbose: bool = True) -> pd.DataFrame:
    """
    Pulls statcast play-level data from Baseball Savant for a given date range.

    INPUTS:
    start_dt: YYYY-MM-DD : the first date for which you want statcast data
    end_dt: YYYY-MM-DD : the last date for which you want statcast data
    team: optional (defaults to None) : city abbreviation of the team you want data for (e.g. SEA or BOS)

    If no arguments are provided, this will return yesterday's statcast data. If one date is provided, it will return that date's statcast data.
    """

    start_dt_date, end_dt_date = sanitize_date_range(start_dt, end_dt)

    # 5 days or less -> a quick one-shot request.
    # Greater than 5 days -> break it into multiple smaller queries
    small_query_threshold = 5

    # How many days worth of data are needed?
    days_in_query = (end_dt_date - start_dt_date).days
    if days_in_query <= small_query_threshold:
        return small_request(start_dt_date, end_dt_date, team=team)
    else:
        return large_request(start_dt_date, end_dt_date, step=small_query_threshold, verbose=verbose, team=team)

def statcast_single_game(game_pk: Union[str, int]) -> pd.DataFrame:
    """
    Pulls statcast play-level data from Baseball Savant for a single game,
    identified by its MLB game ID (game_pk in statcast data)

    INPUTS:
    game_pk : 6-digit integer MLB game ID to retrieve
    """

    return statcast_ds.get_statcast_data_from_csv_url(
        _SC_SINGLE_GAME_REQUEST.format(game_pk=game_pk)
    ).sort_values(
        ['game_date', 'game_pk', 'at_bat_number', 'pitch_number'],
        ascending=False
    )
