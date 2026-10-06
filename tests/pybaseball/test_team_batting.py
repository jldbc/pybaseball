from typing import Callable

import pandas as pd
import pytest
import requests

from pybaseball.team_batting import team_batting


@pytest.fixture(name="sample_html")
def _sample_html(get_data_file_contents: Callable[[str], str]) -> str:
    return get_data_file_contents('team_batting.html')


@pytest.fixture(name="sample_processed_result")
def _sample_processed_result(get_data_file_dataframe: Callable) -> pd.DataFrame:
    return get_data_file_dataframe('team_batting.csv')


def test_team_batting(response_get_monkeypatch: Callable, sample_html: str, sample_processed_result: pd.DataFrame) -> None:
    season = 2019

    response_get_monkeypatch(sample_html)

    team_batting_result = team_batting(season).reset_index(drop=True)

    pd.testing.assert_frame_equal(team_batting_result, sample_processed_result, check_dtype=False)


@pytest.fixture(name="sample_bref_html")
def _sample_bref_html(get_data_file_contents: Callable[[str], str]) -> str:
    return get_data_file_contents('team_batting_bref.html')


def test_team_batting_bref(bref_get_monkeypatch: Callable, sample_bref_html: str) -> None:
    # Regression test for #461: Baseball Reference changed the batting table to
    # id='players_standard_batting' with a <thead>. team_batting_bref must parse
    # the new structure instead of the removed 'sortable stats_table' class.
    from pybaseball.team_batting import team_batting_bref

    bref_get_monkeypatch(sample_bref_html)

    result = team_batting_bref('NYY', 2019)

    assert result is not None
    assert not result.empty
    assert 'Tm' in result.columns
    assert 'Year' in result.columns
    assert (result['Year'] == 2019).all()


def test_team_batting_bref_missing_table_raises(bref_get_monkeypatch: Callable) -> None:
    # Regression test for #461: a page without the expected table should raise a
    # clear ValueError instead of an opaque IndexError.
    from pybaseball.team_batting import team_batting_bref

    bref_get_monkeypatch("<html><body><p>no table here</p></body></html>")

    with pytest.raises(ValueError):
        team_batting_bref('NYY', 2019)
