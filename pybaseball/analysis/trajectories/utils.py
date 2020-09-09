import numpy as np
from functools import lru_cache
from pybaseball.analysis.trajectories.unit_conversions import (
    RPM_TO_RAD_SEC,
)


@lru_cache(maxsize=64)
def spin_components(
        spin: float, spin_angle: float, launch_angle: float, launch_direction_angle: float) -> np.array:
    """
    given spin in revolutions per minute, spin angle in degrees,
    launch angles in degrees, 
    returns the x,y, z components of spin

    :param spin:
    :param spin_angle:
    :return:
    """

    spin_angle_in_radians = np.deg2rad(spin_angle)
    launch_angle_in_radians = np.deg2rad(launch_angle)
    launch_direction_angle_in_radians = np.deg2rad(launch_direction_angle)

    spin_rad_sec = spin * RPM_TO_RAD_SEC
    sidespin = spin_rad_sec * np.sin(spin_angle_in_radians)
    backspin = spin_rad_sec * np.cos(spin_angle_in_radians)

    wx = (
        backspin * np.cos(launch_direction_angle_in_radians)
        - sidespin * np.sin(launch_angle_in_radians) * np.sin(launch_direction_angle_in_radians)
    )
    wy = (
        - backspin * np.sin(launch_direction_angle_in_radians)
        - sidespin * np.sin(launch_angle_in_radians) * np.cos(launch_direction_angle_in_radians)
    )
    wz = sidespin * np.cos(launch_angle_in_radians)
    return np.array((wx, wy, wz))


def unit_vector(elevation_angle: float, azimuthal_angle: float) -> np.array:
    """
    Returns a 3-dimensional unit vector given the elevation and azimuthal angles.
    The angles must be specified in degrees.

    :param elevation_angle:
    :param azimuthal_angle:
    :return:
    """
    elevation_angle_in_radians = np.deg2rad(elevation_angle)
    azimuthal_angle_in_radians = np.deg2rad(azimuthal_angle)
    return np.array(
        [
            np.cos(elevation_angle_in_radians) * np.sin(azimuthal_angle_in_radians),
            np.cos(elevation_angle_in_radians) * np.cos(azimuthal_angle_in_radians),
            np.sin(elevation_angle_in_radians),
        ]
    )
