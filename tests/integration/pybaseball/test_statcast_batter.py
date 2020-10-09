import pandas as pd

from pybaseball.statcast_batter import statcast_batter, statcast_batter_exitvelo_barrels


def test_statcast_batter_exitvelo_barrels() -> None:
    result: pd.DataFrame = statcast_batter_exitvelo_barrels(2019)

    assert result is not None
    assert not result.empty

    assert len(result.columns) == 19
    assert len(result) == 250

def test_statcast_batter() -> None:
    result: pd.DataFrame = statcast_batter('2019-01-01', '2019-12-31', 642715)

    assert result is not None
    assert not result.empty

    assert len(result.columns) == 89
    assert len(result) == 2418
