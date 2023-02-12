from typing import Callable

import pandas as pd
import pytest

from pybaseball.amateur_draft_by_team import _URL, amateur_draft_by_team

from .conftest import GetDataFrameCallable


@pytest.fixture(name="sample_html")
def _sample_html(get_data_file_contents: Callable[[str], str]) -> str:
    return get_data_file_contents("amateur_draft_by_team.html")


@pytest.fixture(name="sample_processed_result")
def _sample_processed_result(
    get_data_file_dataframe: GetDataFrameCallable,
) -> pd.DataFrame:
    return get_data_file_dataframe("amateur_draft_by_team_keep_stats.csv")


@pytest.fixture(name="sample_processed_result_no_stats")
def _sample_processed_result_no_stats(
    get_data_file_dataframe: GetDataFrameCallable,
) -> pd.DataFrame:
    return get_data_file_dataframe("amateur_draft_by_team_no_stats.csv")


def test_amateur_draft(
    bref_get_monkeypatch: Callable[[str, str], None],
    sample_html: str,
    sample_processed_result: pd.DataFrame,
) -> None:
    expected_url = _URL.format(team="TBD", year=2011)

    bref_get_monkeypatch(sample_html, expected_url)
    result = amateur_draft_by_team("TBD", 2011)
    result.to_csv('./tests/pybaseball/data/amateur_draft_by_team_keep_stats.csv')

    assert result is not None
    assert not result.empty

    pd.testing.assert_frame_equal(result, sample_processed_result, check_dtype=False)


def test_amateur_draft_no_stats(
    bref_get_monkeypatch: Callable[[str, str], None],
    sample_html: str,
    sample_processed_result_no_stats: pd.DataFrame,
) -> None:
    expected_url = _URL.format(team="TBD", year=2011)

    bref_get_monkeypatch(sample_html, expected_url)
    result = amateur_draft_by_team("TBD", 2011, keep_stats=False)
    result.to_csv('./tests/pybaseball/data/amateur_draft_by_team_no_stats.csv')

    assert result is not None
    assert not result.empty

    pd.testing.assert_frame_equal(
        result, sample_processed_result_no_stats, check_dtype=False
    )
