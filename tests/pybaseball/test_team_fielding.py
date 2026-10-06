from typing import Callable

import pandas as pd
import pytest
import requests

from pybaseball.team_fielding import team_fielding


@pytest.fixture()
def sample_html(get_data_file_contents: Callable[[str], str]) -> str:
    return get_data_file_contents('team_fielding.html')


@pytest.fixture()
def sample_processed_result(get_data_file_dataframe: Callable) -> pd.DataFrame:
    return get_data_file_dataframe('team_fielding.csv')


def test_team_fielding(response_get_monkeypatch: Callable, sample_html: str, sample_processed_result: pd.DataFrame) -> None:
    season = 2019

    response_get_monkeypatch(sample_html)

    team_fielding_result = team_fielding(season).reset_index(drop=True)

    pd.testing.assert_frame_equal(team_fielding_result, sample_processed_result, check_dtype=False)


def test_team_fielding_bref_invalid_season_range() -> None:
    # Regression test for #462: an end_season earlier than start_season should
    # raise a clear ValueError before any network request is made.
    from pybaseball.team_fielding import team_fielding_bref

    with pytest.raises(ValueError):
        team_fielding_bref('NYY', 2019, 2018)
