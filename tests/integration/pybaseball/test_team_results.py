from pybaseball.utils import first_season_map
from datetime import datetime
import pytest
from pybaseball.team_results import schedule_and_record, get_soup
import json
from typing import Dict, List

@pytest.mark.parametrize(
    "season, team", [
        (first_season_map[x], x) for x in first_season_map.keys()
    ]
)
def test_schedule_and_record(season: int, team: str) -> None:
    result = schedule_and_record(season, team)
    
    assert result is not None
    assert not result.empty

    assert len(result.columns) == 19
    assert len(result) > 0

@pytest.mark.parametrize(
    "season, team", [
        (first_season_map[x] - 1, x) for x in first_season_map.keys()
    ]
)
def test_schedule_and_record_bad_years(season: int, team: str) -> None:
    with pytest.raises(ValueError):
        schedule_and_record(season, team)

def test_schedule_and_record_after_existence() -> None:
    with pytest.raises(ValueError):
        schedule_and_record(2019, 'TBD')
        
def test_schedule_and_record_future() -> None:
    with pytest.raises(ValueError):
        schedule_and_record(datetime.today().year + 1, 'TBR')
        
def test_get_soup_none_season() -> None:
    result = get_soup(None, 'TBR')

    assert result is not None

def test_schedule_and_record_bad_team() -> None:
    with pytest.raises(ValueError):
        schedule_and_record(2019, 'TBZ')
