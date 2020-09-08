from attr.exceptions import FrozenInstanceError
from pybaseball.analysis.trajectories.batted_balls.parameters import BattedBallConstants
import pytest


def test_batted_ball_constants():
    b = BattedBallConstants()
    with pytest.raises(FrozenInstanceError):
        b.mass = 1

    with pytest.raises(ValueError):
        b = BattedBallConstants(mass=-1)
