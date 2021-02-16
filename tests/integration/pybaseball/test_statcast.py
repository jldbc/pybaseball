from datetime import date, timedelta
from typing import cast
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

import pybaseball
from pybaseball.statcast import _small_request, _handle_request, statcast, statcast_single_game
from pybaseball.utils import sanitize_date_range


def test_small_request() -> None:
    start_dt, end_dt = sanitize_date_range('2019-06-01', None)
    result = _small_request(start_dt, end_dt)

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


def test_statcast_chunking() -> None:
    result = statcast('2019-05-01', '2019-05-15').reset_index(drop=True)

    assert result is not None
    assert not result.empty

    day_results = []
    start_date = date(2019, 5, 1)

    for day in range(15):
        day_results.append(statcast(str(start_date + timedelta(days=day))))

    day_results_dataframe = pd.concat(day_results, axis=0).convert_dtypes(convert_string=False)
    day_results_dataframe = day_results_dataframe.sort_values(
        ['game_date', 'game_pk', 'at_bat_number', 'pitch_number'],
        ascending=False
    ).reset_index(drop=True)

    assert list(result.columns) == list(day_results_dataframe.columns)
    assert len(result) == len(day_results_dataframe)


def test_handle_request_pre_season() -> None:
    start_dt, end_dt = sanitize_date_range('2019-03-01', '2019-03-22')
    result = _handle_request(start_dt, end_dt, step=1, verbose=False)

    assert result is not None
    assert not result.empty

    assert len(result.columns) == 89
    assert len(result) == 689


@pytest.mark.filterwarnings("ignore:That's a nice request you got there")
def test_handle_request_post_season() -> None:
    start_dt, end_dt = sanitize_date_range('2018-11-14', '2019-03-22')
    result = _handle_request(start_dt, end_dt, step=1, verbose=False)

    assert result is not None
    assert not result.empty

    assert len(result.columns) == 89
    assert len(result) == 689


def test_handle_request_post_season_same_year() -> None:
    start_dt, end_dt = sanitize_date_range('2018-11-14', '2018-11-30')
    result = _handle_request(start_dt, end_dt, step=1, verbose=False)

    assert result is not None
    assert result.empty


def test_single_game_request() -> None:
    result = statcast_single_game(289317)

    assert result is not None
    assert not result.empty

    assert len(result.columns) == 89
    assert len(result) == 462
