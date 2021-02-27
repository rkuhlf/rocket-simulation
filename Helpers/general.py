from Helpers.variables import *
import Helpers
import re


def interpolate(current_time, start_time, end_time, start_thrust, end_thrust):
    # map the data linearly between the two
    return (current_time - start_time) / (end_time - start_time) * (end_thrust - start_thrust) + start_thrust


def numpy_from_string(x):
    return np.fromstring(
        re.sub(r'[\[\] ]+', ' ', x),
        dtype=float, sep=' ')
