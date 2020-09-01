import numpy as np
import pandas as pd
import pytest

from pybaseball.datasources import fangraphs


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


class TestDatasourceFangraphs:
    def test_get_table(self, sample_html, sample_processed_result):
        actual_result = fangraphs.get_fangraphs_tabular_data_from_html(
            sample_html,
            '//table',
            ["CS%"],
            ["Team"]
        ).reset_index(drop=True)

        pd.testing.assert_frame_equal(sample_processed_result, actual_result)
