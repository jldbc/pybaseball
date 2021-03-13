import functools
import io
import zipfile
from collections import namedtuple
from datetime import date, datetime, timedelta
from typing import Iterator, Optional, Tuple

import pandas as pd
import requests

from . import cache

DATE_FORMAT = "%Y-%m-%d"

# dictionary containing team abbreviations and their first year in existance
first_season_map = {'ALT': 1884, 'ANA': 1997, 'ARI': 1998, 'ATH': 1871,
                    'ATL': 1966, 'BAL': 1872, 'BLA': 1901, 'BLN': 1892,
                    'BLU': 1884, 'BOS': 1871, 'BRA': 1872, 'BRG': 1890,
                    'BRO': 1884, 'BSN': 1876, 'BTT': 1914, 'BUF': 1879,
                    'BWW': 1890, 'CAL': 1965, 'CEN': 1875, 'CHC': 1876,
                    'CHI': 1871, 'CHW': 1901, 'CIN': 1876, 'CKK': 1891,
                    'CLE': 1871, 'CLV': 1879, 'COL': 1883, 'COR': 1884,
                    'CPI': 1884, 'DET': 1901, 'DTN': 1881, 'ECK': 1872,
                    'FLA': 1993, 'HAR': 1874, 'HOU': 1962, 'IND': 1878,
                    'KCA': 1955, 'KCC': 1884, 'KCN': 1886, 'KCP': 1914,
                    'KCR': 1969, 'KEK': 1871, 'LAA': 1961, 'LAD': 1958,
                    'LOU': 1876, 'MAN': 1872, 'MAR': 1873, 'MIA': 2012,
                    'MIL': 1884, 'MIN': 1961, 'MLA': 1901, 'MLG': 1878,
                    'MLN': 1953, 'MON': 1969, 'NAT': 1872, 'NEW': 1915,
                    'NHV': 1875, 'NYG': 1883, 'NYI': 1890, 'NYM': 1962,
                    'NYP': 1883, 'NYU': 1871, 'NYY': 1903, 'OAK': 1968,
                    'OLY': 1871, 'PBB': 1890, 'PBS': 1914, 'PHA': 1882,
                    'PHI': 1873, 'PHK': 1884, 'PHQ': 1890, 'PIT': 1882,
                    'PRO': 1878, 'RES': 1873, 'RIC': 1884, 'ROC': 1890,
                    'ROK': 1871, 'SDP': 1969, 'SEA': 1977, 'SEP': 1969,
                    'SFG': 1958, 'SLB': 1902, 'SLM': 1884, 'SLR': 1875,
                    'STL': 1875, 'STP': 1884, 'SYR': 1879, 'TBD': 1998,
                    'TBR': 2008, 'TEX': 1972, 'TOL': 1884, 'TOR': 1977,
                    'TRO': 1871, 'WAS': 1873, 'WES': 1875, 'WHS': 1884,
                    'WIL': 1884, 'WOR': 1880, 'WSA': 1961, 'WSH': 1901,
                    'WSN': 2005}

STATCAST_VALID_DATES = {
    2008: (date(2008, 3, 25), date(2008, 10, 27)),
    2009: (date(2009, 4, 5), date(2009, 11, 4)),
    2010: (date(2010, 4, 4), date(2010, 11, 1)),
    2011: (date(2011, 3, 31), date(2011, 10, 28)),
    2012: (date(2012, 3, 28), date(2012, 10, 28)),
    2013: (date(2013, 3, 31), date(2013, 10, 30)),
    2014: (date(2014, 3, 22), date(2014, 10, 29)),
    2015: (date(2015, 4, 5), date(2015, 11, 1)),
    2016: (date(2016, 4, 3), date(2016, 11, 2)),
    2017: (date(2017, 4, 2), date(2017, 11, 1)),
    2018: (date(2018, 3, 29), date(2018, 10, 28)),
    2019: (date(2019, 3, 20), date(2019, 10, 30)),
    2020: (date(2020, 7, 23), date(2020, 10, 27))
}

pitch_codes = ["FF", "SIFT", "CH", "CUKC", "FC", "SL", "FS", "ALL"] # note: all doesn't work in words, we'll have some special handling
pitch_names = ["4-Seamer", "Sinker", "Changeup", "Curveball", "Cutter", "Slider", "Sinker"]
pitch_names_upper = [p.upper() for p in pitch_names]

# including all the codes to themselves makes this simpler later
name_to_code_map = dict(zip(pitch_codes + pitch_names_upper, pitch_codes + pitch_codes))
code_to_name_map = dict(zip(pitch_codes, pitch_names))


def validate_datestring(date_text: Optional[str]) -> date:
    try:
        assert date_text
        return datetime.strptime(date_text, DATE_FORMAT).date()
    except (AssertionError, ValueError) as ex:
        raise ValueError("Incorrect data format, should be YYYY-MM-DD") from ex


@functools.lru_cache()
def most_recent_season() -> int:
    '''
    Find the most recent season.

    Will be either this year (if the season has started or just ended)
    or last year (if the season has not yet started).
    '''

    # Get the past year of season dates
    recent_season_dates = date_range(
        (datetime.today() - timedelta(weeks=52)).date(),  # From one year ago
        datetime.today().date(),  # To today
        verbose=False,
    )

    # Grab the last entry as the most recent game date, the year of which is the most recent season
    return list(recent_season_dates)[-1][0].year


def date_range(start: date, stop: date, step: int = 1, verbose: bool = True) -> Iterator[Tuple[date, date]]:
    '''
    Iterate over dates. Skip the offseason dates. Returns a pair of dates for beginning and end of each segment.
    Range is inclusive of the stop date.
    If verbose is enabled, it will print a message if it skips offseason dates.
    '''

    low = start

    while low <= stop:
        if (low.month, low.day) < (3, 15):
            low = low.replace(month=3, day=15)
            if verbose:
                print('Skipping offseason dates')
        elif (low.month, low.day) > (11, 15):
            low = low.replace(month=3, day=15, year=low.year + 1)
            if verbose:
                print('Skipping offseason dates')

        if low > stop:
            return
        high = min(low + timedelta(step - 1), stop)
        yield low, high
        low += timedelta(days=step)


def statcast_date_range(start: date, stop: date, step: int, verbose: bool = True) -> Iterator[Tuple[date, date]]:
    '''
    Iterate over dates. Skip the offseason dates. Returns a pair of dates for beginning and end of each segment.
    Range is inclusive of the stop date.
    If verbose is enabled, it will print a message if it skips offseason dates.
    This version is Statcast specific, relying on skipping predefined dates from STATCAST_VALID_DATES.
    '''
    low = start

    while low <= stop:
        date_span = low.replace(month=3, day=15), low.replace(month=11, day=15)
        season_start, season_end = STATCAST_VALID_DATES.get(low.year, date_span)
        if low < season_start:
            low = season_start
            if verbose:
                print('Skipping offseason dates')
        elif low > season_end:
            low, _ = STATCAST_VALID_DATES.get(low.year + 1, (date(month=3, day=15, year=low.year + 1), None))
            if verbose:
                print('Skipping offseason dates')

        if low > stop:
            return
        high = min(low + timedelta(step - 1), stop)
        yield low, high
        low += timedelta(days=step)


def sanitize_date_range(start_dt: Optional[str], end_dt: Optional[str]) -> Tuple[date, date]:
    # If no dates are supplied, assume they want yesterday's data
    # send a warning in case they wanted to specify
    if start_dt is None and end_dt is None:
        today = date.today()
        start_dt = str(today - timedelta(1))
        end_dt = str(today)

        print('start_dt', start_dt)
        print('end_dt', end_dt)

        print(
            "Warning: no date range supplied. Returning yesterday's Statcast data. For a different date range, "
            "try get_statcast(start_dt, end_dt)."
        )

    # If only one date is supplied, assume they only want that day's stats
    # query in this case is from date 1 to date 1
    if start_dt is None:
        start_dt = end_dt
    if end_dt is None:
        end_dt = start_dt

    start_dt_date = validate_datestring(start_dt)
    end_dt_date = validate_datestring(end_dt)

    # If end date occurs before start date, swap them
    if end_dt_date < start_dt_date:
        start_dt_date, end_dt_date = end_dt_date, start_dt_date

    # Now that both dates are not None, make sure they are valid date strings
    return start_dt_date, end_dt_date


def sanitize_input(start_dt: Optional[str], end_dt: Optional[str], player_id: Optional[int]) -> Tuple[str, str, str]:
    # error if no player ID provided
    if player_id is None:
        raise ValueError(
            "Player ID is required. If you need to find a player's id, try "
            "pybaseball.playerid_lookup(last_name, first_name) and use their key_mlbam. "
            "If you want statcast data for all players, try the statcast() function."
        )
    # this id should be a string to place inside a url
    player_id_str = str(player_id)
    start_dt_date, end_dt_date = sanitize_date_range(start_dt, end_dt)
    return str(start_dt_date), str(end_dt_date), player_id_str


@cache.df_cache()
def split_request(start_dt: str, end_dt: str, player_id: int, url: str) -> pd.DataFrame:
    """
    Splits Statcast queries to avoid request timeouts
    """
    current_dt = datetime.strptime(start_dt, '%Y-%m-%d')
    end_dt_datetime = datetime.strptime(end_dt, '%Y-%m-%d')
    results = []  # list to hold data as it is returned
    player_id_str = str(player_id)
    print('Gathering Player Data')
    # break query into multiple requests
    while current_dt <= end_dt_datetime:
        remaining = end_dt_datetime - current_dt
        # increment date ranges by at most 60 days
        delta = min(remaining, timedelta(days=2190))
        next_dt = current_dt + delta
        start_str = current_dt.strftime('%Y-%m-%d')
        end_str = next_dt.strftime('%Y-%m-%d')
        # retrieve data
        data = requests.get(url.format(start_str, end_str, player_id_str))
        df = pd.read_csv(io.StringIO(data.text))
        # add data to list and increment current dates
        results.append(df)
        current_dt = next_dt + timedelta(days=1)
    return pd.concat(results)


def get_zip_file(url: str) -> zipfile.ZipFile:
    """
    Get zip file from provided URL
    """
    with requests.get(url, stream=True) as file_stream:
        zip_file = zipfile.ZipFile(io.BytesIO(file_stream.content))
    return zip_file


def get_text_file(url: str) -> str:
    """
    Get raw github file from provided URL
    """

    with requests.get(url, stream=True) as file_stream:
        text = file_stream.text

    return text


def flag_imputed_data(statcast_df: pd.DataFrame) -> pd.DataFrame:
    """Function to flag possibly imputed data as a result of no-nulls approach (see: https://tht.fangraphs.com/43416-2/)
       For derivation of values see pybaseball/EXAMPLES/imputed_derivation.ipynb
       Note that this imputation only occured with TrackMan, not present in Hawk-Eye data (beyond 2020)
    Args:
        statcast_df (pd.DataFrame): Dataframe loaded via statcast.py, statcast_batter.py, or statcast_pitcher.py
    Returns:
        pd.DataFrame: Copy of original dataframe with "possible_imputation" flag
    """

    ParameterSet = namedtuple('ParameterSet', ["ev", "angle", "bb_type"])
    impute_combinations = []

    # pop-ups
    impute_combinations.append(ParameterSet(ev=80.0, angle=69.0, bb_type="popup"))

    # Flyout
    impute_combinations.append(ParameterSet(ev=89.2, angle=39.0, bb_type="fly_ball"))
    impute_combinations.append(ParameterSet(ev=102.8, angle=30.0, bb_type="fly_ball"))

    # Line Drive
    impute_combinations.append(ParameterSet(ev=90.4, angle=15.0, bb_type="line_drive"))
    impute_combinations.append(ParameterSet(ev=91.1, angle=18.0, bb_type="line_drive"))

    # Ground balls
    impute_combinations.append(ParameterSet(ev=82.9, angle=-21.0, bb_type="ground_ball"))
    impute_combinations.append(ParameterSet(ev=90.3, angle=-17.0, bb_type="ground_ball"))

    df_imputations = pd.DataFrame(data=impute_combinations)
    df_imputations["possible_imputation"] = True
    df_return = statcast_df.merge(df_imputations, how="left",
                                  left_on=["launch_speed", "launch_angle", "bb_type"],
                                  right_on=["ev", "angle", "bb_type"])
    # Change NaNs to false for boolean consistency
    df_return["possible_imputation"] = df_return["possible_imputation"].fillna(False)
    df_return = df_return.drop(["ev", "angle"], axis=1)
    return df_return

def norm_pitch_code(pitch: str, to_word: bool = False) -> str:
    normed = name_to_code_map.get(pitch.upper())
    normed = code_to_name_map.get(normed) if to_word else normed
    if normed is None:
        if pitch.lower() is 'all':
            raise ValueError("'All' is not a valid pitch in this particular context!")
        raise ValueError(f'{pitch} is not a valid pitch!')
    return normed