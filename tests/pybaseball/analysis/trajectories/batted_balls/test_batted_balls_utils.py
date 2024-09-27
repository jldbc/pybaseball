from typing import Tuple

import numpy as np
from numpy import linalg
import pytest

from pybaseball.analysis.trajectories.utils import unit_vector, spin_components


@pytest.mark.parametrize(
    "spin, spin_angle, launch_angle, launch_direction_angle, expected",
    [(0, 1, 1, 1, (0, 0, 0))],
)
# TODO: add additional tests
def test_spin_components(
    spin: np.float64, spin_angle: np.float64, launch_angle: np.float64, launch_direction_angle: np.float64, expected: Tuple) -> None:
    wx, wy, wz = spin_components(spin, spin_angle, launch_angle, launch_direction_angle)
    for a, b in zip((wx, wy, wz), (expected)):
        assert a == pytest.approx(b)


@pytest.mark.parametrize(
    "elevation_angle, azimuthal_angle",
    [(1, 1), (2, 2), (2.71828, 3.14159), (-10, 10), (1e3, 1e-3)],
)
def test_unit_vector(elevation_angle: np.float64, azimuthal_angle: np.float64) -> None:
    velocity_unit_vector = unit_vector(elevation_angle, azimuthal_angle)
    assert linalg.norm(velocity_unit_vector) == pytest.approx(1)
    assert velocity_unit_vector.shape[0] == 3
