from datetime import date, timedelta
from typing import List, Optional, Union

import pandas as pd

import pybaseball.datasources.statcast as statcast_ds

from .utils import sanitize_date_range

_SC_SINGLE_GAME_REQUEST = "/statcast_search/csv?all=true&type=details&game_pk={game_pk}"
# pylint: disable=line-too-long
_SC_SMALL_REQUEST = "/statcast_search/csv?all=true&hfPT=&hfAB=&hfBBT=&hfPR=&hfZ=&stadium=&hfBBL=&hfNewZones=&hfGT=R%7CPO%7CS%7C=&hfSea=&hfSit=&player_type=pitcher&hfOuts=&opponent=&pitcher_throws=&batter_stands=&hfSA=&game_date_gt={start_dt}&game_date_lt={end_dt}&team={team}&position=&hfRO=&home_road=&hfFlag=&metric_1=&hfInn=&min_pitches=0&min_results=0&group_by=name&sort_col=pitches&player_event_sort=h_launch_speed&sort_order=desc&min_abs=0&type=details&"
_MAX_SC_RESULTS = 40000


def _chunk_small_request(start_date: date, end_date: date, team: Optional[str], verbose: bool,
                         max_retries: int = 3) -> Optional[pd.DataFrame]:
    data = small_request(start_date, end_date, team=team, verbose=verbose)

    # Append to list of dataframes if not empty or failed
    # (failed requests have one row saying "Error: Query Timeout")
    if not data.empty:
        if verbose:
            print(f"Completed sub-query from {start_date} to {end_date} ({len(data)} results)")
        return data

    # If it failed, retry up to three times
    retry_success = False

    # Count failed requests. If > 2, break
    error_counter = 0

    dataframe_list: List[pd.DataFrame] = []
    while not retry_success:
        data = small_request(start_date, end_date, team=team, verbose=verbose)

        if not data.empty:
            if verbose:
                print(f"Completed sub-query from {start_date} to {end_date} ({len(data)} results)")
            return data

        error_counter += 1

        if error_counter < max_retries:
            continue

        # This request is probably too large. Cut a day off of this request
        # and make that its own separate request. For each, append to
        # dataframe list if successful, skip and print error message if failed.
        if end_date > start_date:
            tmp_end = end_date - timedelta(days=1)
            smaller_data_1 = small_request(start_date, tmp_end, team=team, verbose=verbose)
            smaller_data_2 = small_request(end_date, end_date, team=team, verbose=verbose)

            if smaller_data_1 is not None and not smaller_data_1.empty:
                dataframe_list.append(smaller_data_1)
                if verbose:
                    print(f"Completed sub-query from {start_date} to {tmp_end} ({len(smaller_data_1)} results)")
                retry_success = True
            else:
                print(f"Query unsuccessful for data from {end_date} to {tmp_end}. Skipping these dates.")

            if smaller_data_2 is not None and not smaller_data_2.empty:
                dataframe_list.append(smaller_data_2)
                if verbose:
                    print(f"Completed sub-query from {end_date} to {end_date} ({len(smaller_data_2)} results)")
                retry_success = True
            else:
                print(f"Query unsuccessful for data from {end_date} to {end_date}. Skipping these dates.")

            # Reset counter
            error_counter = 0
            break

    if dataframe_list:
        return pd.concat(dataframe_list, axis=0)

    return None


def small_request(start_dt: date, end_dt: date, team: Optional[str] = None, verbose: bool = False) -> pd.DataFrame:
    data = statcast_ds.get_statcast_data_from_csv_url(
        _SC_SMALL_REQUEST.format(start_dt=str(start_dt), end_dt=str(end_dt), team=team if team else '')
    )
    if data is not None and not data.empty:
        if len(data) == _MAX_SC_RESULTS:
            if verbose:
                print('Query completed, but got the maximum number of results. Breaking it down to ensure consistency.')
            day_span = (end_dt - start_dt).days
            sub_chunk_1 = small_request(start_dt, start_dt + timedelta(days=day_span // 2), team=team, verbose=verbose)
            if verbose and sub_chunk_1 is not None and not sub_chunk_1.empty:
                print(
                    f"Completed sub-query from {start_dt} to {start_dt + timedelta(days = day_span // 2)} ({len(sub_chunk_1)} results)"
                )
            sub_chunk_2 = small_request(
                start_dt + timedelta(days=day_span // 2 + 1),
                end_dt,
                team=team,
                verbose=verbose
            )
            if verbose and sub_chunk_2 is not None and not sub_chunk_2.empty:
                print(
                    f"Completed sub-query from {start_dt + timedelta(days = day_span // 2 + 1)} to {end_dt} ({len(sub_chunk_2)} results)"
                )
            data = pd.concat([sub_chunk_1, sub_chunk_2], axis=0)
        data = data.sort_values(
            ['game_date', 'game_pk', 'at_bat_number', 'pitch_number'],
            ascending=False
        )

    return data


def large_request(start_date: date, end_date: date, step: int, verbose: bool,
                  team: Optional[str] = None) -> pd.DataFrame:
    """
    Break start and end date into smaller increments, collecting all data in small chunks
    and appending all results to a common dataframe start_date_date and end_date_date
    are date objects for first and last day of query, for doing date math a third date
    object (d) will be used to increment over time for the several intermediate queries.
    """

    dataframe_list = []

    subq_start = start_date

    if verbose:
        print("This is a large query, it may take a moment to complete")

    # While intermediate query end_dt <= global query end_dt, keep looping
    subq_end = subq_start + timedelta(days=step)
    while subq_end <= end_date:
        # Dates before 3/15 and after 11/15 will always be offseason.
        # If these dates are detected, check if the next season is within the user's query.
        # If yes, fast-forward to the next season to avoid empty requests
        # If no, break the loop. all useful data has been pulled.
        if (subq_end.month == 3 and subq_end.day < 15) or subq_end.month <= 2:
            if verbose:
                print('Skipping offseason dates')
            subq_start = subq_start.replace(month=3, day=15)
            subq_end = subq_start + timedelta(days=step+1)
        elif (subq_start.month == 11 and subq_start.day > 14) or subq_start.month > 11:
            if end_date.year > subq_end.year:
                if verbose:
                    print('Skipping offseason dates')
                subq_start = subq_start.replace(month=3, day=15, year=subq_start.year+1)
                subq_end = subq_start + timedelta(days=step+1)
            else:
                break

        data = _chunk_small_request(subq_start, subq_end, team=team, verbose=verbose)

        # Append to list of dataframes if not empty or failed
        # (failed requests have one row saying "Error: Query Timeout")
        if data is not None and not data.empty:
            dataframe_list.append(data)

        # Increment dates
        subq_start = subq_end + timedelta(days=1)
        subq_end = subq_end + timedelta(days=step+1)

    # If start date > end date after being incremented,
    # the loop captured each date's data
    if subq_start <= end_date:
        # If start date <= end date, then there are a few leftover dates to grab data for.
        # start_dt from the earlier loop will work,
        # but instead of d we now want the original end_dt
        data = small_request(subq_start, end_date, team=team, verbose=verbose)
        dataframe_list.append(data)
        if verbose:
            print(f"Completed sub-query from {subq_start} to {end_date} ({len(data)} results)")

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
    # Greater than small_query_threshold days -> break it into multiple smaller queries
    # The reason 7 is chosen here is because statcast will return at most 40000 rows.
    # 7 seems to be the largest number of days that will guarantee no dropped rows.
    small_query_threshold = 7

    # How many days worth of data are needed?
    days_in_query = (end_dt_date - start_dt_date).days
    if days_in_query <= small_query_threshold:
        return small_request(start_dt_date, end_dt_date, team=team, verbose=verbose)

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
