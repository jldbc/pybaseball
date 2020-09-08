import numpy as np
from pybaseball.analysis.trajectories import BattedBallTrajectory
import pytest


def sin_in_degrees(angle):
    return np.sin(np.deg2rad(angle))


def test_batted_ball_init():
    BattedBallTrajectory()


def test_batted_ball_trajectory():
    batted_ball_traj = BattedBallTrajectory()
    launch_angle = 20
    launch_dir = 0
    initial_speed = 100
    initial_spin = 1
    spin_angle = 0
    traj = batted_ball_traj.get_trajectory(
        initial_speed, launch_angle, launch_dir, initial_spin, spin_angle
    )
    assert traj.y.iloc[-1] == pytest.approx(308, 0.5)


def test_projectile_motion():
    batted_ball_traj = BattedBallTrajectory(magnus_strength=0, drag_strength=0)

    launch_angle = 90
    launch_dir = 0
    initial_speed = 100
    initial_spin = 1
    spin_angle = 0
    traj = batted_ball_traj.get_trajectory(
        initial_speed, launch_angle, launch_dir, initial_spin, spin_angle
    )
    assert traj.t.iloc[-1] == pytest.approx(
        2
        * initial_speed
        * batted_ball_traj.env_parameters.unit_conversions.MPH_TO_FTS
        / batted_ball_traj.env_parameters.g_gravity,
        0.5,
    )
    assert traj.z.max() == pytest.approx(
        0.5
        * (initial_speed * batted_ball_traj.env_parameters.unit_conversions.MPH_TO_FTS)
        ** 2
        / batted_ball_traj.env_parameters.g_gravity,
        1,
    )

    launch_angle = 30
    launch_dir = 0
    initial_speed = 100
    initial_spin = 1
    spin_angle = 0
    traj = batted_ball_traj.get_trajectory(
        initial_speed, launch_angle, launch_dir, initial_spin, spin_angle
    )
    assert traj.t.iloc[-1] == pytest.approx(
        2
        * initial_speed
        * batted_ball_traj.env_parameters.unit_conversions.MPH_TO_FTS
        / batted_ball_traj.env_parameters.g_gravity,
        0.5,
    )
    assert traj.z.max() == pytest.approx(
        0.5
        * (
            initial_speed
            * sin_in_degrees(launch_angle)
            * batted_ball_traj.env_parameters.unit_conversions.MPH_TO_FTS
        )
        ** 2
        / batted_ball_traj.env_parameters.g_gravity,
        1,
    )
