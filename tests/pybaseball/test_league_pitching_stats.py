from unittest.mock import MagicMock, patch

import pytest

from pybaseball import league_pitching_stats
from pybaseball.utils import most_recent_season


def test_get_soup_none_none() -> None:
    result = league_pitching_stats.get_soup(None, None)
    assert result is None


def test_pitching_stats_range_start_dt_lt_2008() -> None:
    with pytest.raises(ValueError):
        league_pitching_stats.pitching_stats_range('2007-01-01', '2019-01-01')


def test_pitching_stats_bref_bad_year() -> None:
    with pytest.raises(ValueError):
        league_pitching_stats.pitching_stats_bref('NOT A YEAR')


def test_pitching_stats_bref_none() -> None:
    pitching_stats_range_mock =  MagicMock()
    this_year = most_recent_season()

    with patch('pybaseball.league_pitching_stats.pitching_stats_range', pitching_stats_range_mock):
        league_pitching_stats.pitching_stats_bref(None)

    pitching_stats_range_mock.assert_called_once_with(f'{this_year}-03-01', f"{this_year}-11-01")
