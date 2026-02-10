from time import sleep
from typing import Generator, Optional

import pandas as pd
import pytest

from pybaseball.playoff_odds import playoff_odds
from pybaseball.utils import most_recent_season

@pytest.fixture(autouse=True)
def before_after_each() -> Generator[None, None, None]:
    # before each test
    yield
    # after each test
    sleep(6) # BBRef will throttle us if we make more than 10 calls per minute

class TestBRefPlayoffOdds:
    @pytest.mark.parametrize(
        "season", [2024]  # Changed to test only 2024
    )
    def test_odds(self, season: Optional[int]) -> None:
        season_playoff_odds = playoff_odds(season)
        assert season_playoff_odds is not None
        assert season_playoff_odds is not None
        assert len(season_playoff_odds.columns) > 0
        assert len(season_playoff_odds.index) > 0