import pytest
from datetime import datetime

from pybaseball.statcast import statcast, statcast_single_game, small_request, large_request
from pybaseball.utils import sanitize_date_range


def test_small_request() -> None:
    start_dt, end_dt = sanitize_date_range('2019-06-01', None)
    result = small_request(start_dt, end_dt)

    assert result is not None
    assert not result.empty

    assert len(result.columns) == 89
    assert len(result) == 4556

def test_statcast() -> None:
    result = statcast('2019-05-01', '2019-05-04')

    assert result is not None
    assert not result.empty

    assert len(result.columns) == 89
    assert len(result) == 16130

def test_large_request_verbose() -> None:
    start_dt, end_dt = sanitize_date_range('2019-05-01', '2019-05-09')
    result = large_request(start_dt, end_dt, step=1, verbose=True)

    assert result is not None
    assert not result.empty

    assert len(result.columns) == 89
    assert len(result) == 35531

def test_large_request_pre_season() -> None:
    start_dt, end_dt = sanitize_date_range('2019-03-01', '2019-03-22')
    result = large_request(start_dt, end_dt, step=1, verbose=False)

    assert result is not None
    assert not result.empty

    assert len(result.columns) == 89
    assert len(result) == 689

def test_large_request_post_season() -> None:
    start_dt, end_dt = sanitize_date_range('2018-11-14', '2019-03-22')
    result = large_request(start_dt, end_dt, step=1, verbose=False)

    assert result is not None
    assert not result.empty

    assert len(result.columns) == 89
    assert len(result) == 689

def test_large_request_post_season_same_year() -> None:
    start_dt, end_dt = sanitize_date_range('2018-11-14', '2018-11-30')
    result = large_request(start_dt, end_dt, step=1, verbose=False)

    assert result is not None
    assert result.empty

def test_single_game_request() -> None:
    result = statcast_single_game(289317)

    assert result is not None
    assert not result.empty

    assert len(result.columns) == 89
    assert len(result) == 462
