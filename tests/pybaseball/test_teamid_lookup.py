from pybaseball.teamid_lookup import fangraphs_teams


def test_team_id_lookup_all() -> None:
    result = fangraphs_teams()

    assert result is not None
    assert not result.empty

    # Remove newer results to ensure we get the count right
    result = result.query('yearID <= 2019')

    assert len(result.columns) == 5
    assert len(result) == 2943

def test_team_id_lookup_season() -> None:
    result = fangraphs_teams(2019)

    assert result is not None
    assert not result.empty

    assert len(result.columns) == 5
    print(result)
    assert len(result) == 30

def test_team_id_lookup_league() -> None:
    result = fangraphs_teams(league='AL')

    assert result is not None
    assert not result.empty

    # Remove newer results to ensure we get the count right
    result = result.query('yearID <= 2019')

    assert len(result.columns) == 5
    assert len(result) == 1265

def test_team_id_lookup_season_league() -> None:
    result = fangraphs_teams(2019, 'NL')

    assert result is not None
    assert not result.empty

    assert len(result.columns) == 5
    
    print(result)
    assert len(result) == 15
