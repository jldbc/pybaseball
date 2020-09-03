from datetime import datetime, timedelta
from typing import Callable

import pandas as pd
import pytest
import requests

from pybaseball.statcast import (_SC_SINGLE_GAME_REQUEST, _SC_SMALL_REQUEST, sanitize_input, statcast,
                                 statcast_single_game, DATE_FORMAT)

from .conftest import GetDataFrameCallable


@pytest.fixture()
def small_request_raw(get_data_file_contents: Callable[[str], str]) -> str:
    return get_data_file_contents('small_request_raw.csv')


@pytest.fixture()
def small_request(get_data_file_dataframe: GetDataFrameCallable) -> pd.DataFrame:
    return get_data_file_dataframe('small_request.csv', parse_dates=[2])

@pytest.fixture()
def single_game_raw(get_data_file_contents: Callable[[str], str]) -> str:
    return get_data_file_contents('single_game_request_raw.csv')


@pytest.fixture()
def single_game(get_data_file_dataframe: GetDataFrameCallable) -> pd.DataFrame:
    return get_data_file_dataframe('single_game_request.csv', parse_dates=[2])

class TestStatcast:
    def test_sanitize_input_nones(self) -> None:
        yesterday = datetime.today() - timedelta(days=1)

        start_dt, end_dt = sanitize_input(None, None)

        assert start_dt.date() == yesterday.date()
        assert end_dt.date() == datetime.today().date()
        
    def test_sanitize_input_no_end_dt(self) -> None:
        yesterday = datetime.today() - timedelta(days=1)

        start_dt, end_dt = sanitize_input(yesterday.strftime(DATE_FORMAT), None)

        assert start_dt.date() == yesterday.date()
        assert end_dt.date() == yesterday.date()
        
    def test_sanitize_input(self) -> None:
        start_dt, end_dt = sanitize_input('2020-05-06', '2020-06-06')

        assert start_dt == datetime.strptime('2020-05-06', DATE_FORMAT)
        assert end_dt == datetime.strptime('2020-06-06', DATE_FORMAT)
        
    def test_sanitize_input_bad_start_dt(self) -> None:
        with pytest.raises(ValueError) as ex_info:
            sanitize_input('INVALID', '2020-06-06')

        assert str(ex_info.value) == 'Incorrect data format, should be YYYY-MM-DD'
        
    def test_sanitize_input_bad_end_dt(self) -> None:
        with pytest.raises(ValueError) as ex_info:
            sanitize_input('2020-05-06', 'INVALID')

        assert str(ex_info.value) == 'Incorrect data format, should be YYYY-MM-DD'

    def test_statcast(
        self,
        response_get_monkeypatch: Callable,
        small_request_raw: str,
        small_request: pd.DataFrame
    ) -> None:
        start_dt, end_dt = sanitize_input(None, None)
        response_get_monkeypatch(
            small_request_raw.encode('UTF-8'),
            _SC_SMALL_REQUEST.format(
                start_dt=start_dt.strftime(DATE_FORMAT),
                end_dt=end_dt.strftime(DATE_FORMAT),
                team=''
            )
        )

        statcast_result = statcast().reset_index(drop=True)

        pd.testing.assert_frame_equal(statcast_result, small_request)
    
    def test_statcast_team(
        self,
        response_get_monkeypatch: Callable,
        small_request_raw: str,
        small_request: pd.DataFrame
    ) -> None:
        start_dt, end_dt = sanitize_input(None, None)
        response_get_monkeypatch(
            small_request_raw.encode('UTF-8'),
            _SC_SMALL_REQUEST.format(
                start_dt=start_dt.strftime(DATE_FORMAT),
                end_dt=end_dt.strftime(DATE_FORMAT),
                team='TB'
            )
        )

        statcast_result = statcast(None, None, team='TB').reset_index(drop=True)

        pd.testing.assert_frame_equal(statcast_result, small_request)

    def test_statcast_single_game_request(
        self,
        response_get_monkeypatch: Callable,
        single_game_raw: str,
        single_game: pd.DataFrame
    ) -> None:
        game_pk = '631614'

        response_get_monkeypatch(
            single_game_raw.encode('UTF-8'),
            _SC_SINGLE_GAME_REQUEST.format(game_pk=game_pk)
        )

        statcast_result = statcast_single_game(game_pk).reset_index(drop=True)

        pd.testing.assert_frame_equal(statcast_result, single_game)
