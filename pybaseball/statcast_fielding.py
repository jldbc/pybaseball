import io
from typing import Union

import pandas as pd
import requests

from . import cache
from .utils import norm_positions, sanitize_statcast_columns

@cache.df_cache()
def statcast_outs_above_average(year: int, pos: Union[int, str], min_att: Union[int, str] = "q", view: str = "Fielder") -> pd.DataFrame:
	"""Scrapes outs above average from baseball savant for a given year and position

	Args:
		year (int): Season to pull
		pos (Union[int, str]): Numerical position (e.g. 3 for 1B, 4 for 2B). Catchers not supported
		min_att (Union[int, str], optional): Integer number of attempts required or "q" for qualified. 
			Defaults to "q".
		view (str, optional): Perspective of defensive metrics. String argument supports "Fielder", "Pitcher", "Fielding_Team", "Batter", and "Batting_Team"
			Defaults to "Fielder"

	Raises:
		ValueError: Failure if catcher is passed

	Returns:
		pd.DataFrame: Dataframe of defensive OAA for the given year and position for players who have met
			the given threshold
	"""
	pos = norm_positions(pos)
	# catcher is not included in this leaderboard
	if pos == "2":
		raise ValueError("This particular leaderboard does not include catchers!")
	url = f"https://baseballsavant.mlb.com/leaderboard/outs_above_average?type={view}&year={year}&team=&range=year&min={min_att}&pos={pos}&roles=&viz=show&csv=true"
	res = requests.get(url, timeout=None).content
	data = pd.read_csv(io.StringIO(res.decode('utf-8')))
	data = sanitize_statcast_columns(data)
	return data

@cache.df_cache()
def statcast_outfield_directional_oaa(year: int, min_opp: Union[int, str] = "q") -> pd.DataFrame:
	"""
	Retrieves outfielders' directional OAA data for the given year and number of opportunities. The directions are 
	Back Left, Back, Back Right, In Left, In, and In Right.

	ARGUMENTS
		year: The year for which you wish to retrieve batted ball against data. Format: YYYY. 
		min_opp: The minimum number of opportunities for the player to be included in the result. Statcast's 
		default is players with at least 1 fielding attempt per game.
	"""
	url = f"https://baseballsavant.mlb.com/directional_outs_above_average?year={year}&min={min_opp}&team=&csv=true"
	res = requests.get(url, timeout=None).content
	data = pd.read_csv(io.StringIO(res.decode('utf-8')))
	data = sanitize_statcast_columns(data)
	return data

@cache.df_cache()
def statcast_outfield_catch_prob(year: int, min_opp: Union[int, str] = "q") -> pd.DataFrame:
	"""
	Retrieves aggregated data for outfielder performance on fielding attempt types, binned into five star categories, 
	for the given year and number of opportunities.

	ARGUMENTS
		year: The year for which you wish to retrieve batted ball against data. Format: YYYY. 
		min_opp: The minimum number of opportunities for the player to be included in the result. Statcast's 
		default is players with at least 1 fielding attempt per game.
	"""
	url = f"https://baseballsavant.mlb.com/leaderboard/catch_probability?type=player&min={min_opp}&year={year}&total=&csv=true"
	res = requests.get(url, timeout=None).content
	data = pd.read_csv(io.StringIO(res.decode('utf-8')))
	data = sanitize_statcast_columns(data)
	return data

@cache.df_cache()
def statcast_outfielder_jump(year: int, min_att: Union[int, str] = "q") -> pd.DataFrame:
	"""
	Retrieves data on outfielder's jump to the ball for the given year and number of attempts. Jump is calculated 
	only for two star or harder plays (90% or less catch probabiility).

	ARGUMENTS
		year: The year for which you wish to retrieve batted ball against data. Format: YYYY. 
		min_att: The minimum number of attempts for the player to be included in the result. Statcast's default 
			is players with at least 2 two star or harder fielding attempts per team game / 5.
	"""
	url = f"https://baseballsavant.mlb.com/leaderboard/outfield_jump?year={year}&min={min_att}&csv=true"
	res = requests.get(url, timeout=None).content
	data = pd.read_csv(io.StringIO(res.decode('utf-8')))
	data = sanitize_statcast_columns(data)
	return data

@cache.df_cache()
def statcast_catcher_poptime(year: int, min_2b_att: int = 5, min_3b_att: int = 0) -> pd.DataFrame:
	"""
	Retrieves pop time data for catchers given year and minimum stolen base attempts for second and third base. 
	Pop time is measured as the time from the moment the ball hits the catcher's mitt to when it reaches the projected 
	receiving point at the center of the fielder's base.

	ARGUMENTS
		year: The year for which you wish to retrieve batted ball against data. Format: YYYY. 
		min_2b_att: The minimum number of stolen base attempts for second base against the catcher. Statcast's default is 5. 
		min_3b_att: The minimum number of stolen base attempts for third base against the catcher. Statcast's default is 0.
	"""
	# currently no 2020 data
	url = f"https://baseballsavant.mlb.com/leaderboard/poptime?year={year}&team=&min2b={min_2b_att}&min3b={min_3b_att}&csv=true"
	res = requests.get(url, timeout=None).content
	data = pd.read_csv(io.StringIO(res.decode('utf-8')))
	return data

@cache.df_cache()
def statcast_catcher_framing(year: int, min_called_p: Union[int, str] = "q") -> pd.DataFrame:
	"""
	Retrieves the catcher's framing results for the given year and minimum called pitches. It uses eight zones around 
	the strike zone (aka "shadow zone") and gives the percentage of time the catcher gets the strike called in each zone.

	ARGUMENTS
		year: The year for which you wish to retrieve batted ball against data. Format: YYYY. 
		min_called_p: The minimum number of called pitches for the catcher in the shadow zone. Statcast's default 
		is players with at least 6 called pitches in the shadow zone per team game.
	"""
	url = f"https://baseballsavant.mlb.com/catcher_framing?year={year}&team=&min={min_called_p}&sort=4,1&csv=true"
	res = requests.get(url, timeout=None).content
	data = pd.read_csv(io.StringIO(res.decode('utf-8')))
	data = sanitize_statcast_columns(data)
	# CSV includes league average player, which we drop from the result
	return data.loc[data.last_name.notna()].reset_index(drop=True)	

