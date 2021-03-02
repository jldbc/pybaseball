from pybaseball.teamid_lookup import team_ids


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
