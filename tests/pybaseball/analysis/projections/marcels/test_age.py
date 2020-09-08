from pybaseball.analysis.projections.marcels.age_adjustment import age_adjustment


class TestAgeAdjustment:
    def test_age_adjustment(self):
        peak_age = 29
        assert age_adjustment(peak_age) == 1
        assert age_adjustment(peak_age + 1) < 1
        assert age_adjustment(peak_age - 1) > 1
