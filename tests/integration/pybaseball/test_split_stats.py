from time import sleep
from typing import Generator

import pandas as pd
import pytest

from pybaseball import get_splits


@pytest.fixture(autouse=True)
def before_after_each() -> Generator[None, None, None]:
    # before each test
    yield
    # after each test
    sleep(6) # BBRef will throttle us if we make more than 10 calls per minute

def test_get_splits() -> None:
    result: pd.DataFrame = get_splits('troutmi01')

    assert result is not None
    assert not result.empty

    assert len(result.columns) > 0
    assert len(result) > 0


def test_get_splits_player_info() -> None:
    result, player_info = get_splits('troutmi01', player_info=True)

    assert result is not None
    assert not result.empty

    assert len(result.columns) > 0
    assert len(result) > 0

    assert player_info is not None
    assert len(player_info.keys()) > 0


def test_get_splits_pitching_splits() -> None:
    result, pitching_splits = get_splits('lestejo01', pitching_splits=True)

    assert result is not None
    assert not result.empty

    assert len(result.columns) > 0
    assert len(result) > 0

    assert pitching_splits is not None
    assert len(pitching_splits.keys()) > 0
