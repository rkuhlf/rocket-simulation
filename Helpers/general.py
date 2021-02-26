from Helpers.variables import *
import Helpers


def interpolate(current_time, start_time, end_time, start_thrust, end_thrust):
    # map the data linearly between the two
    return (current_time - start_time) / (end_time - start_time) * (end_thrust - start_thrust) + start_thrust
