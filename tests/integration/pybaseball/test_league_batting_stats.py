import pytest

from pybaseball import league_batting_stats, batting_stats_range
from pybaseball.utils import most_recent_season


def test_batting_stats_bref() -> None:
    result = league_batting_stats.batting_stats_bref(2019)

    assert result is not None
    assert not result.empty

    assert len(result.columns) == 27
    assert(len(result)) == 991


def test_batting_stats_bref_future() -> None:
    with pytest.raises(IndexError):
        league_batting_stats.batting_stats_bref(most_recent_season() + 1)


def test_batting_stats_bref_bad_year() -> None:
    with pytest.raises(ValueError):
        league_batting_stats.batting_stats_bref('NOT A YEAR')


def test_bwar_bat() -> None:
    result = league_batting_stats.bwar_bat()

    assert result is not None
    assert not result.empty

    bwar_bat_2019 = result.query('year_ID == 2019')

    assert len(bwar_bat_2019.columns) == 17
    assert(len(bwar_bat_2019)) == 1567


def test_bwar_bat_return_all() -> None:
    result = league_batting_stats.bwar_bat(return_all=True)

    assert result is not None
    assert not result.empty

    bwar_bat_2019 = result.query('year_ID == 2019')

    assert len(bwar_bat_2019.columns) == 49
    assert(len(bwar_bat_2019)) == 1567


def test_batting_stats_range_single_date():
    stats = batting_stats_range('2019-05-01', )
    assert not stats.empty


def test_batting_stats_range_parsing_error():
    """This tests the issue with parsing mentioned in
    https://github.com/jldbc/pybaseball/issues/218"""
    stats = batting_stats_range("2021-06-26", "2021-06-26")
    assert len(stats) > 200
