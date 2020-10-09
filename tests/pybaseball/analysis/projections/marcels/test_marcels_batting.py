from pybaseball.analysis.projections.marcels import MarcelProjectionsBatting
from pandas import DataFrame
import pytest


def test_batting_bad_data() -> None:
    stats_df = DataFrame({"x": [1, 2, 3]})
    with pytest.raises(ValueError):
        MarcelProjectionsBatting(stats_df=stats_df)
