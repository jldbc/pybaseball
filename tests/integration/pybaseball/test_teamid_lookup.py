from pybaseball.teamid_lookup import _generate_fangraphs_teams


def test_generate_fangraphs_teams() -> None:
    result = _generate_fangraphs_teams()

    assert result is not None
    assert not result.empty

    # Remove newer results to ensure we get the count right
    result = result.query('yearID <= 2019')

    assert len(result.columns) == 5
    assert len(result) == 2943
