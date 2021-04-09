import pandas as pd

from pybaseball.statcast_fielding import (
	statcast_outs_above_average,
	statcast_outfield_directional_oaa,
	statcast_outfield_catch_proba,
	statcast_outfielder_jump,
	statcast_catcher_poptime,
	statcast_catcher_framing
)

def test_statcast_outs_above_average() -> None:
	min_att = 50
	pos = "of"
	result: pd.DataFrame = statcast_outs_above_average(2019, pos, min_att)

	assert result is not None
	assert not result.empty

def test_statcast_outfield_directional_oaa() -> None:
	min_opp = 50
	result: pd.DataFrame = statcast_outfield_directional_oaa(2019, min_opp)

	assert result is not None
	assert not result.empty

def test_statcast_outfield_catch_proba() -> None:
	min_opp = 25
	result: pd.DataFrame = statcast_outfield_catch_proba(2019, min_opp)

	assert result is not None
	assert not result.empty

def test_statcast_outfielder_jump() -> None:		
	min_att = 50
	result: pd.DataFrame = statcast_outfielder_jump(2019, min_att)
	
	assert result is not None
	assert not result.empty

def test_statcast_catcher_poptime() -> None:
	min_2b_att = 5
	min_3b_att = 0
	result: pd.DataFrame = statcast_catcher_poptime(2019, min_2b_att, min_3b_att) -> pd.DataFrame:

	assert result is not None
	assert not result.empty

def test_statcast_catcher_framing() -> None:
	min_called_p = 100
	result: pd.DataFrame = statcast_catcher_framing(2019, min_called_p)

	assert result is not None
	assert not result.empty
