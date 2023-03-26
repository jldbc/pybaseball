import io
from typing import Optional, Union

import pandas as pd
import requests

from . import cache
from .utils import sanitize_statcast_columns

@cache.df_cache()
def statcast_sprint_speed(year: int, min_opp: int = 10) -> pd.DataFrame:
	"""
	Returns each player's sprint speed for the given year and minimum number of opportunities. Sprint speed is 
	defined as "feet per second in a player’s fastest one-second window" and calculated using approximately the 
	top two-thirds of a player's opportunities.

	ARGUMENTS
		year: The year for which you wish to retrieve batted ball against data. Format: YYYY. 
		min_opp: The minimum number of sprinting opportunities. Statcast considers the following two situations as opportunities:
			Runs of two bases or more on non-homers, excluding being a runner on second base when an extra base hit happens.
			Home to first on “topped” or “weakly hit” balls.
	"""
	url = f"https://baseballsavant.mlb.com/leaderboard/sprint_speed?year={year}&position=&team=&min={min_opp}&csv=true"
	res = requests.get(url, timeout=None).content
	data = pd.read_csv(io.StringIO(res.decode('utf-8')))
	data = sanitize_statcast_columns(data)
	return data

@cache.df_cache()
def statcast_running_splits(year: int, min_opp: int = 5, raw_splits: bool = True) -> pd.DataFrame:
	"""
	Returns each player's 90 feet sprint splits at five foot intervals for the given year and minimum number of opportunities.

	ARGUMENTS
		year: The year for which you wish to retrieve batted ball against data. Format: YYYY. 
		min_opp: The minimum number of sprinting opportunities. Statcast considers the following two situations as opportunities:
			Runs of two bases or more on non-homers, excluding being a runner on second base when an extra base hit happens.
			Home to first on “topped” or “weakly hit” balls. 
		raw_splits: Boolean indicator for if the function returns raw times or percentiles for each split.	
	"""
	split_type = "raw" if raw_splits else "percent"
	url = f"https://baseballsavant.mlb.com/running_splits?type={split_type}&bats=&year={year}&position=&team=&min={min_opp}&csv=true"
	res = requests.get(url, timeout=None).content
	data = pd.read_csv(io.StringIO(res.decode('utf-8')))
	data = sanitize_statcast_columns(data)
	return data

