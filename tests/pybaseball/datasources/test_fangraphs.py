import sys
import urllib.parse
from typing import Callable

import numpy as np
import pandas as pd
import pytest

from pybaseball.datasources.fangraphs import (_FG_LEADERS_URL, MAX_AGE, MIN_AGE, fg_batting_data, fg_pitching_data,
                                              fg_team_batting_data, fg_team_fielding_data, fg_team_pitching_data)
from pybaseball.enums.fangraphs import FanGraphsBattingStat, FanGraphsFieldingStat, FanGraphsPitchingStat, type_list_to_str


@pytest.fixture(name="test_batting_stats_html")
def _test_batting_stats_html(get_data_file_contents: Callable) -> str:
    return get_data_file_contents('batting_leaders.html')


@pytest.fixture(name="test_batting_stats_result")
def _test_batting_stats_result(get_data_file_dataframe: Callable) -> pd.DataFrame:
    return get_data_file_dataframe('batting_leaders.csv')


@pytest.fixture(name="test_pitching_stats_html")
def _test_pitching_stats_html(get_data_file_contents: Callable) -> str:
    return get_data_file_contents('pitching_leaders.html')


@pytest.fixture(name="test_pitching_stats_result")
def _test_pitching_stats_result(get_data_file_dataframe: Callable) -> pd.DataFrame:
    return get_data_file_dataframe('pitching_leaders.csv')


@pytest.fixture(name="test_team_batting_html")
def _test_team_batting_html(get_data_file_contents: Callable) -> str:
    return get_data_file_contents('team_batting.html')


@pytest.fixture(name="test_team_batting_result")
def _test_team_batting_result(get_data_file_dataframe: Callable) -> pd.DataFrame:
    return get_data_file_dataframe('team_batting.csv')

    
@pytest.fixture(name="test_team_fielding_html")
def _test_team_fielding_html(get_data_file_contents: Callable) -> str:
    return get_data_file_contents('team_fielding.html')


@pytest.fixture(name="test_team_fielding_result")
def _test_team_fielding_result(get_data_file_dataframe: Callable) -> pd.DataFrame:
    return get_data_file_dataframe('team_fielding.csv')


@pytest.fixture(name="test_team_pitching_html")
def _test_team_pitching_html(get_data_file_contents: Callable) -> str:
    return get_data_file_contents('team_pitching.html')


@pytest.fixture(name="test_team_pitching_result")
def _test_team_pitching_result(get_data_file_dataframe: Callable) -> pd.DataFrame:
    return get_data_file_dataframe('team_pitching.csv')

class TestDatasourceFangraphs:
    def test_batting_stats(self, response_get_monkeypatch: Callable, test_batting_stats_html: str,
                           test_batting_stats_result: pd.DataFrame):
        season = 2019

        query_params = urllib.parse.urlencode(
            {
                'pos': 'all',
                'stats': 'bat',
                'lg': 'all',
                'qual': 'y',
                'type': type_list_to_str(FanGraphsBattingStat.ALL()),
                'season': season,
                'month': 0,
                'season1': season,
                'ind': '1',
                'team': '',
                'rost': '0',
                'age': f"{MIN_AGE},{MAX_AGE}",
                'filter': '',
                'players': '',
                'page': f'1_1000000'
            },
            safe=','
        )

        expected_url = f"{_FG_LEADERS_URL}?{query_params}" 

        response_get_monkeypatch(test_batting_stats_html, expected_url)

        batting_stats_result = fg_batting_data(season).reset_index(drop=True)

        pd.testing.assert_frame_equal(batting_stats_result, test_batting_stats_result)
    def test_batting_stats_custom_types(self, response_get_monkeypatch: Callable, test_batting_stats_html: str,
                           test_batting_stats_result: pd.DataFrame):
        season = 2019

        query_params = urllib.parse.urlencode(
            {
                'pos': 'all',
                'stats': 'bat',
                'lg': 'all',
                'qual': 'y',
                'type': type_list_to_str([FanGraphsBattingStat.COMMON, FanGraphsBattingStat.WAR], replace_common=False),
                'season': season,
                'month': 0,
                'season1': season,
                'ind': '1',
                'team': '',
                'rost': '0',
                'age': f"{MIN_AGE},{MAX_AGE}",
                'filter': '',
                'players': '',
                'page': f'1_1000000'
            },
            safe=','
        )

        expected_url = f"{_FG_LEADERS_URL}?{query_params}" 

        response_get_monkeypatch(test_batting_stats_html, expected_url)

        batting_stats_result = fg_batting_data(season, types=[FanGraphsBattingStat.WAR]).reset_index(drop=True)

        pd.testing.assert_frame_equal(batting_stats_result, test_batting_stats_result)

    def test_pitching_stats(self, response_get_monkeypatch: Callable, test_pitching_stats_html: str,
                            test_pitching_stats_result: pd.DataFrame):
        season = 2019

        query_params = urllib.parse.urlencode(
            {
                'pos': 'all',
                'stats': 'pit',
                'lg': 'all',
                'qual': 'y',
                'type': type_list_to_str(FanGraphsPitchingStat.ALL()),
                'season': season,
                'month': 0,
                'season1': season,
                'ind': '1',
                'team': '',
                'rost': '0',
                'age': f"{MIN_AGE},{MAX_AGE}",
                'filter': '',
                'players': '',
                'page': f'1_1000000'
            },
            safe=','
        )

        expected_url = f"{_FG_LEADERS_URL}?{query_params}"

        response_get_monkeypatch(test_pitching_stats_html, expected_url)

        pitching_stats_result = fg_pitching_data(season).reset_index(drop=True)

        pd.testing.assert_frame_equal(pitching_stats_result, test_pitching_stats_result)

    def test_pitching_stats_custom_types(self, response_get_monkeypatch: Callable, test_pitching_stats_html: str,
                            test_pitching_stats_result: pd.DataFrame):
        season = 2019

        query_params = urllib.parse.urlencode(
            {
                'pos': 'all',
                'stats': 'pit',
                'lg': 'all',
                'qual': 'y',
                'type': type_list_to_str([FanGraphsPitchingStat.COMMON, FanGraphsPitchingStat.ERA_MINUS], replace_common=False),
                'season': season,
                'month': 0,
                'season1': season,
                'ind': '1',
                'team': '',
                'rost': '0',
                'age': f"{MIN_AGE},{MAX_AGE}",
                'filter': '',
                'players': '',
                'page': f'1_1000000'
            },
            safe=','
        )

        expected_url = f"{_FG_LEADERS_URL}?{query_params}"

        response_get_monkeypatch(test_pitching_stats_html, expected_url)

        pitching_stats_result = fg_pitching_data(season, types=[FanGraphsPitchingStat.ERA_MINUS]).reset_index(drop=True)

        pd.testing.assert_frame_equal(pitching_stats_result, test_pitching_stats_result)

    def test_team_batting(self, response_get_monkeypatch: Callable, test_team_batting_html: str,
                          test_team_batting_result: pd.DataFrame):
        season = 2019

        query_params = urllib.parse.urlencode(
            {
                'pos': 'all',
                'stats': 'bat',
                'lg': 'all',
                'qual': 'y',
                'type': type_list_to_str(FanGraphsBattingStat.ALL()),
                'season': season,
                'month': 0,
                'season1': season,
                'ind': '1',
                'team': '0,ts',
                'rost': '0',
                'age': f"{MIN_AGE},{MAX_AGE}",
                'filter': '',
                'players': '',
                'page': f'1_1000000'
            },
            safe=','
        )

        expected_url = f"{_FG_LEADERS_URL}?{query_params}"

        response_get_monkeypatch(test_team_batting_html, expected_url)

        team_batting_result = fg_team_batting_data(season).reset_index(drop=True)

        pd.testing.assert_frame_equal(team_batting_result, test_team_batting_result)

    def test_team_batting_custom_types(self, response_get_monkeypatch: Callable, test_team_batting_html: str,
                          test_team_batting_result: pd.DataFrame):
        season = 2019

        query_params = urllib.parse.urlencode(
            {
                'pos': 'all',
                'stats': 'bat',
                'lg': 'all',
                'qual': 'y',
                'type': type_list_to_str([FanGraphsBattingStat.COMMON, FanGraphsBattingStat.HOME_RUNS], replace_common=False),
                'season': season,
                'month': 0,
                'season1': season,
                'ind': '1',
                'team': '0,ts',
                'rost': '0',
                'age': f"{MIN_AGE},{MAX_AGE}",
                'filter': '',
                'players': '',
                'page': f'1_1000000'
            },
            safe=','
        )

        expected_url = f"{_FG_LEADERS_URL}?{query_params}"

        response_get_monkeypatch(test_team_batting_html, expected_url)

        team_batting_result = fg_team_batting_data(season, types=[FanGraphsBattingStat.HOME_RUNS]).reset_index(drop=True)

        pd.testing.assert_frame_equal(team_batting_result, test_team_batting_result)


    def test_team_fielding(self, response_get_monkeypatch: Callable, test_team_fielding_html: str,
                           test_team_fielding_result: pd.DataFrame):
        season = 2019

        query_params = urllib.parse.urlencode(
            {
                'pos': 'all',
                'stats': 'fld',
                'lg': 'all',
                'qual': 'y',
                'type': type_list_to_str(FanGraphsFieldingStat.ALL()),
                'season': season,
                'month': 0,
                'season1': season,
                'ind': '1',
                'team': '0,ts',
                'rost': '0',
                'age': f"{MIN_AGE},{MAX_AGE}",
                'filter': '',
                'players': '',
                'page': f'1_1000000'
            },
            safe=','
        )

        expected_url = f"{_FG_LEADERS_URL}?{query_params}"

        response_get_monkeypatch(test_team_fielding_html, expected_url)

        team_fielding_result = fg_team_fielding_data(season).reset_index(drop=True)

        pd.testing.assert_frame_equal(team_fielding_result, test_team_fielding_result)


    def test_team_fielding_custom_types(self, response_get_monkeypatch: Callable, test_team_fielding_html: str,
                           test_team_fielding_result: pd.DataFrame):
        season = 2019

        query_params = urllib.parse.urlencode(
            {
                'pos': 'all',
                'stats': 'fld',
                'lg': 'all',
                'qual': 'y',
                'type': type_list_to_str([FanGraphsFieldingStat.COMMON, FanGraphsFieldingStat.ULTIMATE_ZONE_RATING], replace_common=False),
                'season': season,
                'month': 0,
                'season1': season,
                'ind': '1',
                'team': '0,ts',
                'rost': '0',
                'age': f"{MIN_AGE},{MAX_AGE}",
                'filter': '',
                'players': '',
                'page': f'1_1000000'
            },
            safe=','
        )

        expected_url = f"{_FG_LEADERS_URL}?{query_params}"

        response_get_monkeypatch(test_team_fielding_html, expected_url)

        team_fielding_result = fg_team_fielding_data(season, types=[FanGraphsFieldingStat.ULTIMATE_ZONE_RATING]).reset_index(drop=True)

        pd.testing.assert_frame_equal(team_fielding_result, test_team_fielding_result)


    def test_team_pitching(self, response_get_monkeypatch: Callable, test_team_pitching_html: str,
                           test_team_pitching_result: pd.DataFrame):
        season = 2019

        query_params = urllib.parse.urlencode(
            {
                'pos': 'all',
                'stats': 'pit',
                'lg': 'all',
                'qual': 'y',
                'type': type_list_to_str(FanGraphsPitchingStat.ALL()),
                'season': season,
                'month': 0,
                'season1': season,
                'ind': '1',
                'team': '0,ts',
                'rost': '0',
                'age': f"{MIN_AGE},{MAX_AGE}",
                'filter': '',
                'players': '',
                'page': f'1_1000000'
            },
            safe=','
        )
        expected_url = f"{_FG_LEADERS_URL}?{query_params}"

        response_get_monkeypatch(test_team_pitching_html, expected_url)

        team_pitching_result = fg_team_pitching_data(season).reset_index(drop=True)

        pd.testing.assert_frame_equal(team_pitching_result, test_team_pitching_result)


    def test_team_pitching_custom_types(self, response_get_monkeypatch: Callable, test_team_pitching_html: str,
                           test_team_pitching_result: pd.DataFrame):
        season = 2019

        query_params = urllib.parse.urlencode(
            {
                'pos': 'all',
                'stats': 'pit',
                'lg': 'all',
                'qual': 'y',
                'type': type_list_to_str([FanGraphsPitchingStat.COMMON, FanGraphsPitchingStat.WINS], replace_common=False),
                'season': season,
                'month': 0,
                'season1': season,
                'ind': '1',
                'team': '0,ts',
                'rost': '0',
                'age': f"{MIN_AGE},{MAX_AGE}",
                'filter': '',
                'players': '',
                'page': f'1_1000000'
            },
            safe=','
        )
        expected_url = f"{_FG_LEADERS_URL}?{query_params}"

        response_get_monkeypatch(test_team_pitching_html, expected_url)

        team_pitching_result = fg_team_pitching_data(season, types=[FanGraphsPitchingStat.WINS]).reset_index(drop=True)

        pd.testing.assert_frame_equal(team_pitching_result, test_team_pitching_result)
