from typing import Optional

import pandas as pd
import pytest

from pybaseball.standings import standings
from pybaseball.utils import most_recent_season


def get_division_counts_by_season(season: Optional[int]) -> int:
    if season is None:
        season = most_recent_season()

    if season >= 1994:
        return 6
    if season >= 1969:
        return 4
    return 1

class TestBRefStandings:
    @pytest.mark.parametrize(
        "season", [(x) for x in range(1871, most_recent_season() + 1)] + [(None)] # type: ignore
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

    def test_standings_pre_1871(self) -> None:
        season = 1870

        with pytest.raises(ValueError):
            standings(season)

    def test_standings_future(self) -> None:
        season = most_recent_season() + 1

        standings_list = standings(season)

        assert standings_list == []
