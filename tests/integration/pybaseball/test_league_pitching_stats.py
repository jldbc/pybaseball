from datetime import datetime

import pytest

from pybaseball import league_pitching_stats


def test_pitching_stats_bref() -> None:
    result = league_pitching_stats.pitching_stats_bref(2019)

    assert result is not None
    assert not result.empty

    assert len(result.columns) == 40
    assert(len(result)) == 831


def test_pitching_stats_bref_none() -> None:
    result = league_pitching_stats.pitching_stats_bref(None)

    assert result is not None
    assert not result.empty

    assert len(result.columns) == 40
    assert(len(result)) == 729


def test_pitching_stats_bref_future() -> None:
    with pytest.raises(IndexError):
        league_pitching_stats.pitching_stats_bref(datetime.today().year + 1)


def test_bwar_pitch() -> None:
    result = league_pitching_stats.bwar_pitch()

    assert result is not None
    assert not result.empty

    bwar_pitch_2019 = result.query('year_ID == 2019')

    assert len(bwar_pitch_2019.columns) == 19
    assert(len(bwar_pitch_2019)) == 938


def test_bwar_pitch_return_all() -> None:
    result = league_pitching_stats.bwar_pitch(return_all=True)

    assert result is not None
    assert not result.empty

    bwar_pitch_2019 = result.query('year_ID == 2019')

    assert len(bwar_pitch_2019.columns) == 43
    assert(len(bwar_pitch_2019)) == 938
