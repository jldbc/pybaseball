from time import sleep
from typing import Generator

import pytest

from pybaseball import league_pitching_stats, pitching_stats_range
from pybaseball.utils import most_recent_season


@pytest.fixture(autouse=True)
def before_after_each() -> Generator[None, None, None]:
    # before each test
    yield
    # after each test
    sleep(6) # BBRef will throttle us if we make more than 10 calls per minute

def test_get_soup_none_none() -> None:
    result = league_pitching_stats.get_soup(None, None)
    assert result is None


def test_pitching_stats_range_start_dt_lt_2008() -> None:
    with pytest.raises(ValueError):
        league_pitching_stats.pitching_stats_range('2007-01-01', '2019-01-01')


def test_pitching_stats_bref() -> None:
    result = league_pitching_stats.pitching_stats_bref(2019)

    assert result is not None
    assert not result.empty

    assert len(result.columns) == 41
    assert(len(result)) == 831


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


def test_pitching_stats_bref_future() -> None:
    with pytest.raises(IndexError):
        league_pitching_stats.pitching_stats_bref(most_recent_season() + 1)


def test_pitching_stats_range_single_date() -> None:
    stats = pitching_stats_range('2019-05-01',)
    assert not stats.empty
