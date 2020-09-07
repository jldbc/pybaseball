import attr
from functools import partial
from scipy.integrate import RK45
import numpy as np
import pandas as pd
from pybaseball.datahelpers.postprocessing import check_between_zero_one
from pybaseball.analysis.trajectories.utils import cos_in_degrees, sin_in_degrees
from .parameters import (
    BattedBallConstants,
    DragForceCoefficients,
    LiftForceCoefficients,
    EnvironmentalParameters,
)


@attr.s(kw_only=True)
class BattedBallTrajectory:
    """
    Class for a batted ball trajectory. The algorithm is taken from
    Alan Nathan's trajectory calculator,
    http://baseball.physics.illinois.edu/trajectory-calculator-new.html

    """

    x0 = attr.ib(default=0, metadata={"units": "ft"})
    y0 = attr.ib(default=2.0, metadata={"units": "ft"})
    z0 = attr.ib(default=3.0, metadata={"units": "ft"})
    spin = attr.ib(default=2675, metadata={"units": "revs_per_second"})
    spin_phi = attr.ib(default=-18.5, metadata={"units": "degrees"})
    drag_strength = attr.ib(default=1, validator=check_between_zero_one)
    magnus_strength = attr.ib(default=1, validator=check_between_zero_one)
    batted_ball_constants = attr.ib(default=BattedBallConstants())
    drag_force_coefs = attr.ib(default=DragForceCoefficients())
    lift_force_coefs = attr.ib(default=LiftForceCoefficients())
    env_parameters = attr.ib(default=EnvironmentalParameters())

    def __attrs_post_init__(self):
        self.initial_position = np.array((self.x0, self.y0, self.z0))
        self.pi_30 = np.pi / 30
        self.c0 = (
            0.07182
            * self.env_parameters.air_density
            * self.env_parameters.unit_conversions.KGM3_TO_LBFT3
            * (5.125 / self.batted_ball_constants.mass)
            * (self.batted_ball_constants.circumference / 9.125) ** 2
        )

    def omega_fun(self, t, spin):
        """
        angular speed.

        :param t: float
        :param spin: float
        :return: float
        """
        return spin * np.pi / 30

    def s_fun(self, t, vw, spin):
        """
        spin. computed as a function of `t`, the time,
        `vw` speed with respect to the wind, and `spin`, the initial spin

        :param t: float
        :param vw: float
        :param spin: float
        :return: float
        """
        omega = self.omega_fun(t, spin)
        romega = self.batted_ball_constants.circumference * omega / (24 * np.pi)
        return (romega / vw) * np.exp(-t * vw / (self.lift_force_coefs.tau * 146.7))

    def cl_fun(self, t, vw, spin):
        """
        coefficient of lift. computed as a function of `t`, the time,
        `vw` speed with respect to the wind, and `spin`, the spin

        :param t: float
        :param vw: float
        :param spin: float
        :return: float
        """
        s = self.s_fun(t, vw, spin)
        return (
            self.lift_force_coefs.cl2
            * s
            / (self.lift_force_coefs.cl0 + self.lift_force_coefs.cl1 * s)
        )

    def cd_fun(self, t, vw, spin):
        """
        coefficient of drag. computed as a function of `t`, the time,
        `vw`, the speed with respect to the wind, and `spin`, the spin.

        :param t: float
        :param vw: float
        :param spin: float
        :return: float
        """
        return self.drag_force_coefs.cd0 + self.drag_force_coefs.cdspin * (
            spin * 1e-3
        ) * np.exp(-t * vw / (self.lift_force_coefs.tau * 146.7))

    def get_trajectory(
        self,
        initial_speed,
        launch_angle,
        launch_direction_angle,
        initial_spin,
        spin_angle,
        delta_time=0.01,
    ):
        # TODO: make the return value a trajectory object
        """
        computes a batted ball trajectory. speed is in miles-per-hour,
        angles in degrees, and spin in revolutions per minute

        :param initial_speed: float
        :param launch_angle: float
        :param launch_direction_angle: float
        :param initial_spin: float
        :param spin_angle: float
        :param delta_time: float
        :return: pandas data frame
        """

        initial_velocity = (
            initial_speed
            * self.env_parameters.unit_conversions.MPH_TO_FTS
            * np.array(
                [
                    cos_in_degrees(launch_angle)
                    * sin_in_degrees(launch_direction_angle),
                    cos_in_degrees(launch_angle)
                    * cos_in_degrees(launch_direction_angle),
                    sin_in_degrees(launch_angle),
                ]
            )
        )

        initial_conditions = np.concatenate(
            (self.initial_position, initial_velocity), axis=0
        )

        rk_solution = RK45(
            partial(
                self.trajectory_fun,
                launch_angle=launch_angle,
                launch_direction_angle=launch_direction_angle,
                spin=initial_spin,
                spin_angle=spin_angle,
            ),
            0,
            initial_conditions,
            t_bound=1000,
            max_step=delta_time,
        )
        ans = []
        z = self.initial_position[2]
        while z >= 0:
            rk_solution.step()
            res = rk_solution.y
            z = res[2]
            ans.append([rk_solution.t] + list(res))
        result_df = pd.DataFrame(np.array(ans).reshape(-1, 7))
        result_df.columns = ["t", "x", "y", "z", "vx", "vy", "vz"]
        return result_df

    def trajectory_fun(
        self,
        t,
        trajectory_vars,
        spin=2500,
        spin_angle=0,
        launch_angle=0,
        launch_direction_angle=0,
    ):
        """
        function for computing the trajectory using the 4th-order Runge-Kutta method.
        trajectory vars are the 3 positions and 3 velocity components of the ball.
        returns the derivatives of the input variables, i.e., the 3 velocity components,
        and the 3 acceleration components.

        :param t: float
        :param trajectory_vars: tuple(float)
        :param spin: float
        :param spin_angle: float
        :param launch_angle: float
        :param launch_direction_angle: float
        :return: numpy array
        """
        # trajectory_vars = x, y, z, vx, vy, vz
        _, _, _, vx, vy, vz = trajectory_vars
        v = np.sqrt(vx ** 2 + vy ** 2 + vz ** 2)

        sidespin = spin * sin_in_degrees(spin_angle)
        backspin = spin * cos_in_degrees(spin_angle)

        wb = backspin
        ws = sidespin

        wx = (
            (
                wb * cos_in_degrees(launch_direction_angle)
                - ws
                * sin_in_degrees(launch_angle)
                * sin_in_degrees(launch_direction_angle)
            )
            * np.pi
            / 30
        )
        wy = (
            (
                -wb * sin_in_degrees(launch_direction_angle)
                - ws
                * sin_in_degrees(launch_angle)
                * cos_in_degrees(launch_direction_angle)
            )
            * np.pi
            / 30
        )
        wz = ws * cos_in_degrees(launch_angle) * np.pi / 30

        cd = self.cd_fun(t, v, spin)
        cl = self.cl_fun(t, v, spin)

        magnus_const = self.c0 * cl / self.omega_fun(t, spin) * v
        magnus_const *= self.magnus_strength

        drag_const = self.c0 * cd * v
        drag_const *= self.drag_strength
        fx = -drag_const * vx + magnus_const * (wy * vz - wz * vy)

        fy = -drag_const * vy + magnus_const * (-wx * vz + wz * vx)

        fz = (
            -drag_const * vz
            + magnus_const * (wx * vy - wy * vx)
            - self.env_parameters.g_gravity
        )

        gx = vx
        gy = vy
        gz = vz

        return np.array([gx, gy, gz, fx, fy, fz])
