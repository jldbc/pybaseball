from datetime import datetime
from typing import List, Optional, Tuple

import pandas as pd
import pytest

from pybaseball.standings import standings

def get_division_counts_by_season(season: Optional[int]) -> int:
    if season is None:
        season = datetime.today().year

    if season >= 1994:
        return 6
    if season >= 1969:
        return 4
    return 1

class TestBRefStandings:
    @pytest.mark.parametrize(
        "season", [(x) for x in range(1871, datetime.today().year + 1)] + [(None)] # type: ignore
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
        season = datetime.today().year + 1

        standings_list = standings(season)

        assert standings_list == []
