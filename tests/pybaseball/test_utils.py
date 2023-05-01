from datetime import date, datetime, timedelta

import pytest

from pybaseball.utils import DATE_FORMAT, sanitize_date_range, statcast_clean_column_names


def test_sanitize_date_range_nones() -> None:
    yesterday = date.today() - timedelta(days=1)

    start_dt, end_dt = sanitize_date_range(None, None)

    assert start_dt == yesterday
    assert end_dt == date.today()


def test_sanitize_date_range_no_end_dt() -> None:
    yesterday = date.today() - timedelta(days=1)

    start_dt, end_dt = sanitize_date_range(str(yesterday), None)

    assert start_dt == yesterday
    assert end_dt == yesterday


def test_sanitize_date_range() -> None:
    start_dt, end_dt = sanitize_date_range('2020-05-06', '2020-06-06')

    assert start_dt == datetime.strptime('2020-05-06', DATE_FORMAT).date()
    assert end_dt == datetime.strptime('2020-06-06', DATE_FORMAT).date()


def test_sanitize_date_range_bad_start_dt() -> None:
    with pytest.raises(ValueError) as ex_info:
        sanitize_date_range('INVALID', '2020-06-06')

    assert str(ex_info.value) == 'Incorrect data format, should be YYYY-MM-DD'


def test_sanitize_date_range_bad_end_dt() -> None:
    with pytest.raises(ValueError) as ex_info:
        sanitize_date_range('2020-05-06', 'INVALID')

    assert str(ex_info.value) == 'Incorrect data format, should be YYYY-MM-DD'


def test_sanitize_date_range_start_dt_gt_end_dt() -> None:
    start_dt = '2020-05-06'
    end_dt = '2019-08-01'
    start_dt_date, end_dt_date = sanitize_date_range(start_dt, end_dt)

    assert start_dt_date < end_dt_date
    assert str(start_dt_date) == end_dt
    assert str(end_dt_date) == start_dt

def test_statcast_clean_column_names() -> None:
    assert statcast_clean_column_names(("Unnamed: 0_level_0", "Total Movement (In.)")) == "Total Movement (In.)"
    assert statcast_clean_column_names(("Runners On Base", "Total Movement (In.)")) == "Runners On Base Total Movement (In.)"
    assert statcast_clean_column_names("Total Movement (In.)") == "Total Movement (In.)"
