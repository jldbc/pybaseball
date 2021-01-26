from unittest.mock import MagicMock, patch

import pytest

from pybaseball import league_batting_stats
from pybaseball.utils import most_recent_season


def test_batting_stats_range_start_dt_lt_2008() -> None:
    with pytest.raises(ValueError):
        league_batting_stats.batting_stats_range('2007-01-01', '2019-01-01')


def test_batting_stats_bref_none() -> None:
    batting_stats_range_mock =  MagicMock()
    this_year = most_recent_season()

    with patch('pybaseball.league_batting_stats.batting_stats_range', batting_stats_range_mock):
        league_batting_stats.batting_stats_bref(None)

    batting_stats_range_mock.assert_called_once_with(f'{this_year}-03-01', f"{this_year}-11-01")
