from pybaseball.analysis.projections.marcels import MarcelProjectionsBatting
from pandas import DataFrame
import pytest


class TestMarcelBatting:
    def test_batting_projections_season():
        md = MarcelProjectionsBatting()
        md.projections(2020)

    @pytest.mark.parametrize(
        "season, expected", [(2020, 36), (2019, 38), (2018, 41), (2017, 34), (2004, 42)]
    )
    def test_batting_metric_projections(season, expected):

        md = MarcelProjectionsBatting()
        proj = md.metric_projection("HR", season)
        assert round(proj.HR.max()) == expected

    def test_batting_bad_data():
        stats_df = DataFrame({"x": [1, 2, 3]})
        with pytest.raises(ValueError):
            MarcelProjectionsBatting(stats_df=stats_df)
