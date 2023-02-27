from time import sleep
from typing import Generator

import pytest

from pybaseball import team_batting_against
from pybaseball.utils import most_recent_season


@pytest.fixture(autouse=True)
def before_after_each() -> Generator[None, None, None]:
    # before each test
    yield
    # after each test
    sleep(6)  # BBRef will throttle us if we make more than 10 calls per minute


def test_team_batting_current_year() -> None:
    result = team_batting_against()

    assert result is not None
    assert not result.empty

    assert len(result.columns) == 26


def test_team_batting_against_specific_year() -> None:
    result = team_batting_against(2022)

    assert result is not None
    assert not result.empty

    assert len(result.columns) == 26
    assert len(result) == 30


def test_team_batting_against_future() -> None:
    with pytest.raises(ValueError):
        team_batting_against(most_recent_season() + 1)


def test_team_batting_against_bad_input() -> None:
    with pytest.raises(ValueError):
        team_batting_against(1776)
