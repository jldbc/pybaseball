from time import sleep
from typing import Generator, Optional

import pytest

from pybaseball.team_results import get_soup, schedule_and_record
from pybaseball.utils import first_season_map, get_first_season, most_recent_season


missing_schedules_scores = {
    'AB2', 'AB3', 'ABC', 'AC' , 'AG' , 'BBB', 'BBS', 'BCA', 'BE' , 'BEG', 'BFB', 'BLO', 'BLT', 'BR2', 'BRD', 'BRS',
    'CAG', 'CBB', 'CBE', 'CBK', 'CBL', 'CBN', 'CBR', 'CC' , 'CCB', 'CCU', 'CEG', 'CEL', 'CG',  'CHH', 'CHI', 'CHP', 'CHT',
    'CL2', 'CLI', 'CLS', 'CLV', 'CNR', 'CNS', 'COB', 'COG', 'COT', 'CRS', 'CS' , 'CSE', 'CSW', 'CT' , 'CTG', 'CTS', 'CUP',
    'DM' , 'DS' , 'DTS', 'DW' , 'DYM', 'HBG', 'HG' , 'HIL', 'IA' , 'IAB', 'IBL', 'IC' , 'ID' , 'IHO', 'JRC', 'KCM', 'KCU',
    'LGR', 'LOW', 'LRG', 'LVB', 'MB' , 'MGS', 'MLA', 'MLU', 'MRM', 'MRS', 'NBY', 'ND' , 'NE' , 'NEG', 'NLG', 'NS' , 'NWB',
    'NYC', 'PBG', 'PBK', 'PC' , 'PK' , 'PS' , 'PTG', 'SBS', 'SEN', 'SL2', 'SL3', 'SLG', 'SLI', 'SLS', 'SNH', 'SNS',
    'SYS', 'TC' , 'TC2', 'TLM', 'TRT', 'TT' , 'WAP', 'WEG', 'WMP', 'WNA', 'WNL', 'WP' , 'WST'
}

@pytest.fixture(autouse=True)
def before_after_each() -> Generator[None, None, None]:
    # before each test
    yield
    # after each test
    sleep(6) # BBRef will throttle us if we make more than 10 calls per minute

@pytest.mark.parametrize(
    "season, team", [
        (get_first_season(x, False), x) for x in first_season_map.keys()
    ]
)
def test_schedule_and_record(season: Optional[int], team: str) -> None:
    if season is None or team in missing_schedules_scores:
        return
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
        (get_first_season(x, False), x) for x in first_season_map.keys()
    ]
)
def test_schedule_and_record_bad_years(season: Optional[int], team: str) -> None:
    if season is None:
        return

    with pytest.raises(ValueError):
        schedule_and_record(season - 1, team)

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
