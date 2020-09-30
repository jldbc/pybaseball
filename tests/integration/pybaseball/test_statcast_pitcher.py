from pybaseball.statcast_pitcher import statcast_pitcher

def test_statcast_pitcher() -> None:
    result = statcast_pitcher('2019-01-01', '2019-12-31', 605483)

    assert result is not None
    assert not result.empty

    assert len(result.columns) == 89
    assert len(result) == 1982
