from typing import Callable

import pandas as pd
import pytest
import requests

from pybaseball.batting_leaders import _FG_BATTING_LEADERS_TYPES, _FG_BATTING_LEADERS_URL, batting_stats


@pytest.fixture()
def sample_html(get_data_file_contents: Callable) -> str:
    return get_data_file_contents('batting_leaders.html')


@pytest.fixture()
def sample_processed_result(get_data_file_dataframe: Callable) -> pd.DataFrame:
    return get_data_file_dataframe('batting_leaders.csv')


class TestBattingLeaders:
    def test_batting_stats(
        self,
        response_get_monkeypatch: Callable,
        sample_html: str,
        sample_processed_result: pd.DataFrame
    ):
        season = 2019

        expected_url = _FG_BATTING_LEADERS_URL.format(
            start_season=season,
            end_season=season,
            league='all',
            qual=1,
            ind=1,
            types=_FG_BATTING_LEADERS_TYPES
        )

        response_get_monkeypatch(sample_html, expected_url)

        batting_stats_result = batting_stats(season).reset_index(drop=True)

        assert batting_stats_result['Dol'][8] == sample_processed_result['Dol'][8]

        pd.testing.assert_frame_equal(batting_stats_result, sample_processed_result)
