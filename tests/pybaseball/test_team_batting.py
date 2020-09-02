import pandas as pd
import pytest
import requests

from pybaseball.team_batting import team_batting, _FG_TEAM_BATTING_URL


@pytest.fixture()
def sample_html(get_data_file_contents):
    return get_data_file_contents('team_batting.html')


@pytest.fixture()
def sample_processed_result(get_data_file_dataframe):
    return get_data_file_dataframe('team_batting.csv')

class TestTeamBatting:
    def test_team_batting(self, response_get_monkeypatch, sample_html, sample_processed_result):
        season = 2019

        expected_url = _FG_TEAM_BATTING_URL.format(start_season=season, end_season=season, league='all', ind=1)

        response_get_monkeypatch(sample_html, expected_url)

        team_batting_result = team_batting(season).reset_index(drop=True)

        pd.testing.assert_frame_equal(team_batting_result, sample_processed_result)
