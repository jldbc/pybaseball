from time import sleep
from typing import Generator

import pytest

from pybaseball import amateur_draft
from pybaseball.utils import most_recent_season


@pytest.fixture(autouse=True)
def before_after_each() -> Generator[None, None, None]:
    # before each test
    yield
    # after each test
    sleep(6) # BBRef will throttle us if we make more than 10 calls per minute

def test_amateur_draft() -> None:
    result = amateur_draft(2019, 1)

    assert result is not None
    assert not result.empty

    assert len(result.columns) == 20
    assert len(result) == 41


def test_amateur_draft_no_stats() -> None:
    result = amateur_draft(2019, 1, keep_stats=False)

    assert result is not None
    assert not result.empty

    assert len(result.columns) == 8
    assert len(result) == 41


def test_amateur_draft_future() -> None:
    result = amateur_draft(most_recent_season() + 1, 1, keep_stats=False)

    assert result is not None
    assert not result.empty

    print(result)

    assert len(result.columns) == 8
    assert (len(result) > 30) and (len(result) < 60)
