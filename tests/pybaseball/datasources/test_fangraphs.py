import sys
from typing import Callable

import numpy as np
import pandas as pd
import pytest

from pybaseball.datasources.fangraphs import (_FG_LEADERS_URL, MAX_AGE,
                                              MIN_AGE, GenericColumnMapper,
                                              BattingStatsColumnMapper,
                                              FanGraphs)

from pybaseball.enums.fangraphs import batting_stats, fielding_stats, pitching_stats

@pytest.fixture()
def sample_html():
    return """
        <html>
        <head></head>
        <body>
            <table class="rgMasterTable">
                <thead>
                    <tr>
                        <th class="rgHeader">#</th>
                        <th class="rgHeader">Team</th>
                        <th class="rgHeader">Runs</th>
                        <th class="rgHeader">Hits</th>
                        <th class="rgHeader">CS%</th>
                        <th class="rgHeader">HR</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>#1</td>
                        <td>TBR</td>
                        <td>1.0</td>
                        <td>2</td>
                        <td>50 %</td>
                        <td>8</td>
                    </tr>
                    <tr>
                        <td>#2</td>
                        <td>NYY</td>
                        <td>3.5</td>
                        <td>4</td>
                        <td>45%</td>
                        <td>null</td>
                    </tr>
                </tbody>
            </table>
        </body>
    """


@pytest.fixture()
def sample_processed_result():
    return pd.DataFrame(
        [
            ['TBR', 1, 2, 0.50, 8],
            ['NYY', 3.5, 4, 0.45, np.nan]
        ],
        columns=['Team', 'Runs', 'Hits', 'CS%', 'HR']
    ).reset_index(drop=True)


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
    def test_get_table(self, sample_html, sample_processed_result):
        actual_result = FanGraphs().get_tabular_data_from_html(
            sample_html
        ).reset_index(drop=True)

        pd.testing.assert_frame_equal(sample_processed_result, actual_result)

    def test_batting_stats(self, response_get_monkeypatch: Callable, test_batting_stats_html: str,
                           test_batting_stats_result: pd.DataFrame):
        season = 2019

        expected_url = FanGraphs()._create_url(_FG_LEADERS_URL,
            {
                'pos': 'all',
                'stats': 'bat',
                'lg': 'all',
                'qual': 'y',
                'type': batting_stats.FanGraphsBattingStat.ALL(),
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
            }
        )

        response_get_monkeypatch(test_batting_stats_html, expected_url)

        batting_stats_result = FanGraphs().batting_stats(season).reset_index(drop=True)

        pd.testing.assert_frame_equal(batting_stats_result, test_batting_stats_result)

    def test_pitching_stats(self, response_get_monkeypatch: Callable, test_pitching_stats_html: str,
                            test_pitching_stats_result: pd.DataFrame):
        season = 2019

        expected_url = FanGraphs()._create_url(_FG_LEADERS_URL,
            {
                'pos': 'all',
                'stats': 'pit',
                'lg': 'all',
                'qual': 'y',
                'type': pitching_stats.FanGraphsPitchingStat.ALL(),
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
            }
        )

        response_get_monkeypatch(test_pitching_stats_html, expected_url)

        pitching_stats_result = FanGraphs().pitching_stats(season).reset_index(drop=True)

        pd.testing.assert_frame_equal(pitching_stats_result, test_pitching_stats_result)

    def test_team_batting(self, response_get_monkeypatch: Callable, test_team_batting_html: str,
                          test_team_batting_result: pd.DataFrame):
        season = 2019

        expected_url = FanGraphs()._create_url(_FG_LEADERS_URL,
            {
                'pos': 'all',
                'stats': 'bat',
                'lg': 'all',
                'qual': 'y',
                'type': batting_stats.FanGraphsBattingStat.ALL(),
                'season': season,
                'month': 0,
                'season1': season,
                'ind': '1',
                'team': '0,ts',
                'rost': '0',
                'age': f"{MIN_AGE},{MAX_AGE}",
                'filter': '',
                'players': '0',
                'page': f'1_1000000'
            }
        )

        response_get_monkeypatch(test_team_batting_html, expected_url)

        team_batting_result = FanGraphs().team_batting(season).reset_index(drop=True)

        pd.testing.assert_frame_equal(team_batting_result, test_team_batting_result)


    def test_team_fielding(self, response_get_monkeypatch: Callable, test_team_fielding_html: str,
                           test_team_fielding_result: pd.DataFrame):
        season = 2019

        expected_url = FanGraphs()._create_url(_FG_LEADERS_URL,
            {
                'pos': 'all',
                'stats': 'fld',
                'lg': 'all',
                'qual': 'y',
                'type': fielding_stats.FanGraphsFieldingStat.ALL(),
                'season': season,
                'month': 0,
                'season1': season,
                'ind': '1',
                'team': '0,ts',
                'rost': '0',
                'age': f"{MIN_AGE},{MAX_AGE}",
                'filter': '',
                'players': '0',
                'page': f'1_1000000'
            }
        )

        response_get_monkeypatch(test_team_fielding_html, expected_url)

        team_fielding_result = FanGraphs().team_fielding(season).reset_index(drop=True)

        pd.testing.assert_frame_equal(team_fielding_result, test_team_fielding_result)


    def test_team_pitching(self, response_get_monkeypatch: Callable, test_team_pitching_html: str,
                           test_team_pitching_result: pd.DataFrame):
        season = 2019

        expected_url = FanGraphs()._create_url(_FG_LEADERS_URL,
            {
                'pos': 'all',
                'stats': 'pit',
                'lg': 'all',
                'qual': 'y',
                'type': pitching_stats.FanGraphsPitchingStat.ALL(),
                'season': season,
                'month': 0,
                'season1': season,
                'ind': '1',
                'team': '0,ts',
                'rost': '0',
                'age': f"{MIN_AGE},{MAX_AGE}",
                'filter': '',
                'players': '0',
                'page': f'1_1000000'
            }
        )

        response_get_monkeypatch(test_team_pitching_html, expected_url)

        team_pitching_result = FanGraphs().team_pitching(season).reset_index(drop=True)

        pd.testing.assert_frame_equal(team_pitching_result, test_team_pitching_result)

class TestGenericColumnWrapper:
    def test_generic_column_mapper(self):
        mapper = GenericColumnMapper()

        assert mapper.map('FB%') == 'FB%'

        assert mapper.map('HR') == 'HR'

        assert mapper.map('FB%') == 'FB% 2'

        assert mapper.map('HR') == 'HR 2'

class TestBattingStatsColumnWrapper:
    def test_batting_stats_column_mapper(self):
        mapper = BattingStatsColumnMapper()

        assert mapper.map('FB%') == 'FB%'

        assert mapper.map('HR') == 'HR'

        assert mapper.map('FB%') == 'FB% (Pitch)'

        assert mapper.map('HR') == 'HR 2'
