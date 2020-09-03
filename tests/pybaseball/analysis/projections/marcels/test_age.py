from pybbda.analysis.projections.marcels.age_adjustment import age_adjustment


def test_age_adjustment():
    a = 29
    x = 1
    assert age_adjustment(a) == x
