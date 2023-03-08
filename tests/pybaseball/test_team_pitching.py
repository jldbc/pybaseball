from typing import Callable

import pandas as pd
import pytest
import requests

from pybaseball.team_pitching import team_pitching


@pytest.fixture()
def sample_html(get_data_file_contents: Callable[[str], str]) -> str:
    return get_data_file_contents('team_pitching.html')


@pytest.fixture()
def sample_processed_result(get_data_file_dataframe: Callable) -> pd.DataFrame:
    return get_data_file_dataframe('team_pitching.csv')


def test_team_pitching(response_get_monkeypatch: Callable, sample_html: str, sample_processed_result: pd.DataFrame) -> None:
    season = 2019

    response_get_monkeypatch(sample_html)

    team_pitching_result = team_pitching(season).reset_index(drop=True)

    pd.testing.assert_frame_equal(team_pitching_result, sample_processed_result, check_dtype=False)
