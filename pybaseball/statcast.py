import concurrent.futures
import warnings
from datetime import date
from typing import Optional, Union

import pandas as pd
from tqdm import tqdm

import pybaseball.datasources.statcast as statcast_ds

from . import cache
from .utils import sanitize_date_range, statcast_date_range

_SC_SINGLE_GAME_REQUEST = "/statcast_search/csv?all=true&type=details&game_pk={game_pk}"
# pylint: disable=line-too-long
_SC_SMALL_REQUEST = "/statcast_search/csv?all=true&hfPT=&hfAB=&hfBBT=&hfPR=&hfZ=&stadium=&hfBBL=&hfNewZones=&hfGT=R%7CPO%7CS%7C=&hfSea=&hfSit=&player_type=pitcher&hfOuts=&opponent=&pitcher_throws=&batter_stands=&hfSA=&game_date_gt={start_dt}&game_date_lt={end_dt}&team={team}&position=&hfRO=&home_road=&hfFlag=&metric_1=&hfInn=&min_pitches=0&min_results=0&group_by=name&sort_col=pitches&player_event_sort=h_launch_speed&sort_order=desc&min_abs=0&type=details&"
# _MAX_SC_RESULTS = 40000

class StatcastException(Exception):
    pass

@cache.df_cache(expires=365)
def _small_request(start_dt: date, end_dt: date, team: Optional[str] = None) -> pd.DataFrame:
    data = statcast_ds.get_statcast_data_from_csv_url(
        _SC_SMALL_REQUEST.format(start_dt=str(start_dt), end_dt=str(end_dt), team=team if team else '')
    )
    if data is not None and not data.empty:
        if 'error' in data.columns:
            raise StatcastException(data['error'].values[0])

        data = data.sort_values(
            ['game_date', 'game_pk', 'at_bat_number', 'pitch_number'],
            ascending=False
        )

    return data


_OVERSIZE_WARNING = '''
That's a nice request you got there. It'd be a shame if something were to happen to it.
We strongly recommend that you enable caching before running this. It's as simple as `pybaseball.cache.enable()`.
Since the Statcast requests can take a *really* long time to run, if something were to happen, like: a disconnect;
gremlins; computer repair by associates of Rudy Giuliani; electromagnetic interference from metal trash cans; etc.;
you could lose a lot of progress. Enabling caching will allow you to immediately recover all the successful
subqueries if that happens.'''


def _check_warning(start_dt: date, end_dt: date) -> None:
    if not cache.config.enabled and (end_dt - start_dt).days >= 42:
        warnings.warn(_OVERSIZE_WARNING)


def _handle_request(start_dt: date, end_dt: date, step: int, verbose: bool,
                    team: Optional[str] = None, parallel: bool = True) -> pd.DataFrame:
    """
    Fulfill the request in sensible increments.
    """

    _check_warning(start_dt, end_dt)

    if verbose:
        print("This is a large query, it may take a moment to complete", flush=True)

    dataframe_list = []
    date_range = list(statcast_date_range(start_dt, end_dt, step, verbose))

    with tqdm(total=len(date_range)) as progress:
        if parallel:
            # Use ThreadPoolExecutor over ProcessPoolExecutor because ProcessPoolExecutor doesn't work with
            # notebooks and python command line due to the fact it won't have a `__main__` module.
            # See https://docs.python.org/3.7/library/concurrent.futures.html#processpoolexecutor
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = {executor.submit(_small_request, subq_start, subq_end, team=team)
                        for subq_start, subq_end in date_range}
                for future in concurrent.futures.as_completed(futures):
                    dataframe_list.append(future.result())
                    progress.update(1)
        else:
            for subq_start, subq_end in date_range:
                dataframe_list.append(_small_request(subq_start, subq_end, team=team))
                progress.update(1)

    # Concatenate all dataframes into final result set
    if dataframe_list:
        final_data = pd.concat(dataframe_list, axis=0).convert_dtypes(convert_string=False)
        final_data = final_data.sort_values(
            ['game_date', 'game_pk', 'at_bat_number', 'pitch_number'],
            ascending=False
        )
    else:
        final_data = pd.DataFrame()
    return final_data


def statcast(start_dt: str = None, end_dt: str = None, team: str = None,
             verbose: bool = True, parallel: bool = True) -> pd.DataFrame:
    """
    Pulls statcast play-level data from Baseball Savant for a given date range.

    INPUTS:
    start_dt: YYYY-MM-DD : the first date for which you want statcast data
    end_dt: YYYY-MM-DD : the last date for which you want statcast data
    team: optional (defaults to None) : city abbreviation of the team you want data for (e.g. SEA or BOS)
    verbose: bool (defaults to True) : whether to print updates on query progress
    parallel: bool (defaults to True) : whether to parallelize HTTP requests in large queries

    If no arguments are provided, this will return yesterday's statcast data.
    If one date is provided, it will return that date's statcast data.
    """

    start_dt_date, end_dt_date = sanitize_date_range(start_dt, end_dt)

    return _handle_request(start_dt_date, end_dt_date, 1, verbose=verbose,
                           team=team, parallel=parallel)


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

    if data is None or data.empty:
        return None

    if 'error' in data.columns:
        raise StatcastException(data['error'].values[0])

    return data.sort_values(
        ['game_date', 'game_pk', 'at_bat_number', 'pitch_number'],
        ascending=False
    )
