from typing import Callable

import pandas as pd
import pytest

from pybaseball.team_batting_against import _URL, team_batting_against
from pybaseball.utils import most_recent_season
from .conftest import GetDataFrameCallable


@pytest.fixture(name="sample_html_2022")
def _sample_html_2022(get_data_file_contents: Callable[[str], str]) -> str:
    return get_data_file_contents('team_batting_against_2022.html')


@pytest.fixture(name="sample_processed_result_2022")
def _sample_processed_result_2022(get_data_file_dataframe: GetDataFrameCallable) -> pd.DataFrame:
    return get_data_file_dataframe('team_batting_against_2022.csv')


@pytest.fixture(name="sample_html_1925")
def _sample_html_1925(get_data_file_contents: Callable[[str], str]) -> str:
    return get_data_file_contents('team_batting_against_1925.html')


@pytest.fixture(name="sample_processed_result_1925")
def _sample_processed_result_1925(get_data_file_dataframe: GetDataFrameCallable) -> pd.DataFrame:
    return get_data_file_dataframe('team_batting_against_1925.csv')

@pytest.fixture(name="sample_html_1974")
def _sample_html_1974(get_data_file_contents: Callable[[str], str]) -> str:
    return get_data_file_contents('team_batting_against_1974.html')


@pytest.fixture(name="sample_processed_result_1974")
def _sample_processed_result_1974(get_data_file_dataframe: GetDataFrameCallable) -> pd.DataFrame:
    return get_data_file_dataframe('team_batting_against_1974.csv')


def test_batting_against_2022(bref_get_monkeypatch: Callable, sample_html_2022: str,
                              sample_processed_result_2022: pd.DataFrame) -> None:
    expected_url = _URL.format(year=2022)

    bref_get_monkeypatch(sample_html_2022, expected_url)
    result = team_batting_against(2022)

    assert result is not None
    assert not result.empty

    pd.testing.assert_frame_equal(result, sample_processed_result_2022, check_dtype=False)


def test_batting_against_1925(bref_get_monkeypatch: Callable, sample_html_1925: str,
                              sample_processed_result_1925: pd.DataFrame) -> None:
    expected_url = _URL.format(year=1925)

    bref_get_monkeypatch(sample_html_1925, expected_url)
    result = team_batting_against(1925)

    assert result is not None
    assert not result.empty

    pd.testing.assert_frame_equal(result, sample_processed_result_1925, check_dtype=False)
    
def test_batting_against_1974(bref_get_monkeypatch: Callable, sample_html_1974: str,
                              sample_processed_result_1974: pd.DataFrame) -> None:
    expected_url = _URL.format(year=1974)

    bref_get_monkeypatch(sample_html_1974, expected_url)
    result = team_batting_against(1974)

    assert result is not None
    assert not result.empty

    pd.testing.assert_frame_equal(result, sample_processed_result_1974, check_dtype=False)


def test_batting_against_illegal_arguments() -> None:
    old_year = 1914
    with pytest.raises(ValueError, match='between 1915 and current season'):
        team_batting_against(old_year)

    future_year = most_recent_season() + 1
    with pytest.raises(ValueError, match='between 1915 and current season'):
        team_batting_against(future_year)
