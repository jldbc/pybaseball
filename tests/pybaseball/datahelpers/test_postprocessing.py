from datetime import datetime

import numpy as np
import pandas as pd
import pytest

from pybaseball.datahelpers import postprocessing


@pytest.fixture(name='sample_unprocessed_result')
def _sample_unprocessed_result() -> pd.DataFrame:
    return pd.DataFrame(
        [
            ['TBR', '1', '2', '50 %', '8'],
            ['555', '3', '4', '45%', 'null'],
        ],
        columns=['Team', 'Runs', 'Hits', 'CS%', 'HR']
    ).reset_index(drop=True)


def test_try_parse_short_date() -> None:
    assert postprocessing.try_parse('2020-09-04', 'game_dt') == datetime(year=2020, month=9, day=4)


def test_try_parse_long_date() -> None:
    expected_datetime = datetime(year=2020, month=9, day=3, hour=5, minute=40, second=30, microsecond=210000)
    assert postprocessing.try_parse('2020-09-03T05:40:30.210Z', 'game_dt') == expected_datetime


def test_try_parse_date_nonstr() -> None:
    expected = datetime(year=2020, month=9, day=4)
    assert postprocessing.try_parse(expected, 'game_dt') == expected


def test_try_parse_int() -> None:
    assert postprocessing.try_parse('1', 'runs') == 1


def test_try_parse_int_nonstr() -> None:
    assert postprocessing.try_parse(1, 'runs') == 1


def test_try_parse_float() -> None:
    assert postprocessing.try_parse('1.0', 'runs') == 1.0


def test_try_parse_float_nonstr() -> None:
    assert postprocessing.try_parse(1.0, 'runs') == 1.0


def test_try_parse_percentage_value() -> None:
    assert postprocessing.try_parse('10%', 'avg') == 0.1


def test_try_parse_percentage_column() -> None:
    assert postprocessing.try_parse('50', 'CS%') == 0.5


def test_try_parse_percentage_column_known() -> None:
    assert postprocessing.try_parse('50', 'CS', known_percentages=['CS']) == 0.5


def test_try_parse_null() -> None:
    assert pd.isna(postprocessing.try_parse(None, 'runs'))


def test_try_parse_dataframe() -> None:
    raw_data = pd.DataFrame(
        [
            ['1', 'TBR', '2019-01-01', '0.5', '40%', 8, '1048576'],
            ['2', 'NYY', '2019-02-01', '0.6', '20%', 'null', '4294967296'],
        ],
        columns=['id', 'team', 'dt', 'rate', 'chance', 'wins', 'long_number']
    )

    processed_data = postprocessing.try_parse_dataframe(raw_data)

    expected_data = pd.DataFrame(
        [
            [1, 'TBR', np.datetime64('2019-01-01'), 0.5, 0.4, 8, 1048576],
            [2, 'NYY', np.datetime64('2019-02-01'), 0.6, 0.2, np.nan, 4294967296],
        ],
        columns=['id', 'team', 'dt', 'rate', 'chance', 'wins', 'long_number']
    ).convert_dtypes(convert_string=False)

    pd.testing.assert_frame_equal(processed_data, expected_data, check_dtype=False)


def test_coalesce_nulls(sample_unprocessed_result: pd.DataFrame) -> None:
    expected_result = pd.DataFrame(
        [
            ['TBR', '1', '2', '50 %', '8'],
            ['555', '3', '4', '45%', np.nan],
        ],
        columns=['Team', 'Runs', 'Hits', 'CS%', 'HR']
    ).reset_index(drop=True)

    actual_result = postprocessing.coalesce_nulls(sample_unprocessed_result).reset_index(drop=True)

    pd.testing.assert_frame_equal(actual_result, expected_result)


def test_columns_except(sample_unprocessed_result: pd.DataFrame) -> None:
    expected_columns = ['Runs', 'Hits', 'CS%', 'HR']

    actual_columns = postprocessing.columns_except(sample_unprocessed_result, ['Team'])

    assert set(expected_columns) == set(actual_columns)


def test_convert_numeric(sample_unprocessed_result: pd.DataFrame) -> None:
    expected_result = pd.DataFrame(
        [
            ['TBR', 1.0, 2.0, '50 %', 8],
            ['555', 3.0, 4.0, '45%', np.nan],
        ],
        columns=['Team', 'Runs', 'Hits', 'CS%', 'HR']
    ).reset_index(drop=True)

    actual_result = postprocessing.convert_numeric(
        postprocessing.coalesce_nulls(sample_unprocessed_result),
        ['Runs', 'Hits', 'HR']
    ).reset_index(drop=True)

    pd.testing.assert_frame_equal(actual_result, expected_result)


def test_convert_percentages(sample_unprocessed_result: pd.DataFrame) -> None:
    expected_result = pd.DataFrame(
        [
            ['TBR', '1', '2', 0.50, '8'],
            ['555', '3', '4', 0.45, 'null'],
        ],
        columns=['Team', 'Runs', 'Hits', 'CS%', 'HR']
    ).reset_index(drop=True)

    actual_result = postprocessing.convert_percentages(
        sample_unprocessed_result,
        ['CS%']
    ).reset_index(drop=True)

    pd.testing.assert_frame_equal(actual_result, expected_result)
