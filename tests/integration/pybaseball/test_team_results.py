import pytest

from pybaseball.team_results import get_soup, schedule_and_record
from pybaseball.utils import first_season_map, most_recent_season


@pytest.mark.parametrize(
    "season, team", [
        (first_season_map[x], x) for x in first_season_map.keys()
    ]
)
def test_schedule_and_record(season: int, team: str) -> None:
    result = schedule_and_record(season, team)
    
    assert result is not None
    assert not result.empty

    expected_columns = [
        'Date', 'Tm', 'Home_Away', 'Opp', 'W/L', 'R', 'RA', 'Inn', 'W-L', 'Rank', 'GB', 'Win',
        'Loss', 'Save', 'Time', 'D/N', 'Attendance', 'cLI', 'Streak', 'Orig. Scheduled'
    ]

    if season < 1903:
        expected_columns.remove('cLI')

    assert list(result.columns) == expected_columns
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
        schedule_and_record(most_recent_season() + 1, 'TBR')
        
def test_get_soup_none_season() -> None:
    result = get_soup(None, 'TBR')

    assert result is not None

def test_schedule_and_record_bad_team() -> None:
    with pytest.raises(ValueError):
        schedule_and_record(2019, 'TBZ')
