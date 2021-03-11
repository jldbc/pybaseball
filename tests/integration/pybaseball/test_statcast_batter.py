import pandas as pd

from pybaseball.statcast_batter import (
    statcast_batter,
    statcast_batter_exitvelo_barrels,
    statcast_batter_expected_stats,
    statcast_batter_percentile_ranks,
    statcast_batter_pitch_arsenal
)


def test_statcast_batter_exitvelo_barrels() -> None:
    min_bbe = 250
    result: pd.DataFrame = statcast_batter_exitvelo_barrels(2019, min_bbe)

    assert result is not None
    assert not result.empty

    assert len(result.columns) == 19
    assert len(result) > 0
    assert len(result[result['attempts'] < min_bbe]) == 0


def test_statcast_batter() -> None:
    result: pd.DataFrame = statcast_batter('2019-01-01', '2019-12-31', 642715)

    assert result is not None
    assert not result.empty

    assert len(result.columns) == 89
    assert len(result) == 2418

def test_statcast_batter_expected_stats() -> None:
    min_pa = 250
    result: pd.DataFrame = statcast_batter_expected_stats(2019, min_pa)

    assert result is not None
    assert not result.empty

    assert len(result.columns) == 15
    assert len(result) > 0
    assert len(result[result['pa'] < min_pa]) == 0

def test_statcast_batter_percentile_ranks() -> None:
    result: pd.DataFrame = statcast_batter_percentile_ranks(2019)

    assert result is not None
    assert not result.empty

    assert len(result.columns) == 17
    assert len(result) == 990

def test_statcast_batter_pitch_arsenal() -> None:
    result: pd.DataFrame = statcast_batter_pitch_arsenal(2019)

    assert result is not None
    assert not result.empty

    assert len(result.columns) == 21
    assert len(result) == 2204
