import io
from typing import Optional, Union

import pandas as pd
import requests

from . import cache
from .utils import sanitize_statcast_columns

@cache.df_cache()
def statcast_sprint_speed(year: int, min_opp: int = 10) -> pd.DataFrame:
	url = f"https://baseballsavant.mlb.com/leaderboard/sprint_speed?year={year}&position=&team=&min={min_opp}&csv=true"
	res = requests.get(url, timeout=None).content
	data = pd.read_csv(io.StringIO(res.decode('utf-8')))
	data = sanitize_statcast_columns(data)
	return data

@cache.df_cache()
def statcast_running_splits(year: int, min_opp: int = 5, raw_splits: bool = True) -> pd.DataFrame:
	split_type = "raw" if raw_splits else "percent"
	url = f"https://baseballsavant.mlb.com/running_splits?type={split_type}&bats=&year={year}&position=&team=&min={min_opp}&csv=true"
	res = requests.get(url, timeout=None).content
	data = pd.read_csv(io.StringIO(res.decode('utf-8')))
	data = sanitize_statcast_columns(data)
	return data

