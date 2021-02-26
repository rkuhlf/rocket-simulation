from Helpers.variables import *


def interpolate(current_time, start_time, end_time, start_thrust, end_thrust):
    # map the data linearly between the two
    return (current_time - start_time) / (end_time - start_time) * (end_thrust - start_thrust) + start_thrust


def update_previous():
    p_position = np.copy(position)
    p_velocity = np.copy(velocity)
    p_acceleration = np.copy(acceleration)
