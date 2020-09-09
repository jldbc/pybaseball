from typing import Callable

import pandas as pd
import pytest
import requests

from pybaseball.datasources.fangraphs import _FG_TEAM_PITCHING_URL, _FG_TEAM_PITCHING_TYPES
from pybaseball.team_pitching import team_pitching


@pytest.fixture()
def sample_html(get_data_file_contents: Callable) -> str:
    return get_data_file_contents('team_pitching.html')


@pytest.fixture()
def sample_processed_result(get_data_file_dataframe: Callable) -> pd.DataFrame:
    return get_data_file_dataframe('team_pitching.csv')


def test_team_pitching(response_get_monkeypatch: Callable, sample_html: str, sample_processed_result: pd.DataFrame):
    season = 2019

    expected_url = _FG_TEAM_PITCHING_URL.format(
        start_season=season,
        end_season=season,
        league='all',
        ind=1,
        types=_FG_TEAM_PITCHING_TYPES
    )

    response_get_monkeypatch(sample_html, expected_url)

    with pytest.warns(DeprecationWarning):
        team_pitching_result = team_pitching(season).reset_index(drop=True)

    pd.testing.assert_frame_equal(team_pitching_result, sample_processed_result)
