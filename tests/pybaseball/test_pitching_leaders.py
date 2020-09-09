from typing import Callable

import pandas as pd
import pytest

from pybaseball.datasources.fangraphs import _FG_PITCHING_LEADERS_TYPES, _FG_PITCHING_LEADERS_URL
from pybaseball.pitching_leaders import pitching_stats


@pytest.fixture(name="sample_html")
def _sample_html(get_data_file_contents: Callable) -> str:
    return get_data_file_contents('pitching_leaders.html')


@pytest.fixture(name="sample_processed_result")
def _sample_processed_result(get_data_file_dataframe: Callable) -> pd.DataFrame:
    return get_data_file_dataframe('pitching_leaders.csv')


def test_pitching_stats(response_get_monkeypatch: Callable, sample_html: str, sample_processed_result: pd.DataFrame):
    season = 2019

    expected_url = _FG_PITCHING_LEADERS_URL.format(
        start_season=season,
        end_season=season,
        league='all',
        qual=1,
        ind=1,
        types=_FG_PITCHING_LEADERS_TYPES
    )

    response_get_monkeypatch(sample_html, expected_url)

    with pytest.warns(DeprecationWarning):
        pitching_stats_result = pitching_stats(season).reset_index(drop=True)

    pd.testing.assert_frame_equal(pitching_stats_result, sample_processed_result)
