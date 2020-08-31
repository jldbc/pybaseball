import numpy as np
import pandas as pd
import pytest
import requests

from pybaseball.team_fielding import team_fielding, _FG_TEAM_FIELDING_URL


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
                        <td>1</td>
                        <td>2</td>
                        <td>50 %</td>
                        <td>8</td>
                    </tr>
                    <tr>
                        <td>#2</td>
                        <td>555</td>
                        <td>3</td>
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
            ['TBR', 1.0, 2.0, 0.50, 8],
            ['555', 3.0, 4.0, 0.45, np.nan]
        ],
        columns=['Team', 'Runs', 'Hits', 'CS%', 'HR']
    ).reset_index(drop=True)


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
