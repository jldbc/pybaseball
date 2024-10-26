import pandas as pd

from tests.conftest import CURRENT_SC_COLUMNS

from pybaseball.statcast_pitcher import (
    statcast_pitcher,
    statcast_pitcher_active_spin,
    statcast_pitcher_arsenal_stats,
    statcast_pitcher_exitvelo_barrels,
    statcast_pitcher_expected_stats,
    statcast_pitcher_percentile_ranks,
    statcast_pitcher_pitch_arsenal,
    statcast_pitcher_pitch_movement,
    statcast_pitcher_spin_dir_comp,
    statcast_pitcher_bat_tracking,
    statcast_pitcher_arm_angle
)


def test_statcast_pitcher() -> None:
    result: pd.DataFrame = statcast_pitcher('2019-01-01', '2019-12-31', 605483)

    assert result is not None
    assert not result.empty

    assert len(result.columns) == CURRENT_SC_COLUMNS
    assert len(result) > 0

def test_statcast_pitcher_exitvelo_barrels() -> None:
    min_bbe = 100
    result: pd.DataFrame = statcast_pitcher_exitvelo_barrels(2019, minBBE=min_bbe)

    assert result is not None
    assert not result.empty

    assert len(result.columns) == 18
    assert len(result) > 0
    assert len(result[result['attempts'] < min_bbe]) == 0

def test_statcast_pitchers_expected_stats() -> None:
    min_pa = 100
    result: pd.DataFrame = statcast_pitcher_expected_stats(2019, min_pa)

    assert result is not None
    assert not result.empty

    assert len(result.columns) == 17
    assert len(result) > 0
    assert len(result[result['pa'] < min_pa]) == 0

def test_statcast_pitcher_pitch_arsenal() -> None:
    min_p = 250
    result: pd.DataFrame = statcast_pitcher_pitch_arsenal(2019, min_p)

    assert result is not None
    assert not result.empty

    assert len(result.columns) == 12
    assert len(result) > 0

def test_statcast_pitcher_arsenal_stats() -> None:
    min_pa = 25
    result: pd.DataFrame = statcast_pitcher_arsenal_stats(2019, min_pa)

    assert result is not None
    assert not result.empty

    assert len(result.columns) == 20
    assert len(result) > 0
    assert len(result[result['pa'] < min_pa]) == 0

def test_statcast_pitcher_pitch_movement() -> None:
    min_p = 250
    result: pd.DataFrame = statcast_pitcher_pitch_movement(2019, min_p)

    assert result is not None
    assert not result.empty

    assert len(result.columns) == 24
    assert len(result) > 0
    assert len(result[result['pitches_thrown'] < min_p]) == 0

def test_statcast_pitcher_active_spin() -> None:
    min_p = 250
    result: pd.DataFrame = statcast_pitcher_active_spin(2019, min_p)

    assert result is not None
    assert not result.empty

    assert len(result.columns) == 11
    assert len(result) > 0

def test_statcast_pitcher_percentile_ranks() -> None:
    result: pd.DataFrame = statcast_pitcher_percentile_ranks(2019)

    assert result is not None
    assert not result.empty

    assert len(result.columns) == 22
    assert len(result) > 0

def test_statcast_pitcher_spin_dir_comp() -> None:
    result: pd.DataFrame = statcast_pitcher_spin_dir_comp(2020)

    assert result is not None
    assert not result.empty

    assert len(result.columns) == 29
    assert len(result) > 100
def test_statcast_pitcher_bat_tracking() -> None:
    result: pd.DataFrame = statcast_pitcher_bat_tracking(2024)

    assert result is not None
    assert not result.empty

    assert len(result.columns) == 18
    assert len(result) > 0
def test_statcast_pitcher_arm_angle() -> None:
    result: pd.DataFrame = statcast_pitcher_arm_angle(2024)

    assert result is not None
    assert not result.empty

    assert len(result.columns) == 11
    assert len(result) > 0
