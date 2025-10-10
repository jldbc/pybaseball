import pytest

from pybaseball import fg_projections


def test_get_projections_batters_via_default_args() -> None:
    result = fg_projections()

    assert result is not None
    assert not result.empty

    assert len(result.columns) == 51

    if 'AVG' not in result.columns:
        pytest.fail("Could not find AVG column in batters only projections")


def test_get_projections_pitchers_only() -> None:
    result = fg_projections("pitchers")

    assert result is not None
    assert not result.empty

    assert len(result.columns) == 41

    if 'ERA' not in result.columns:
        pytest.fail("Could not find ERA column in pitchers only projections")
