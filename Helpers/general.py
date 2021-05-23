import re
import numpy as np


def interpolate(x, x1, x2, y1, y2):
    '''Map one point from one range to another'''
    if x2 == x1:
        return (y1 + y2) / 2
    return (x - x1) / (x2 - x1) * (y2 - y1) + y1


def get_next(index, data, previous_index, direction, target):
    """Get the next closest value in a collection of data starting from a cached index"""

    # for some reason this is slower but I don't really care because it is better
    # I think the function call required by recursion might be doing it

    if direction < 0 and data[index] < target:
        return index, previous_index
    elif direction > 0 and data[index] > target:
        return index, previous_index
    else:
        previous_index = index
        index += direction

        return get_next(index, data, previous_index, direction, target)



def numpy_from_string(x):
    return np.fromstring(
        re.sub(r'[\[\] ]+', ' ', x),
        dtype=float, sep=' ')


def angle_from_vector_2d(array):
    if array[0] == 0:
        if array[1] < 0:
            return -np.pi / 2

        # The y component is positive, x is zero, so the angle is 90
        return np.pi / 2

    ratio = array[1] / array[0]
    ans = np.arctan(ratio)

    # numpy inverse tangent ranges from -pi/2 to pi/2, so we have to add back in the negatives to get a full 360
    # Already works perfectly for positive x values
    if array[0] > 0:
        return ans

    # if array[1] < 0:  # both are negative
    #     return np.pi + ans

    return np.pi + ans



def euler_to_vector_2d(angle):
    """Converts Euler angles (up, right, away) into a unit vector"""
    return np.array(
        [np.cos(angle),  # ajacent / hypotenuse (1)
         np.sin(angle)])  # opposite / hypotenuse (1)


def euler_to_vector():
    """Converts Euler angles (up, right, away) into a unit vector"""
    pass


def unit_vector(vector):
    """ Returns the unit vector of the vector.  """
    return vector / np.linalg.norm(vector)


def angle_between(v1, v2):
    # https://stackoverflow.com/questions/2827393/angles-between-two-n-dimensional-vectors-in-python
    """ Returns the angle in radians between vectors 'v1' and 'v2'::

            >>> angle_between((1, 0, 0), (0, 1, 0))
            1.5707963267948966
            >>> angle_between((1, 0, 0), (1, 0, 0))
            0.0
            >>> angle_between((1, 0, 0), (-1, 0, 0))
            3.141592653589793
    """
    v1_u = unit_vector(v1)
    v2_u = unit_vector(v2)
    return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))


def combine(a, b):
    """Returns the average of a and b"""
    # Taking the average of the current acceleration and the previous acceleration is a better approximation of the change over the time_interval
    # It is basically a riemann midpoint integral over the acceleration so that it is more accurate finding the change in velocity
    return (a + b) / 2
