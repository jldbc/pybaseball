import json
from io import StringIO
from typing import Callable

import pandas as pd
import pytest
from bs4 import BeautifulSoup

from pybaseball.fangraphs_projections import (_FgProjectionArgument,
                                              fg_projections)


@pytest.fixture(name="raw_source_batters")
def _raw_source_batters(get_data_file_contents: Callable[[str], str]) -> str:
    return get_data_file_contents('fangraphs_projections_batters.html')


@pytest.fixture(name="raw_source_pitchers")
def _raw_source_pitchers(get_data_file_contents: Callable[[str], str]) -> str:
    return get_data_file_contents('fangraphs_projections_pitchers.html')


@pytest.fixture(name="raw_source_empty")
def _raw_source_empty(get_data_file_contents: Callable[[str], str]) -> str:
    return get_data_file_contents('fangraphs_projections_empty.html')


@pytest.fixture(name="expected_results_batters")
def _expected_results_batters(get_data_file_dataframe: Callable[[str], str]) -> str:
    return get_data_file_dataframe("fangraphs_projections_batters.csv")


@pytest.fixture(name="expected_results_pitchers")
def _expected_results_pitchers(get_data_file_dataframe: Callable[[str], str]) -> str:
    return get_data_file_dataframe("fangraphs_projections_pitchers.csv")


@pytest.fixture(name="raw_json")
def _raw_json(get_data_file_contents: Callable[[str], str]) -> str:
    return get_data_file_contents("fangraphs_projections_pitchers.json")


def test_default_batters_projections_success(response_get_monkeypatch: Callable, raw_source_batters: str, expected_results_batters: str) -> None:
    response_get_monkeypatch(raw_source_batters)
    result = fg_projections()
    pd.testing.assert_frame_equal(result, expected_results_batters, check_dtype=False)


def test_pitchers_projections_success(response_get_monkeypatch: Callable, raw_source_pitchers: str, expected_results_pitchers: str) -> None:
    response_get_monkeypatch(raw_source_pitchers)
    result = fg_projections(position="pitchers")
    pd.testing.assert_frame_equal(result, expected_results_pitchers, check_dtype=False)


def test_empty_projections_returns_empty_dataframe(response_get_monkeypatch: Callable, raw_source_empty: str, expected_results_batters: str) -> None:
    response_get_monkeypatch(raw_source_empty)
    result = fg_projections("onpaceegp")  # on pace sources are empty during offseason
    pd.testing.assert_frame_equal(result, pd.DataFrame(), check_dtype=False)


def test_illegal_arguments_return_exception() -> None:
    with pytest.raises(ValueError):
        fg_projections("quarterbacks")

    with pytest.raises(ValueError):
        fg_projections("pitchers", "pecota")

    with pytest.raises(ValueError):
        fg_projections("pitchers", "zipsdc", "nfl")

    with pytest.raises(ValueError):
        fg_projections("pitchers", "zipsdc", "al", "Eagles")


def test_team_lookup_arguments() -> None:
    args = _FgProjectionArgument("cf", "thebat", "mlb", "PHI")
    assert args.team_id == 26


def test_url_generator() -> None:
    expected = "https://www.fangraphs.com/projections?pos=&stats=bat&type=zips&team=&lg="
    args = _FgProjectionArgument("batters", "zips", "mlb", "")
    assert args.url == expected

    expected = "https://www.fangraphs.com/projections?pos=&stats=pit&type=zips&team=&lg="
    args = _FgProjectionArgument("pitchers", "zips", "mlb", "")
    assert args.url == expected

    expected = "https://www.fangraphs.com/projections?pos=&stats=rel&type=steamer&team=&lg="
    args = _FgProjectionArgument("rp", "steamer", "mlb", "")
    assert args.url == expected

    expected = "https://www.fangraphs.com/projections?pos=cf&stats=bat&type=thebat&team=&lg=al"
    args = _FgProjectionArgument("cf", "thebat", "al", "")
    assert args.url == expected
