from pybaseball.analysis.projections.marcels.age_adjustment import age_adjustment


class TestAgeAdjustment:
    def test_age_adjustment():
        a = 29
        x = 1
        assert age_adjustment(a) == x
