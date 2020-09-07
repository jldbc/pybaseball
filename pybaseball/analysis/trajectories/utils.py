import numpy as np
from functools import lru_cache


@lru_cache(maxsize=64)
def _deg_to_radians(angle_in_degrees):
    return np.deg2rad(angle_in_degrees)


@lru_cache(maxsize=64)
def cos_in_degrees(angle_in_degrees):
    return np.cos(_deg_to_radians(angle_in_degrees))


@lru_cache(maxsize=64)
def sin_in_degrees(angle_in_degrees):
    return np.sin(_deg_to_radians(angle_in_degrees))
