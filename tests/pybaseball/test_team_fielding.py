import os

import numpy as np
import pandas as pd
import pytest
import requests

from pybaseball.team_fielding import team_fielding, _FG_TEAM_FIELDING_URL


@pytest.fixture()
def data_dir():
    this_dir = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(this_dir, 'data')


@pytest.fixture()
def sample_html(data_dir):
    with open(os.path.join(data_dir, 'team_fielding.html')) as html:
        return html.read()


@pytest.fixture()
def sample_processed_result(data_dir):
    return pd.read_csv(os.path.join(data_dir, 'team_fielding.csv'), index_col=0)


class TestTeamFielding:
    def test_team_fielding(self, monkeypatch, sample_html, sample_processed_result):
        season = 2019

        def response_get_monkeypatch(url):
            assert url.endswith(
                _FG_TEAM_FIELDING_URL.format(start_season=season, end_season=season, league='all', ind=1)
            )

            class DummyResponse:
                def __init__(self, html):
                    self.content = html

            return DummyResponse(sample_html)

        monkeypatch.setattr(requests, 'get', response_get_monkeypatch)

        team_fielding_result = team_fielding(season).reset_index(drop=True)

        pd.testing.assert_frame_equal(team_fielding_result, sample_processed_result)
