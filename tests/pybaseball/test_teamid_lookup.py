import pandas as pd
import pytest

from pybaseball.teamid_lookup import _front_loaded_ratio, _get_close_team_matches, team_ids


def test_team_id_lookup_all() -> None:
    result = team_ids()

    assert result is not None
    assert not result.empty

    # Remove newer results to ensure we get the count right
    result = result.query('yearID <= 2019')

    assert len(result.columns) == 7
    assert len(result) == 2925


def test_team_id_lookup_season() -> None:
    result = team_ids(2019)

    assert result is not None
    assert not result.empty

    assert len(result.columns) == 7
    assert len(result) == 30


def test_team_id_lookup_league() -> None:
    result = team_ids(league='AL')

    assert result is not None
    assert not result.empty

    # Remove newer results to ensure we get the count right
    result = result.query('yearID <= 2019')

    assert len(result.columns) == 7
    assert len(result) == 1265


def test_team_id_lookup_season_league() -> None:
    result = team_ids(2019, 'NL')

    assert result is not None
    assert not result.empty

    assert len(result.columns) == 7
    assert len(result) == 15

@pytest.mark.parametrize(
    'team1, team2, expected_ratio',
    [
        ['LSA', 'BSA', .58],
        ['BSN', 'BSA', .83],
        ['ABC', 'XYZ', 0],
        ['AA', 'ABC', 0],
        ['A', 'ABC', 0],
        ['AAA', 'AB', 0],
        ['AAA', 'A', 0],
    ]
)

def test_front_loaded_ratio(team1: str, team2: str, expected_ratio: int) -> None:
    if len(team1) == 3 and len(team2) == 3:
        assert round(_front_loaded_ratio(team1, team2), 2) == expected_ratio
    else:
        with pytest.warns(None):
            assert _front_loaded_ratio(team1, team2) == 0

def test_get_close_team_matches():
    lahman_teams = pd.DataFrame(
        [
            {'yearID': 2020, 'franchID': 'ARI', 'teamID': 'ARI', 'teamIDBR': 'ARI', 'name': 'Arizona Diamondbacks', 'initials': 'AD', 'city_start': 'ARI', 'expected': 'ARI'},
            {'yearID': 2020, 'franchID': 'ATL', 'teamID': 'ATL', 'teamIDBR': 'ATL', 'name': 'Atlanta Braves', 'initials': 'AB', 'city_start': 'ATL', 'expected': 'ATL'},
            {'yearID': 2020, 'franchID': 'BAL', 'teamID': 'BAL', 'teamIDBR': 'BAL', 'name': 'Baltimore Orioles', 'initials': 'BO', 'city_start': 'BAL', 'expected': 'BAL'},
            {'yearID': 2020, 'franchID': 'BOS', 'teamID': 'BOS', 'teamIDBR': 'BOS', 'name': 'Boston Red Sox', 'initials': 'BRS', 'city_start': 'BOS', 'expected': 'BOS'},
            {'yearID': 2020, 'franchID': 'CHW', 'teamID': 'CHA', 'teamIDBR': 'CHW', 'name': 'Chicago White Sox', 'initials': 'CWS', 'city_start': 'CHI', 'expected': 'CHW'},
            {'yearID': 2020, 'franchID': 'CHC', 'teamID': 'CHN', 'teamIDBR': 'CHC', 'name': 'Chicago Cubs', 'initials': 'CC', 'city_start': 'CHI', 'expected': 'CHC'},
            {'yearID': 2020, 'franchID': 'CIN', 'teamID': 'CIN', 'teamIDBR': 'CIN', 'name': 'Cincinnati Reds', 'initials': 'CR', 'city_start': 'CIN', 'expected': 'CIN'},
            {'yearID': 2020, 'franchID': 'CLE', 'teamID': 'CLE', 'teamIDBR': 'CLE', 'name': 'Cleveland Indians', 'initials': 'CI', 'city_start': 'CLE', 'expected': 'CLE'},
            {'yearID': 2020, 'franchID': 'COL', 'teamID': 'COL', 'teamIDBR': 'COL', 'name': 'Colorado Rockies', 'initials': 'CR', 'city_start': 'COL', 'expected': 'COL'},
            {'yearID': 2020, 'franchID': 'DET', 'teamID': 'DET', 'teamIDBR': 'DET', 'name': 'Detroit Tigers', 'initials': 'DT', 'city_start': 'DET', 'expected': 'DET'},
            {'yearID': 2020, 'franchID': 'HOU', 'teamID': 'HOU', 'teamIDBR': 'HOU', 'name': 'Houston Astros', 'initials': 'HA', 'city_start': 'HOU', 'expected': 'HOU'},
            {'yearID': 2020, 'franchID': 'KCR', 'teamID': 'KCA', 'teamIDBR': 'KCR', 'name': 'Kansas City Royals', 'initials': 'KCR', 'city_start': 'KAN', 'expected': 'KCR'},
            {'yearID': 2020, 'franchID': 'ANA', 'teamID': 'LAA', 'teamIDBR': 'LAA', 'name': 'Los Angeles Angels of Anaheim', 'initials': 'LAA', 'city_start': 'LOS', 'expected': 'LAA'},
            {'yearID': 2020, 'franchID': 'LAD', 'teamID': 'LAN', 'teamIDBR': 'LAD', 'name': 'Los Angeles Dodgers', 'initials': 'LAD', 'city_start': 'LOS', 'expected': 'LAD'},
            {'yearID': 2020, 'franchID': 'FLA', 'teamID': 'MIA', 'teamIDBR': 'MIA', 'name': 'Miami Marlins', 'initials': 'MM', 'city_start': 'MIA', 'expected': 'MIA'},
            {'yearID': 2020, 'franchID': 'MIL', 'teamID': 'MIL', 'teamIDBR': 'MIL', 'name': 'Milwaukee Brewers', 'initials': 'MB', 'city_start': 'MIL', 'expected': 'MIL'},
            {'yearID': 2020, 'franchID': 'MIN', 'teamID': 'MIN', 'teamIDBR': 'MIN', 'name': 'Minnesota Twins', 'initials': 'MT', 'city_start': 'MIN', 'expected': 'MIN'},
            {'yearID': 2020, 'franchID': 'NYY', 'teamID': 'NYA', 'teamIDBR': 'NYY', 'name': 'New York Yankees', 'initials': 'NYY', 'city_start': 'NEW', 'expected': 'NYY'},
            {'yearID': 2020, 'franchID': 'NYM', 'teamID': 'NYN', 'teamIDBR': 'NYM', 'name': 'New York Mets', 'initials': 'NYM', 'city_start': 'NEW', 'expected': 'NYM'},
            {'yearID': 2020, 'franchID': 'OAK', 'teamID': 'OAK', 'teamIDBR': 'OAK', 'name': 'Oakland Athletics', 'initials': 'OA', 'city_start': 'OAK', 'expected': 'OAK'},
            {'yearID': 2020, 'franchID': 'PHI', 'teamID': 'PHI', 'teamIDBR': 'PHI', 'name': 'Philadelphia Phillies', 'initials': 'PP', 'city_start': 'PHI', 'expected': 'PHI'},
            {'yearID': 2020, 'franchID': 'PIT', 'teamID': 'PIT', 'teamIDBR': 'PIT', 'name': 'Pittsburgh Pirates', 'initials': 'PP', 'city_start': 'PIT', 'expected': 'PIT'},
            {'yearID': 2020, 'franchID': 'SDP', 'teamID': 'SDN', 'teamIDBR': 'SDP', 'name': 'San Diego Padres', 'initials': 'SDP', 'city_start': 'SAN', 'expected': 'SDP'},
            {'yearID': 2020, 'franchID': 'SEA', 'teamID': 'SEA', 'teamIDBR': 'SEA', 'name': 'Seattle Mariners', 'initials': 'SM', 'city_start': 'SEA', 'expected': 'SEA'},
            {'yearID': 2020, 'franchID': 'SFG', 'teamID': 'SFN', 'teamIDBR': 'SFG', 'name': 'San Francisco Giants', 'initials': 'SFG', 'city_start': 'SAN', 'expected': 'SFG'},
            {'yearID': 2020, 'franchID': 'STL', 'teamID': 'SLN', 'teamIDBR': 'STL', 'name': 'St. Louis Cardinals', 'initials': 'SLC', 'city_start': 'ST.', 'expected': 'STL'},
            {'yearID': 2020, 'franchID': 'TBD', 'teamID': 'TBA', 'teamIDBR': 'TBR', 'name': 'Tampa Bay Rays', 'initials': 'TBR', 'city_start': 'TAM', 'expected': 'TBR'},
            {'yearID': 2020, 'franchID': 'TEX', 'teamID': 'TEX', 'teamIDBR': 'TEX', 'name': 'Texas Rangers', 'initials': 'TR', 'city_start': 'TEX', 'expected': 'TEX'},
            {'yearID': 2020, 'franchID': 'TOR', 'teamID': 'TOR', 'teamIDBR': 'TOR', 'name': 'Toronto Blue Jays', 'initials': 'TBJ', 'city_start': 'TOR', 'expected': 'TOR'},
            {'yearID': 2020, 'franchID': 'WSN', 'teamID': 'WAS', 'teamIDBR': 'WSN', 'name': 'Washington Nationals', 'initials': 'WN', 'city_start': 'WAS', 'expected': 'WSN'},
        ]
    )

    fg_teams = pd.DataFrame([
        {'Season': 2020, 'Team': 'CHW'},
        {'Season': 2020, 'Team': 'SDP'},
        {'Season': 2020, 'Team': 'LAD'},
        {'Season': 2020, 'Team': 'ATL'},
        {'Season': 2020, 'Team': 'NYM'},
        {'Season': 2020, 'Team': 'NYY'},
        {'Season': 2020, 'Team': 'OAK'},
        {'Season': 2020, 'Team': 'TBR'},
        {'Season': 2020, 'Team': 'MIN'},
        {'Season': 2020, 'Team': 'SFG'},
        {'Season': 2020, 'Team': 'CHC'},
        {'Season': 2020, 'Team': 'LAA'},
        {'Season': 2020, 'Team': 'STL'},
        {'Season': 2020, 'Team': 'BOS'},
        {'Season': 2020, 'Team': 'KCR'},
        {'Season': 2020, 'Team': 'PHI'},
        {'Season': 2020, 'Team': 'CLE'},
        {'Season': 2020, 'Team': 'HOU'},
        {'Season': 2020, 'Team': 'TOR'},
        {'Season': 2020, 'Team': 'DET'},
        {'Season': 2020, 'Team': 'SEA'},
        {'Season': 2020, 'Team': 'CIN'},
        {'Season': 2020, 'Team': 'ARI'},
        {'Season': 2020, 'Team': 'BAL'},
        {'Season': 2020, 'Team': 'MIL'},
        {'Season': 2020, 'Team': 'MIA'},
        {'Season': 2020, 'Team': 'WSN'},
        {'Season': 2020, 'Team': 'COL'},
        {'Season': 2020, 'Team': 'PIT'},
        {'Season': 2020, 'Team': 'TEX'},
    ])

    for _, row in lahman_teams.iterrows():
        assert _get_close_team_matches(row, fg_teams) == row.expected
