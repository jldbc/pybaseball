from typing import Callable

import pandas as pd
import pytest
import requests

from pybaseball.batting_leaders import batting_stats


@pytest.fixture(name="sample_html")
def _sample_html(get_data_file_contents: Callable[[str], str]) -> str:
    return get_data_file_contents('batting_leaders.html')


@pytest.fixture(name="sample_processed_result")
def _sample_processed_result(get_data_file_dataframe: Callable[[str], pd.DataFrame]) -> pd.DataFrame:
    return get_data_file_dataframe('batting_leaders.csv')


def test_batting_stats(response_get_monkeypatch: Callable, sample_html: str,
                        sample_processed_result: pd.DataFrame):
    season = 2019

    response_get_monkeypatch(sample_html)

    batting_stats_result = batting_stats(season).reset_index(drop=True)

    pd.testing.assert_frame_equal(batting_stats_result, sample_processed_result, check_dtype=False)
