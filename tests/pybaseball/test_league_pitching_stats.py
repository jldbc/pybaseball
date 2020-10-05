from datetime import date, datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest

from pybaseball import league_pitching_stats


def test_get_soup_none_none() -> None:
    result = league_pitching_stats.get_soup(None, None)
    assert result is None


def test_pitching_stats_range_start_dt_lt_2008() -> None:
    with pytest.raises(ValueError):
        league_pitching_stats.pitching_stats_range('2007-01-01', '2019-01-01')


def test_pitching_stats_bref_future() -> None:
    with pytest.raises(IndexError):
        league_pitching_stats.pitching_stats_bref(datetime.today().year + 1)


def test_pitching_stats_bref_bad_year() -> None:
    with pytest.raises(ValueError):
        league_pitching_stats.pitching_stats_bref('NOT A YEAR')


def test_pitching_stats_bref_none() -> None:
    pitching_stats_range_mock =  MagicMock()
    this_year = date.today().year

    with patch('pybaseball.league_pitching_stats.pitching_stats_range', pitching_stats_range_mock):
        league_pitching_stats.pitching_stats_bref(None)

    pitching_stats_range_mock.assert_called_once_with(f'{this_year}-03-01', f"{this_year}-11-01")
