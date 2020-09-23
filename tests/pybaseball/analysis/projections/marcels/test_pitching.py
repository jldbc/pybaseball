from pybaseball.analysis.projections.marcels import MarcelProjectionsPitching
from pandas import DataFrame
import pytest


class TestMarcelPitching:
    def test_pitching_projections_season(self):
        md = MarcelProjectionsPitching()
        md.projections(2020)

    @pytest.mark.parametrize(
        "season, expected",
        [(2020, 242), (2019, 235), (2018, 229), (2017, 224), (2004, 207)],
    )
    def test_pitching_metric_projections(self, season, expected):

        md = MarcelProjectionsPitching()
        proj = md.metric_projection("SO", season)
        assert round(proj.SO.max()) == expected

    def test_pitching_bad_data(self):
        stats_df = DataFrame({"x": [1, 2, 3]})
        with pytest.raises(ValueError):
            MarcelProjectionsPitching(stats_df=stats_df)
