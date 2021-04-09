import io
from typing import Optional, Union

import pandas as pd
import requests

from . import cache
from .utils import norm_positions

@cache.df_cache()
def statcast_outs_above_average(year: int, pos: str, min_att: Union[int, str] = "q") -> pd.DataFrame:
	# a lot of options here. need to handle all the positions. range and split years?
	# can use startYear and endYear for multi year
	pos = norm_positions(pos)
	# catcher is not included in this leaderboard
	if pos == "2":
		raise ValueError("'C' not a valid position in this particular context!")
	url = f"https://baseballsavant.mlb.com/leaderboard/outs_above_average?type=Fielder&year={year}&team=&range=year&min={min_att}&pos={pos}&roles=&viz=show&csv=true"
	res = requests.get(url, timeout=None).content
	data = pd.read_csv(io.StringIO(res.decode('utf-8')))
	return data

@cache.df_cache()
def statcast_outfield_directional_oaa(year: int, min_opp: Union[int, str] = "q") -> pd.DataFrame:
	url = f"https://baseballsavant.mlb.com/directional_outs_above_average?year={year}&min={min_opp}&team=&csv=true"
	res = requests.get(url, timeout=None).content
	data = pd.read_csv(io.StringIO(res.decode('utf-8')))
	return data

@cache.df_cache()
def statcast_outfield_catch_proba(year: int, min_opp: Union[int, str] = "q") -> pd.DataFrame:
	url = f"https://baseballsavant.mlb.com/leaderboard/catch_probability?type=player&min={min_opp}&year={year}&total=&csv=true"
	res = requests.get(url, timeout=None).content
	data = pd.read_csv(io.StringIO(res.decode('utf-8')))
	return data

@cache.df_cache()
def statcast_outfielder_jump(year: int, min_att: Union[int, str] = "q") -> pd.DataFrame:
	url = f"https://baseballsavant.mlb.com/leaderboard/outfield_jump?year={year}&min={min_att}&csv=true"
	res = requests.get(url, timeout=None).content
	data = pd.read_csv(io.StringIO(res.decode('utf-8')))
	return data

@cache.df_cache()
def statcast_catcher_poptime(year: int, min_2b_att: int, min_3b_att: int) -> pd.DataFrame:
	# currently no 2020 data
	url = f"https://baseballsavant.mlb.com/leaderboard/poptime?year={year}&team=&min2b={min_2b_att}&min3b={min_3b_att}&csv=true"
	res = requests.get(url, timeout=None).content
	data = pd.read_csv(io.StringIO(res.decode('utf-8')))
	return data

@cache.df_cache()
def statcast_catcher_framing(year: int, min_called_p: Union[int, str] = "q") -> pd.DataFrame:
	url = f"https://baseballsavant.mlb.com/catcher_framing?year={year}&team=&min={min_called_p}&sort=4,1&csv=true"
	res = requests.get(url, timeout=None).content
	data = pd.read_csv(io.StringIO(res.decode('utf-8')))
	return data	

