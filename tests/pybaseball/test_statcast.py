from typing import Callable

import pandas as pd
import pytest
import requests

from pybaseball.statcast import statcast, statcast_single_game


@pytest.fixture()
def small_request_raw(get_data_file_contents: Callable) -> str:
    return get_data_file_contents('small_request_raw.csv')


@pytest.fixture()
def small_request(get_data_file_dataframe: Callable) -> pd.DataFrame:
    return get_data_file_dataframe('small_request.csv', parse_dates=[2])

@pytest.fixture()
def single_game_raw(get_data_file_contents: Callable) -> str:
    return get_data_file_contents('single_game_request_raw.csv')


@pytest.fixture()
def single_game(get_data_file_dataframe: Callable) -> pd.DataFrame:
    return get_data_file_dataframe('single_game_request.csv', parse_dates=[2])

class TestStatcast:
    def test_statcast(
        self,
        response_get_monkeypatch: Callable,
        small_request_raw: str,
        small_request: pd.DataFrame
    ):
        response_get_monkeypatch(small_request_raw.encode('UTF-8'))

        statcast_result = statcast().reset_index(drop=True)

        pd.testing.assert_frame_equal(statcast_result, small_request)

    def test_statcast_single_game_request(
        self,
        response_get_monkeypatch: Callable,
        single_game_raw: str,
        single_game: pd.DataFrame
    ):
        response_get_monkeypatch(single_game_raw.encode('UTF-8'))

        statcast_result = statcast_single_game('631614').reset_index(drop=True)

        pd.testing.assert_frame_equal(statcast_result, single_game)
