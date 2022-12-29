from time import sleep
from typing import Generator, Optional

import pandas as pd
import pytest

from pybaseball.standings import standings
from pybaseball.utils import most_recent_season

@pytest.fixture(autouse=True)
def before_after_each() -> Generator[None, None, None]:
    # before each test
    yield
    # after each test
    sleep(6) # BBRef will throttle us if we make more than 10 calls per minute

def get_division_counts_by_season(season: Optional[int]) -> int:
    if season is None:
        season = most_recent_season() - 1

    if season >= 1994:
        return 6
    if season >= 1969:
        return 4
    return 1

class TestBRefStandings:
    @pytest.mark.parametrize(
        "season", [(x) for x in range(1876, most_recent_season())]
    )
    def test_standings(self, season: Optional[int]) -> None:
        standings_list = standings(season)

        assert standings_list is not None
        assert len(standings_list) == get_division_counts_by_season(season)

        for data in standings_list:
            assert data is not None
            assert not data.empty
            assert len(data.columns) > 0
            assert len(data.index) > 0

    def test_standings_pre_1876(self) -> None:
        season = 1870

        with pytest.raises(ValueError):
            standings(season)

    def test_standings_future(self) -> None:
        season = most_recent_season() + 1

        standings_list = standings(season)

        assert standings_list == []
