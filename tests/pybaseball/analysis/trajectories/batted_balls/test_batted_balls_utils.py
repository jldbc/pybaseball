from pybaseball.analysis.trajectories.utils import cos_in_degrees, sin_in_degrees
from math import sqrt
import pytest


def test_trig_utils():
    deg = 1
    assert cos_in_degrees(deg) ** 2 + sin_in_degrees(deg) ** 2 == 1

    deg = 30
    assert cos_in_degrees(deg) == pytest.approx(sqrt(3) / 2)
    assert sin_in_degrees(deg) == pytest.approx(1 / 2)

    deg = 45
    assert cos_in_degrees(deg) == pytest.approx(1 / sqrt(2))
    assert sin_in_degrees(deg) == pytest.approx(1 / sqrt(2))
