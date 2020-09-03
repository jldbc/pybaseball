import numpy as np
from functools import partial


def _trig_in_degrees(trig_func, angle_in_degrees):
    return trig_func(np.deg2rad(angle_in_degrees))


cos_in_degrees = partial(_trig_in_degrees, np.cos)
sin_in_degrees = partial(_trig_in_degrees, np.sin)
