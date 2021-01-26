from pybaseball import amateur_draft
from pybaseball.utils import most_recent_season


def test_amateur_draft() -> None:
    result = amateur_draft(2019, 1)

    assert result is not None
    assert not result.empty

    assert len(result.columns) == 20
    assert len(result) == 41


def test_amateur_draft_no_stats() -> None:
    result = amateur_draft(2019, 1, keep_stats=False)

    assert result is not None
    assert not result.empty

    assert len(result.columns) == 8
    assert len(result) == 41


def test_amateur_draft_future() -> None:
    result = amateur_draft(most_recent_season() + 1, 1, keep_stats=False)

    assert result is not None
    assert not result.empty

    print(result)

    assert len(result.columns) == 8
    assert len(result) == 37
