import attr
import numpy as np
from pybaseball.datahelpers.postprocessing import check_greater_zero
from pybaseball.analysis.trajectories import unit_conversions


@attr.s(frozen=True, kw_only=True)
class BattedBallConstants:
    mass: float = attr.ib(
        default=5.125, validator=check_greater_zero, metadata={"units": "oz"}
    )
    circumference: float = attr.ib(
        default=9.125, validator=check_greater_zero, metadata={"units": "in"}
    )


@attr.s(frozen=True, kw_only=True)
class DragForceCoefficients:
    cd0: float = attr.ib(default=0.3008)
    cdspin: float = attr.ib(default=0.0292)


@attr.s(frozen=True, kw_only=True)
class LiftForceCoefficients:
    cl0: float = attr.ib(default=0.583)
    cl1: float = attr.ib(default=2.333)
    cl2: float = attr.ib(default=1.120)
    tau: float = attr.ib(default=10000, metadata={"units": "seconds"})


@attr.s(kw_only=True)
class EnvironmentalParameters:
    # environmental parameters
    g_gravity: float = attr.ib(default=32.174, metadata={"units": "ft_per_s_per_s"})
    vwind: float = attr.ib(default=0, metadata={"units": "mph"})  # mph
    phiwind: float = attr.ib(default=0, metadata={"units": "deg"})  # deg
    hwind: float = attr.ib(default=0, metadata={"units": "ft"})  # ft
    relative_humidity: float = attr.ib(default=50)
    pressure_in_hg: float = attr.ib(default=29.92)
    temperature_f: float = attr.ib(default=70, metadata={"units": "F"})  # F
    elevation_ft: float = attr.ib(default=15, metadata={"units": "ft"})
    beta: float = attr.ib(
        default=1.217e-4, validator=check_greater_zero, metadata={"units": "per_meter"}
    )

    def __attrs_post_init__(self) -> None:
        self.unit_conversions = unit_conversions
        self.elevation_m = self.elevation_ft * self.unit_conversions.FT_TO_M
        self.temperature_c = (self.temperature_f - 32) * 5 / 9
        self.pressure_mm_hg = self.pressure_in_hg * 1000 / 39.37
        self.SVP = 4.5841 * np.exp(
            (18.687 - self.temperature_c / 234.5)
            * self.temperature_c
            / (257.14 + self.temperature_c)
        )

        self.air_density = 1.2929 * (
            273.15
            / (self.temperature_c + 273.15)
            * (
                self.pressure_mm_hg * np.exp(-self.beta * self.elevation_m)
                - 0.3783 * self.relative_humidity * self.SVP * 0.01
            )
            / 760
        )
