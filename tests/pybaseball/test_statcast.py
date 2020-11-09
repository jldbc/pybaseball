from typing import Callable

import pandas as pd
import pytest

from pybaseball.statcast import _SC_SINGLE_GAME_REQUEST, statcast_single_game
from pybaseball.utils import DATE_FORMAT

# For an explanation of this type, see the note on GetDataFrameCallable in tests/pybaseball/conftest.py
from .conftest import GetDataFrameCallable


@pytest.fixture(name="single_game_raw")
def _single_game_raw(get_data_file_contents: Callable[[str], str]) -> str:
    return get_data_file_contents('single_game_request_raw.csv')


@pytest.fixture(name="single_game")
def _single_game(get_data_file_dataframe: GetDataFrameCallable) -> pd.DataFrame:
    data = get_data_file_dataframe('single_game_request.csv', parse_dates=[2])
    data[data.columns[2]].apply(pd.to_datetime, errors='ignore', format=DATE_FORMAT)
    return data


def test_statcast_single_game_request(response_get_monkeypatch: Callable, single_game_raw: str,
                                      single_game: pd.DataFrame) -> None:
    game_pk = '631614'

    response_get_monkeypatch(
        single_game_raw.encode('UTF-8'),
        _SC_SINGLE_GAME_REQUEST.format(game_pk=game_pk)
    )

    statcast_result = statcast_single_game(game_pk).reset_index(drop=True)

    pd.testing.assert_frame_equal(statcast_result, single_game, check_dtype=False)
