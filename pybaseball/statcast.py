import datetime
import io
import warnings

import numpy as np
import pandas as pd
import requests

import pybaseball.datasources.statcast as statcast_ds

_SC_SINGLE_GAME_REQUEST = "/statcast_search/csv?all=true&type=details&game_pk={game_pk}"
_SC_SMALL_REQUEST = "/statcast_search/csv?all=true&hfPT=&hfAB=&hfBBT=&hfPR=&hfZ=&stadium=&hfBBL=&hfNewZones=&hfGT=R%7CPO%7CS%7C=&hfSea=&hfSit=&player_type=pitcher&hfOuts=&opponent=&pitcher_throws=&batter_stands=&hfSA=&game_date_gt={start_dt}&game_date_lt={end_dt}&team={team}&position=&hfRO=&home_road=&hfFlag=&metric_1=&hfInn=&min_pitches=0&min_results=0&group_by=name&sort_col=pitches&player_event_sort=h_launch_speed&sort_order=desc&min_abs=0&type=details&"

def validate_datestring(date_text):
    try:
        datetime.datetime.strptime(date_text, '%Y-%m-%d')
    except ValueError:
        raise ValueError("Incorrect data format, should be YYYY-MM-DD")

def sanitize_input(start_dt, end_dt):
    # If no dates are supplied, assume they want yesterday's data
    # send a warning in case they wanted to specify
    if start_dt is None and end_dt is None:
        today = datetime.datetime.today()
        start_dt = (today - datetime.timedelta(1)).strftime("%Y-%m-%d")
        end_dt = today.strftime("%Y-%m-%d")
        print(
            "Warning: no date range supplied. Returning yesterday's Statcast data. For a different date range, try get_statcast(start_dt, end_dt)."
        )
    
    # If only one date is supplied, assume they only want that day's stats
    # query in this case is from date 1 to date 1
    if start_dt is None:
        start_dt = end_dt
    if end_dt is None:
        end_dt = start_dt
    
    # Now that both dates are not None, make sure they are valid date strings
    validate_datestring(start_dt)
    validate_datestring(end_dt)
    
    return start_dt, end_dt

def small_request(start_dt, end_dt, team: str = None) -> pd.DataFrame:
    data = statcast_ds.get_statcast_data_from_csv_url(
        _SC_SMALL_REQUEST.format(start_dt=start_dt, end_dt=end_dt, team=team if team else '')
    )
    if data is not None and not data.empty:
        data = data.sort_values(
            ['game_date', 'game_pk', 'at_bat_number', 'pitch_number'],
            ascending=False
        )

    return data

def large_request(start_dt, end_dt, d1, d2, step, verbose, team: str = None) -> pd.DataFrame:
    """
    Break start and end date into smaller increments, collecting all data in small chunks
    and appending all results to a common dataframe end_dt is the date strings for the
    final day of the query d1 and d2 are datetime objects for first and last day of query,
    for doing date math a third datetime object (d) will be used to increment over time
    for the several intermediate queries.
    """
    
    # Count failed requests. If > X, break
    error_counter = 0

    # A flag for passing over the success message of requests are failing
    no_success_msg_flag = False
    
    dataframe_list = []

    print("This is a large query, it may take a moment to complete")
    
    # Number of days per mini-query
    # (test this later to see how large I can make this without losing data)

    # While intermediate query end_dt <= global query end_dt, keep looping
    d = d1 + datetime.timedelta(days=step)
    while d <= d2: 
        # Dates before 3/15 and after 11/15 will always be offseason.
        # If these dates are detected, check if the next season is within the user's query.
        # If yes, fast-forward to the next season to avoid empty requests
        # If no, break the loop. all useful data has been pulled.
        if (d.month == 3 and d.day < 15) or d.month <= 2:
            print('Skipping offseason dates')
            d1 = d1.replace(month=3, day=15, year=d1.year)
            d = d1 + datetime.timedelta(days=step+1)
        elif (d1.month == 11 and d1.day > 14) or d1.month > 11:
            if d2.year > d.year:
                print('Skipping offseason dates')
                d1 = d1.replace(month=3, day=15, year=d1.year+1)
                d = d1 + datetime.timedelta(days=step+1)
            else:
                break

        start_dt = d1.strftime('%Y-%m-%d')
        intermediate_end_dt = d.strftime('%Y-%m-%d')
        data = small_request(start_dt, intermediate_end_dt, team=team)
        
        # Append to list of dataframes if not empty or failed
        # (failed requests have one row saying "Error: Query Timeout")
        if data.shape[0] > 1:
            dataframe_list.append(data)
        else:
            # If it failed, retry up to three times
            success = 0
            while success == 0:
                data = small_request(start_dt, intermediate_end_dt, team=team)
                if data.shape[0] > 1:
                    dataframe_list.append(data)
                    success = 1
                else:
                    error_counter += 1
                if error_counter > 2:
                    # This request is probably too large. Cut a day off of this request
                    # and make that its own separate request. For each, append to
                    # dataframe list if successful, skip and print error message if failed.
                    tmp_end = d - datetime.timedelta(days=1)
                    tmp_end = tmp_end.strftime('%Y-%m-%d')
                    smaller_data_1 = small_request(start_dt, tmp_end, team=team)
                    smaller_data_2 = small_request(intermediate_end_dt, intermediate_end_dt, team=team)
                    if smaller_data_1.shape[0] > 1:
                        dataframe_list.append(smaller_data_1)
                        print("Completed sub-query from {} to {}".format(start_dt, tmp_end))
                    else:
                        print("Query unsuccessful for data from {} to {}. Skipping these dates.".format(start_dt, tmp_end))
                    if smaller_data_2.shape[0] > 1:
                        dataframe_list.append(smaller_data_2)
                        print("Completed sub-query from {} to {}".format(intermediate_end_dt, intermediate_end_dt))
                    else:
                        print("Query unsuccessful for data from {} to {}. Skipping these dates.".format(intermediate_end_dt, intermediate_end_dt))

                    # Flag for passing over the success message since this request failed
                    no_success_msg_flag = True
                    
                    # Reset counter
                    error_counter = 0
                    break


        if verbose:
            if no_success_msg_flag is False:
                print("Completed sub-query from {} to {}".format(start_dt, intermediate_end_dt))
            else:
                no_success_msg_flag = False # if failed, reset this flag so message will send again next iteration
        
        # Increment dates
        d1 = d + datetime.timedelta(days=1)
        d = d + datetime.timedelta(days=step+1)

    # If start date > end date after being incremented,
    # the loop captured each date's data
    if d1 > d2:
        pass
    else:
        # If start date <= end date, then there are a few leftover dates to grab data for.
        # start_dt from the earlier loop will work,
        # but instead of d we now want the original end_dt
        start_dt = d1.strftime('%Y-%m-%d')
        data = small_request(start_dt, end_dt, team=team)
        dataframe_list.append(data)
        if verbose:
            print("Completed sub-query from {} to {}".format(start_dt, end_dt))

    # Concatenate all dataframes into final result set
    final_data = pd.concat(dataframe_list, axis=0)
    return final_data


def statcast(start_dt=None, end_dt=None, team=None, verbose=True):
    """
    Pulls statcast play-level data from Baseball Savant for a given date range.

    INPUTS:
    start_dt: YYYY-MM-DD : the first date for which you want statcast data
    end_dt: YYYY-MM-DD : the last date for which you want statcast data
    team: optional (defaults to None) : city abbreviation of the team you want data for (e.g. SEA or BOS)

    If no arguments are provided, this will return yesterday's statcast data. If one date is provided, it will return that date's statcast data.
    """

    start_dt, end_dt = sanitize_input(start_dt, end_dt)
    
    # 5 days or less -> a quick one-shot request.
    # Greater than 5 days -> break it into multiple smaller queries
    small_query_threshold = 5
    
    # Inputs are valid if either both or zero dates are supplied.
    # Not valid if only one given.
    if start_dt and end_dt:
        # How many days worth of data are needed?
        date_format = "%Y-%m-%d"
        d1 = datetime.datetime.strptime(start_dt, date_format)
        d2 = datetime.datetime.strptime(end_dt, date_format)
        days_in_query = (d2 - d1).days
        if days_in_query <= small_query_threshold:
            return small_request(start_dt, end_dt, team=team)
        else:
            return large_request(start_dt, end_dt, d1, d2, step=small_query_threshold, verbose=verbose, team=team)

def statcast_single_game(game_pk):
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
