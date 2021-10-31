# MISCELLANEOUS HELPERS
# Mostly mathematical, this is where most of the operations for angles are implemented

import re
import numpy as np


def transpose_tuple(iterable):
    iterable = np.array([*iterable])
    return iterable.transpose()


def cylindrical_volume(length, radius):
    return length * np.pi * radius ** 2

def cylindrical_length(volume, radius):
    return volume / (np.pi * radius ** 2)

def get_radius(area):
    # A = pi * r ^ 2
    # sqrt(A/pi) = r
    
    return (area / np.pi) ** (1/2)

# TODO: find a better naming convention for these: maybe the helpers don't need a keyword and I should assume they return a value

def interpolate(x, x1, x2, y1, y2):
    '''Map one point from one range to another'''
    if x2 == x1:
        return (y1 + y2) / 2
    return (x - x1) / (x2 - x1) * (y2 - y1) + y1

def interpolate_point(value, input_min, input_max, p1, p2):
    x = interpolate(value, input_min, input_max, p1[0], p2[0])
    y = interpolate(value, input_min, input_max, p1[1], p2[1])

    return (x, y)

def normalized(array):
    array = array.copy()
    range = np.max(array) - np.min(array)
    array -= np.min(array)
    array /= range
    return array

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


def linear_intersection(p1, m1, p2, m2):
    x1, y1 = p1
    x2, y2 = p2
    # Solve for x
    # m1(x - x1) + y1 = m2(x - x2) + y2
    # m1 * x - m1 * x1 + y1 = m2 * x - m2 * x2 + y2
    # m1 * x - m2 * x = m1 * x1 - y1 - m2 * x2 + y2
    # x * (m1 - m2) = m1 * x1 - y1 - m2 * x2 + y2
    # x = (m1 * x1 - y1 - m2 * x2 + y2) / (m1 - m2)
    x = (m1 * x1 - y1 - m2 * x2 + y2) / (m1 - m2)

    return (x, m1 * (x - x1) + y1)



def numpy_from_string(x):
    return np.fromstring(
        re.sub(r'[\[\] ]+', ' ', x),
        dtype=float, sep=' ')


def magnitude(np_array):
    return np.linalg.norm(np_array)


def angled_cylinder_cross_section(angle, radius, height):
    "When the angle is zero, the rocket is traveling the same way it is pointed, so it is the angle of attack"
    # https://math.stackexchange.com/questions/2336305/cross-section-of-a-cylinder
    area = abs(np.pi * radius * radius * 1 / np.cos(angle))

    # The first calculation assumes the cylinder is infinitely tall
    area = min(area, height * 2 * radius)

    return area


def binary_solve(func, target, min, max, iters=100):
    "Solve for an input on a known domain using binary search"

    # This is my very own idea and I have no idea how efficient or reasonable it is
    while func(max) < target:
        print('doubling')
        max = max + (max - min)

    while func(min) > target:
        min = min - (max - min)

    for i in range(iters):
        guess = func(combine(min, max))

        if guess > target:  # we are overestimating
            max = min + (max - min) / 2
        else:  # we are underestimating
            min = max - (max - min) / 2

    return combine(min, max)


def project(initial, target):
    'Project vector initial onto target vector'

    return (np.dot(initial, target) / np.dot(target, target)) * target


def unit_vector(vector):
    """ Returns the unit vector of the vector.  """
    return vector / magnitude(vector)


def angle_between(v1, v2):
    """ Returns the angle in radians between vectors 'v1' and 'v2'::

            >>> angle_between((1, 0, 0), (0, 1, 0))
            1.5707963267948966
            >>> angle_between((1, 0, 0), (1, 0, 0))
            0.0
            >>> angle_between((1, 0, 0), (-1, 0, 0))
            3.141592653589793
    """
    if (np.isclose(magnitude(v1), 0) or np.isclose(magnitude(v2), 0)):
        return np.pi / 2

    v1_u = unit_vector(v1)
    v2_u = unit_vector(v2)
    return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))


def angles_from_vector_3d(np_array):
    normalized = np_array / magnitude(np_array)
    x, y, z = normalized

    # For some reason the axes lines are poorly defined, so I just encode them manually
    if x == 0:
        if y < 0:
            theta_around = np.pi * 3 / 2
        else:
            theta_around = np.pi / 2
    elif y == 0:
        if x < 0:
            theta_around = np.pi
        else:
            theta_around = 0
    else:
        theta_around = np.arcsin(
            abs(y) / (x ** 2 + y ** 2) ** (1 / 2))

        if x < 0 and y > 0 or x > 0 and y < 0:
            theta_around = (np.pi / 2) - theta_around

        # This sould be oing around in a C pattern
        if x < 0 and y < 0:
            theta_around += np.pi
        elif x < 0:
            theta_around += np.pi / 2
        elif y < 0:
            theta_around += np.pi * 3 / 2

    theta_down = np.arccos(z)


    return np.array([theta_around, theta_down])


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


def vector_from_angle(np_array):
    # I copied it from https://stackoverflow.com/questions/1568568/how-to-convert-euler-angles-to-directional-vector
    around, down = np_array

    x = np.cos(around) * np.sin(down)
    y = np.sin(around) * np.sin(down)
    # I altered this line to cosine from sine - now 0 degrees (straight up, will return 1 in the z axis).
    z = np.cos(down)

    return np.array([x, y, z])


def euler_to_vector_2d(angle):
    """Converts Euler angles (up, right, away) into a unit vector"""
    return np.array(
        [np.cos(angle),  # ajacent / hypotenuse (1)
         np.sin(angle)])  # opposite / hypotenuse (1)


def unit_vector(vector):
    """ Returns the unit vector of the vector.  (Division by magnitude)"""
    return vector / np.linalg.norm(vector)


def combine(a, b):
    """Returns the average of a and b"""
    # Taking the average of the current acceleration and the previous acceleration is a better approximation of the change over the time_interval
    # It is basically a riemann midpoint integral over the acceleration so that it is more accurate finding the change in velocity
    return (a + b) / 2
