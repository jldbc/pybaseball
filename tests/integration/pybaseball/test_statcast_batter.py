import pandas as pd

from tests.conftest import CURRENT_SC_COLUMNS

from pybaseball.statcast_batter import (
    statcast_batter,
    statcast_batter_exitvelo_barrels,
    statcast_batter_expected_stats,
    statcast_batter_percentile_ranks,
    statcast_batter_pitch_arsenal,
    statcast_batter_bat_tracking
)


def test_statcast_batter_exitvelo_barrels() -> None:
    min_bbe = 250
    result: pd.DataFrame = statcast_batter_exitvelo_barrels(2019, min_bbe)

    assert result is not None
    assert not result.empty

    assert len(result.columns) == 18
    assert len(result) > 0
    assert len(result[result['attempts'] < min_bbe]) == 0


def test_statcast_batter() -> None:
    result: pd.DataFrame = statcast_batter('2019-01-01', '2019-12-31', 642715)

    assert result is not None
    assert not result.empty

    assert len(result.columns) == CURRENT_SC_COLUMNS
    assert len(result) > 0

def test_statcast_batter_multiple_seasons() -> None:
    result: pd.DataFrame = statcast_batter('2023-04-01', '2024-10-01', 656941)

    assert result is not None
    assert not result.empty

    assert len(result.columns) == CURRENT_SC_COLUMNS
    assert len(result) > 0

def test_statcast_batter_expected_stats() -> None:
    min_pa = 250
    result: pd.DataFrame = statcast_batter_expected_stats(2019, min_pa)

    assert result is not None
    assert not result.empty

    assert len(result.columns) == 14
    assert len(result) > 0
    assert len(result[result['pa'] < min_pa]) == 0

def test_statcast_batter_percentile_ranks() -> None:
    result: pd.DataFrame = statcast_batter_percentile_ranks(2019)

    assert result is not None
    assert not result.empty

    assert len(result.columns) == 23
    assert len(result) > 0

def test_statcast_batter_pitch_arsenal() -> None:
    min_pa = 25
    result: pd.DataFrame = statcast_batter_pitch_arsenal(2019, min_pa)

    assert result is not None
    assert not result.empty

    assert len(result.columns) == 20
    assert len(result) > 0
    assert len(result[result['pa'] < min_pa]) == 0
def test_statcast_batter_bat_tracking() -> None:
    min_pa = 25
    result: pd.DataFrame = statcast_batter_bat_tracking(2024, min_pa)

    assert result is not None
    assert not result.empty

    assert len(result.columns) == 18
    assert len(result) > 0
    assert len(result[result['swings_competitive'] < min_pa]) == 0
