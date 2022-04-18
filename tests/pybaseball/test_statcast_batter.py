from typing import Callable

import pandas as pd
import pytest
from tests.pybaseball.conftest import GetDataFrameCallable

from pybaseball.statcast_batter import statcast_batter


@pytest.fixture(name="single_day_raw")
def _single_day_raw(get_data_file_contents: Callable[[str], str]) -> str:
    return get_data_file_contents("statcast_batter_raw.csv")


@pytest.fixture(name="single_day")
def _single_day(get_data_file_dataframe: GetDataFrameCallable) -> pd.DataFrame:
    return get_data_file_dataframe("statcast_batter_data.csv")


def test_statcast_batter_input_handling(
    response_get_monkeypatch: Callable,
    single_day_raw: str,
    single_day: pd.DataFrame,
) -> None:
    """
    Test whether `statcast_batter` correctly handles optional start and end dates.

    Parameters
    ----------
    response_get_monkeypatch : Callable
        The response monkeypatch function
    single_day_raw : str
        The raw csv result from the request
    single_day : pd.DataFrame
        The processed DataFrame expected
    """
    pid = 116539  # Derek Jeter
    dt = "2014-09-28"  # Last day

    url_end = "&team=&position=&hfRO=&home_road=&hfFlag=&metric_1=&hfInn=&min_pitches=0&min_results=0&group_by=name&sort_col=pitches&player_event_sort=h_launch_speed&sort_order=desc&min_abs=0&type=details&"
    response_get_monkeypatch(single_day_raw, url_end)

    res = statcast_batter(start_dt=dt, player_id=pid)
    pd.testing.assert_frame_equal(res, single_day, check_dtype=False)

    res = statcast_batter(end_dt=dt, player_id=pid)
    pd.testing.assert_frame_equal(res, single_day, check_dtype=False)
