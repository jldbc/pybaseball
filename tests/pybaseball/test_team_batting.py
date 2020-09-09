from typing import Callable

import pandas as pd
import pytest
import requests

from pybaseball.datasources.fangraphs import _FG_TEAM_BATTING_URL
from pybaseball.team_batting import team_batting


@pytest.fixture(name="sample_html")
def _sample_html(get_data_file_contents: Callable) -> str:
    return get_data_file_contents('team_batting.html')


@pytest.fixture(name="sample_processed_result")
def _sample_processed_result(get_data_file_dataframe: Callable) -> pd.DataFrame:
    return get_data_file_dataframe('team_batting.csv')

def test_team_batting(response_get_monkeypatch: Callable, sample_html: str, sample_processed_result: pd.DataFrame):
    season = 2019

    expected_url = _FG_TEAM_BATTING_URL.format(start_season=season, end_season=season, league='all', ind=1)

    response_get_monkeypatch(sample_html, expected_url)

    with pytest.warns(DeprecationWarning):
        team_batting_result = team_batting(season).reset_index(drop=True)

    pd.testing.assert_frame_equal(team_batting_result, sample_processed_result)
