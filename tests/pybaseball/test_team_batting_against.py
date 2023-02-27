from typing import Callable

import pandas as pd
import pytest

from pybaseball.team_batting_against import _URL, team_batting_against

from .conftest import GetDataFrameCallable


@pytest.fixture(name="sample_html")
def _sample_html(get_data_file_contents: Callable[[str], str]) -> str:
    return get_data_file_contents('team_batting_against.html')


@pytest.fixture(name="sample_processed_result")
def _sample_processed_result(get_data_file_dataframe: GetDataFrameCallable) -> pd.DataFrame:
    return get_data_file_dataframe('team_batting_against.csv')


def test_batting_against(bref_get_monkeypatch: Callable, sample_html: str,
                         sample_processed_result: pd.DataFrame) -> None:
    expected_url = _URL.format(year=2022)

    bref_get_monkeypatch(sample_html, expected_url)
    result = team_batting_against(2022)

    assert result is not None
    assert not result.empty

    pd.testing.assert_frame_equal(result, sample_processed_result, check_dtype=False)
