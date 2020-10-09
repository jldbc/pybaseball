from pybaseball.analysis.projections.marcels import MarcelProjectionsPitching
from pandas import DataFrame
import pytest


def test_pitching_bad_data() -> None:
    stats_df = DataFrame({"x": [1, 2, 3]})
    with pytest.raises(ValueError):
        MarcelProjectionsPitching(stats_df=stats_df)
