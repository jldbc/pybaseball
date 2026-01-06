from time import sleep
from typing import Generator

import pytest

from pybaseball import pitching_stats

@pytest.fixture(autouse=True)
def before_after_each() -> Generator[None, None, None]:
    # before each test
    yield
    # after each test
    sleep(6) # BBRef will throttle us if we make more than 10 calls per minute

def test_pitching_stats_basic() -> None:
    result = pitching_stats(2019)

    assert result is not None
    assert not result.empty

    assert len(result.columns) == 334
    assert len(result) == 61

def test_pitching_stats_range() -> None:
    result = pitching_stats(2019, start_date='2019-09-03', end_date='2019-10-05')

    assert result is not None
    assert not result.empty

    assert len(result.columns) == 333
    assert len(result) == 57

def test_pitching_stats_range_gt3yrs() -> None:
    with pytest.raises(ValueError):
        result = pitching_stats(2015, start_date='2015-10-03', end_date='2019-10-05')

def test_pitching_stats_range_start_season_ne_start_date() -> None:
    with pytest.raises(ValueError):
        result = pitching_stats(2019, start_date='2020-10-03', end_date='2021-10-05')

def test_pitching_stats_range_bad_formatting() -> None:
    with pytest.raises(ValueError):
        result = pitching_stats(2023, start_date='23-04-03', end_date='23-04-05')

def test_pitching_stats_range_no_start_season() -> None:
    with pytest.raises(TypeError):
        result = pitching_stats(start_date='2020-10-03', end_date='2021-10-05')
