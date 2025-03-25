import unittest
import datetime
from typing import Callable

import pandas as pd
import pytest

from pybaseball.daily_schedule import daily_schedule

@pytest.fixture(name="sample_html")
def _sample_html(get_data_file_contents: Callable[[str], str]) -> str:
    return get_data_file_contents('daily_schedule.html')

def test_batting_stats(response_get_monkeypatch: Callable, sample_html: str):

    response_get_monkeypatch(sample_html)

    # never games in January
    jan = datetime.datetime(2025, 1, 1)

    assert daily_schedule(jan).empty

    # always games on fourth of July
    fourth = datetime.datetime(2025, 7, 4)
    fourth_games = daily_schedule(fourth)

    assert not fourth_games.empty

    assert fourth_games[fourth_games['start_time'] == '11:05 am']['home_team'].values[0] == 'Washington Nationals'