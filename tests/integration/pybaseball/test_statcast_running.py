import pandas as pd

from pybaseball.statcast_running import (
	statcast_sprint_speed,
	statcast_running_splits
)
	
def test_statcast_sprint_speed() -> None:
	min_opp = 10
	result: pd.DataFrame = statcast_sprint_speed(2019, min_opp)

	assert result is not None
	assert not result.empty

	assert len(result.columns) == 11
	assert len(result) > 0
	assert len(result.loc[result.competitive_runs < min_opp]) == 0

def test_statcast_running_splits() -> None:
	min_opp = 5
	raw_splits = True
	result: pd.DataFrame = statcast_running_splits(2019, min_opp, raw_splits)

	assert result is not None
	assert not result.empty

	assert len(result.columns) == 27
	assert len(result) > 0
