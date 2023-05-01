from collections import namedtuple
from datetime import date, datetime, timedelta
import functools
import io
from typing import Dict, Iterator, Optional, Tuple, Union
import zipfile

import pandas as pd
import requests

from . import cache

DATE_FORMAT = "%Y-%m-%d"

# dictionary containing team abbreviations and their first year in existance
# https://www.baseball-reference.com/teams/
# Nones mean that team only exists as an alias
first_season_map: Dict[str, Optional[int]] = {
    'AB2': 1931, 'AB3': 1938, 'ABC': 1920, 'AC' : 1923, 'AG' : 1933, 'ALT': 1884, 'ANA': 1997, 'ARI': 1998,
    'ATH': 1876, 'ATL': 1966, 'BAG': None, 'BAL': 1954, 'BBB': 1924, 'BBS': 1923, 'BCA': 1932, 'BE' : 1935,
    'BEG': 1938, 'BFB': 1890, 'BFL': None, 'BLA': 1901, 'BLN': 1892, 'BLO': 1882, 'BLT': 1914, 'BLU': 1884,
    'BOS': 1901, 'BR2': 1923, 'BRA': 1872, 'BRD': 1884, 'BRG': 1890, 'BRO': 1884, 'BRS': 1890, 'BSN': 1876,
    'BTT': 1914, 'BUF': 1879, 'BWW': 1890, 'CAG': 1920, 'CAL': 1965, 'CBB': 1933, 'CBE': 1943, 'CBK': 1883,
    'CBL': 1870, 'CBN': 1924, 'CBR': 1939, 'CC' : 1943, 'CCB': 1942, 'CCU': 1931, 'CEG': 1935, 'CEL': 1926,
    'CEN': 1875, 'CG' : 1933, 'CHC': 1876, 'CHH': 1914, 'CHP': 1890, 'CHT': 1927, 'CHW': 1901, 'CIN': 1876,
    'CKK': 1891, 'CL2': 1932, 'CLE': 1901, 'CLI': 1890, 'CLS': 1889, 'CLV': 1887, 'CNR': 1876, 'CNS': 1880,
    'COB': 1921, 'COG': 1920, 'COL': 1883, 'COR': 1884, 'COT': 1932, 'CPI': 1884, 'CRS': 1934, 'CS' : 1921,
    'CSE': 1923, 'CSW': 1920, 'CT' : 1937, 'CTG': 1928, 'CTS': 1922, 'CUP': 1932, 'DET': 1901, 'DM' : 1920,
    'DS' : 1920, 'DTN': 1881, 'DTS': 1937, 'DW' : 1932, 'DYM': 1920, 'ECK': 1872, 'FLA': 1993, 'HAR': 1876,
    'HBG': 1924, 'HG' : 1929, 'HIL': 1923, 'HOU': 1962, 'IA' : 1937, 'IAB': 1939, 'IBL': 1878, 'IC' : 1946,
    'ID' : 1933, 'IHO': 1884, 'IND': 1887, 'JRC': 1938, 'KCA': 1955, 'KCC': 1888, 'KCM': 1920, 'KCN': 1886,
    'KCP': 1914, 'KCR': 1969, 'KCU': 1884, 'KEK': 1871, 'LAA': 1961, 'LAD': 1958, 'LGR': 1876, 'LOU': 1882,
    'LOW': 1931, 'LRG': 1932, 'LVB': 1930, 'MAN': 1872, 'MAR': 1873, 'MB' : 1923, 'MGS': 1932, 'MIA': 2012,
    'MIL': 1884, 'MIN': 1961, 'MLA': 1891, 'MLG': 1878, 'MLN': 1953, 'MLU': 1884, 'MON': 1969, 'MRM': 1932,
    'MRS': 1924, 'NAT': 1872, 'NBY': 1936, 'ND' : 1934, 'NE' : 1936, 'NEG': 1930, 'NEW': 1915, 'NHV': 1875,
    'NLG': 1923, 'NS' : 1926, 'NWB': 1932, 'NYC': 1935, 'NYG': 1883, 'NYI': 1890, 'NYM': 1962, 'NYP': 1883,
    'NYU': 1876, 'NYY': 1903, 'OAK': 1968, 'OLY': 1871, 'PBB': 1890, 'PBG': 1934, 'PBK': 1922, 'PBS': 1914,
    'PC' : 1933, 'PHA': 1882, 'PHI': 1873, 'PHK': 1884, 'PHQ': 1890, 'PIT': 1882, 'PK' : 1922, 'PRO': 1878,
    'PS' : 1934, 'PTG': 1928, 'RES': 1873, 'RIC': 1884, 'ROC': 1890, 'ROK': 1871, 'SBS': 1876, 'SDP': 1969,
    'SEA': 1977, 'SEN': 1938, 'SEP': 1969, 'SFG': 1958, 'SL2': 1937, 'SL3': 1939, 'SLB': 1902, 'SLG': 1920,
    'SLI': 1914, 'SLM': 1884, 'SLR': 1875, 'SLS': 1922, 'SNH': 1938, 'SNS': 1940, 'STL': 1875, 'STP': 1884,
    'SYR': 1879, 'SYS': 1890, 'TBD': 1998, 'TBR': 2008, 'TC' : 1940, 'TC2': 1939, 'TEX': 1972, 'TLM': 1890,
    'TOL': 1884, 'TOR': 1977, 'TRO': 1871, 'TRT': 1879, 'TT' : 1923, 'WAP': 1932, 'WAS': 1884, 'WEG': 1936,
    'WES': 1875, 'WHS': 1892, 'WIL': 1884, 'WMP': 1925, 'WNA': 1884, 'WNL': 1886, 'WOR': 1880, 'WP' : 1924,
    'WSA': 1961, 'WSH': 1901, 'WSN': 2005, 'WST': 1884, 
}

team_equivalents = [
    {'ANA', 'CAL', 'LAA'},
    {'BSN', 'MLN', 'ATL'},
    {'BLO', 'BLN', 'BLT', 'MLA', 'SLB', 'BAL'},
    {'BRD', 'BRS', 'BOS'},
    {'BRO', 'LAD'},
    {'PHA', 'OAK'},
    {'FLA', 'MIA'},
    {'SEP', 'MIL'},
    {'WSH', 'MIN'},
    {'MON', 'WSN'},
    {'NYG', 'SFG'},
    {'TBD', 'TBR'},
    {'BCA', 'IAB'},
    {'AC' , 'BAG'},
    {'BR2', 'BRG'},
    {'NEG', 'CEG', 'WEG', 'BEG'},
    {'CNS', 'CIN'},
    {'CCB', 'CBE'},
    {'CLE', 'CLV'},
    {'CS' , 'CSW'},
    {'AB2', 'ID' },
    {'CC' , 'IC' },
    {'JRC', 'CBR'},
    {'LVB', 'LOW'},
    {'BE' , 'NE' },
    {'PC' , 'TC' , 'TC2'},
    {'PBK', 'PK' },
    {'SLG', 'SLS'},
    # Potenital issue here as HAR is duplicated by BR for both
    # Hartford Dark Blues (NL 1876-1878)
    # Harrisburgh Stars (NNL 1943)
    # These are two distinct teams, but with the same code in BR
    {'AB3', 'SL3', 'SNS', 'HAR'},
    {'WP' , 'WMP'},
    {'WHS', 'WNA'},
    {'WAS', 'WST'}
]

def get_first_season(team: str, include_equivalents: bool = True) -> Optional[int]:
    if not include_equivalents:
        return first_season_map[team]
    
    oldest = first_season_map[team] or date.today().year
    
    equivalents = [x for x in team_equivalents if team in x]

    if not equivalents:
        return oldest

    for equivalent in equivalents[0]:
        equivalent_first = first_season_map[equivalent]
        if equivalent_first is not None and equivalent_first < oldest:
            oldest = equivalent_first
    
    return oldest

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

pitch_codes = ["FF", "CU", "CH", "FC", "EP", "FO", "KN", "KC", "SC", "SI", "SL", "FS", "FT", "ST", "SV", "SIFT", "CUKC", "ALL"] # note: all doesn't work in words, we'll have some special handling
pitch_names = ["4-Seamer", "Curveball", "Changeup", "Cutter", "Eephus", "Forkball", "Knuckleball", "Knuckle-curve", "Screwball", "Sinker", "Slider", "Splitter", "2-Seamer", "Sweeper", "Slurve", "Sinker", "Curveball"]
pitch_names_upper = [p.upper() for p in pitch_names]

# including all the codes to themselves makes this simpler later
pitch_name_to_code_map = dict(zip(pitch_codes + pitch_names_upper, pitch_codes + pitch_codes))
pitch_code_to_name_map = dict(zip(pitch_codes, pitch_names))

# Statcast outs above average positions
position_codes = ["IF", "OF", "C", "1B", "2B", "3B", "SS", "LF", "CF", "RF", "ALL"]
position_names = ["Infield", "Outfield", "Catcher", "First Base", "Second Base", "Third Base", "Shortstop", "Left Field", "Center Field", "Right Field"]
position_names_upper = [p.upper() for p in position_names]

pos_code_to_numbers_map = dict(zip(position_codes[2:10], [str(x) for x in range(2, 10)]))
pos_name_to_code_map = dict(zip(position_codes + position_names_upper, position_codes + position_codes))
pos_code_to_name_map = dict(zip(position_codes, position_names))


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


def sanitize_statcast_columns(df: pd.DataFrame) -> pd.DataFrame:
	'''
	Creates uniform structure in Statcast column names
	Removes leading whitespace in column names
	'''
	df.columns = df.columns.str.strip()
	return df


def sanitize_date_range(start_dt: Optional[str], end_dt: Optional[str]) -> Tuple[date, date]:
	# If no dates are supplied, assume they want yesterday's data
	# send a warning in case they wanted to specify
	if start_dt is None and end_dt is None:
		today = date.today()
		start_dt = str(today - timedelta(1))
		end_dt = str(today)

		print('start_dt', start_dt)
		print('end_dt', end_dt)

		print("Warning: no date range supplied, assuming yesterday's date.")

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
	normed = pitch_name_to_code_map.get(pitch.upper())
	normed = pitch_code_to_name_map.get(normed) if to_word and normed else normed
	if normed is None:
		if pitch.lower() == 'all':
			raise ValueError("'All' is not a valid pitch in this particular context!")
		raise ValueError(f'{pitch} is not a valid pitch!')
	return normed

def norm_positions(pos: Union[int, str], to_word: bool = False, to_number: bool = True) -> str:
	pos_str = str(pos)
	normed: Optional[str] = None
	if pos_str in pos_code_to_numbers_map.values():
		to_number = False
		normed = pos_str
	else:
		normed = pos_name_to_code_map.get(pos_str.upper())
		normed = pos_code_to_name_map.get(normed) if to_word and normed else normed
	if to_number:
		if normed not in ["IF", "OF"]:
			normed = pos_code_to_numbers_map.get(normed) if normed else normed
		if pos_str.lower() == "all":
			normed = ""
	if normed is None:
		raise ValueError(f'{pos} is not a valid position!')
	# lower() ok due to positional numbers being cast as strings when created
	return normed.lower()

