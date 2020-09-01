import numpy as np
import pandas as pd

import pytest

from pybaseball.datahelpers import postprocessing


@pytest.fixture()
def sample_unprocessed_result():
    return pd.DataFrame(
        [
            ['TBR', '1', '2', '50 %', '8'],
            ['555', '3', '4', '45%', 'null']
        ],
        columns=['Team', 'Runs', 'Hits', 'CS%', 'HR']
    ).reset_index(drop=True)


class TestPostProcessing:
    def test_try_parse_int(self):
        assert postprocessing.try_parse('1', 'runs') == 1

    def test_try_parse_float(self):
        assert postprocessing.try_parse('1.0', 'runs') == 1.0

    def test_try_parse_percentage_value(self):
        assert postprocessing.try_parse('10%', 'avg') == 0.1

    def test_try_parse_percentage_column(self):
        assert postprocessing.try_parse('50', 'CS%') == 0.5

    def test_coalesce_nulls(self, sample_unprocessed_result):
        expected_result = pd.DataFrame(
            [
                ['TBR', '1', '2', '50 %', '8'],
                ['555', '3', '4', '45%', np.nan]
            ],
            columns=['Team', 'Runs', 'Hits', 'CS%', 'HR']
        ).reset_index(drop=True)

        actual_result = postprocessing.coalesce_nulls(sample_unprocessed_result).reset_index(drop=True)

        pd.testing.assert_frame_equal(actual_result, expected_result)

    def test_columns_except(self, sample_unprocessed_result):
        expected_columns = ['Runs', 'Hits', 'CS%', 'HR']

        actual_columns = postprocessing.columns_except(sample_unprocessed_result, ['Team'])

        assert set(expected_columns) == set(actual_columns)

    def test_convert_numeric(self, sample_unprocessed_result):
        expected_result = pd.DataFrame(
            [
                ['TBR', 1.0, 2.0, '50 %', 8],
                ['555', 3.0, 4.0, '45%', np.nan]
            ],
            columns=['Team', 'Runs', 'Hits', 'CS%', 'HR']
        ).reset_index(drop=True)

        actual_result = postprocessing.convert_numeric(
            postprocessing.coalesce_nulls(sample_unprocessed_result),
            ['Runs', 'Hits', 'HR']
        ).reset_index(drop=True)

        pd.testing.assert_frame_equal(actual_result, expected_result)

    def test_convert_percentages(self, sample_unprocessed_result):
        expected_result = pd.DataFrame(
            [
                ['TBR', '1', '2', 0.50, '8'],
                ['555', '3', '4', 0.45, 'null']
            ],
            columns=['Team', 'Runs', 'Hits', 'CS%', 'HR']
        ).reset_index(drop=True)

        actual_result = postprocessing.convert_percentages(
            sample_unprocessed_result,
            ['CS%']
        ).reset_index(drop=True)

        pd.testing.assert_frame_equal(actual_result, expected_result)
