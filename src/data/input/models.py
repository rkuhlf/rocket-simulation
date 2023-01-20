# Stores the fitted polynomials that are outputted from fitPolynomial.py
# They have to be transferred manually

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d, interp2d, fitpack, bisplrep, bisplev
from math import isnan


from helpers.data import interpolated_lookup, interpolated_lookup_2D


# This code should run regardless of how you import this file
data = pd.read_csv('Data/Input/aerodynamicQualities.csv')
mach = data['Mach']
alpha = data['Alpha']
CD = data['CD']
CL = data['CL']
CP = data['CP']


def get_density(altitude: float):
    ":param: float altitude in kilometers"
    return np.polyval([0.00287959, -0.1096957, 1.21608074], altitude)


def get_speed_of_sound(altitude):
    """Altitude in kilometers"""
    # For some reason it flattens out here
    if (altitude > 11):
        altitude = 11

    return np.polyval(
        [-2.64851747e-02, - 3.81579975e+00, 3.40273658e+02],
        altitude)


# def get_coefficient_of_drag(mach, angle_of_attack=0):
#     # Currently using the data from the Raven.CDX1 example RasAero file
#     # There are two ways to go about simulating coefficient of drag. You can use hard-coded values, from data collected by Rasaero or simulated by CFD (or just some random constant). You could use data for the five separate components (form, skin friction, base, wave, and excresense), adjusted for probable errors, collected from various websites like the ESDU (explained page 46ish of http://www.aspirespace.org.uk/downloads/Rocketry%20aerodynamics.pdf).
#     # For this project, I am only going to code in CSV reading with the idea of confirming rasaero stuff with CFD
#     # laminar
#     if mach < 1.05:
#         return np.polyval(
#             [4.70927343, -12.39902486, 12.82128281, -5.79253425, 1.00385474,
#              1.01004552],
#             mach)
#     return np.polyval(
#         [-1.70456402e-06, 1.30617668e-04, -3.86403536e-03, 5.54072679e-02, -
#          3.91568896e-01, 1.60204340e+00],
#         mach)

# FIXME: For some reason tis has unpredictable and concerning behavior. Try messing with s. I don't see why linearly interpolating 2d inputs is so hard. Half tempted to implement my own solution.
# Note that CD doesn't change with angle but CA does
drag_spline = bisplrep(mach, alpha, CD, kx=1, ky=1, s=0.3)


def get_splined_coefficient_of_drag(mach, alpha):
    if isnan(alpha):
        raise Exception("Your angle of attack is NaN")

    alpha = alpha / np.pi * 180
    return bisplev(mach, alpha, drag_spline)


def get_sine_interpolated_coefficient_of_drag(mach, alpha):
    if isnan(alpha):
        raise Exception("Your angle of attack is NaN")
    


    



lift_spline = bisplrep(mach, alpha, CL, kx=2, ky=2, s=0.1)


def get_coefficient_of_lift(mach, alpha):
    alpha = alpha / np.pi * 180
    return bisplev(mach, alpha, lift_spline)


# region lift
"""
coords = [
    -0.0664, 0,
    0.00947, 0.900636, 0.0183, 1.00537, 0.031, 1.05994, 0.0425, 1.07916,
    0.0504, 1.08585, 0.0576, 1.08763, 0.0709, 1.08633, 0.0799, 1.08428,
    0.1734, 1.0572, 0.2203, 1.04842, 0.2853, 1.04026, 0.3305, 1.03797,
    0.381, 1.0365, 0.4424, 1.03937, 0.499, 1.0436, 0.5833, 1.05822, 0.6495,
    1.07973, 0.6794, 1.09261, 0.6897, 1.09689, 0.7018, 1.102, 0.8007,
    1.08501, 0.9693, 1.32587, 1.048, 1.4036, 1.1889, 1.32451, 1.401,
    1.1858, 1.574, 1.0957, 1.708, 1.0399, 1.894, 0.9803, 2.134, 0.9305,
    2.43, 0.8822, 2.752, 0.8443, 2.988, 0.808, 3.458, 0.7558, 4.22, 0.6919,
    4.638, 0.6615, 5.209, 0.6257, 6.14, 0.5771, 7.24, 0.5404, 8.561,
    0.5101, 9.957, 0.488, 14.336, 0.4738, 24.996, 0.4635]


x_coords = coords[::2]
y_coords = coords[1::2]


# Eventually tis needs to be an interp2d
# Add in a linear interpolation between eac of te different anles of attack at all mac values
# get_coefficient_of_drag = interp1d(x_coords, y_coords, assume_sorted=True)

# x coords are te mac value, y is C, z is anle
# coordinates for AOA = 2
coords_4 = [-0.0052, 0.92483, 0.0088, 0.91593, 0.0279, 0.90432, 0.0441,
            0.90244, 0.08, 0.903, 0.413, 0.9083, 0.676, 0.901, 0.807, 0.9046,
            0.91, 0.8908, 1.053, 1.1872, 1.156, 1.1856, 1.43, 1.1875, 1.787,
            1.1557, 2.713, 1.0522, 3.05, 0.9781, 3.576, 0.8471, 4.209, 0.7715,
            4.965, 0.7101, 5.735, 0.6404, 6.66, 0.718, 7.174, 0.7694, 7.792,
            0.7478, 8.57, 0.734, 9.826, 0.6905, 11.457, 0.6469, 14.25, 0.565,
            17.355, 0.5104, 21.46, 0.464, 25.03, 0.44]

x_coords = coords_4[::2]
y_coords = coords_4[1::2]

get_coefficient_of_lift_4 = interp1d(x_coords, y_coords)

coords_2 = [-0.0012, 0.46335, 0.0199, 0.45509, 0.0437, 0.45221, 0.399, 0.4545,
            0.8072, 0.4524, 0.8997, 0.44706, 1.0501, 0.53453, 1.7609, 0.5342,
            2.7238, 0.5238, 3.947, 0.4241, 4.935, 0.3668, 6.081, 0.307, 7.148,
            0.2605, 9.52, 0.21, 11.46, 0.186, 14.334, 0.2148, 25.001, 0.17378]

x_coords = coords_2[::2]
y_coords = coords_2[1::2]

get_coefficient_of_lift_2 = interp1d(x_coords, y_coords)


def get_coefficient_of_lift_0(mach):
    return 0


def get_coefficient_of_lift(mach, angle_of_attack=0):
    # Could probably create a list of functions, mapped to a list of anle data
    # Tis is very brute forcin
    interp = 0
    if angle_of_attack <= 2:
        interp = angle_of_attack / 2

        return get_coefficient_of_lift_0(mach) * (
            1 - interp) + get_coefficient_of_lift_2(mach) * interp

    interp = (angle_of_attack - 2) / 2
    return get_coefficient_of_lift_2(mach) * (
        1 - interp) + get_coefficient_of_lift_4(mach) * interp
"""
# endregion



def display_CD():
    plt.scatter(mach, CD, label="data")

    get_coefficient_of_drag = get_splined_coefficient_of_drag

    x_points = np.linspace(0, 25, 100)

    y_points = get_coefficient_of_drag(x_points, 0)
    plt.plot(x_points, y_points.flatten(), label="0")

    y_points = get_coefficient_of_drag(x_points, 1)
    plt.plot(x_points, y_points.flatten(), label="1")

    y_points = get_coefficient_of_drag(x_points, 2)
    plt.plot(x_points, y_points.flatten(), label="2")

    y_points = get_coefficient_of_drag(x_points, 2.5)
    plt.plot(x_points, y_points.flatten(), label="2.5")

    y_points = get_coefficient_of_drag(x_points, 3)
    plt.plot(x_points, y_points.flatten(), label="3")

    y_points = get_coefficient_of_drag(x_points, 3.5)
    plt.plot(x_points, y_points.flatten(), label="3.5")

    y_points = get_coefficient_of_drag(x_points, 4)
    plt.plot(x_points, y_points.flatten(), label="4")

    plt.legend()

    plt.show()
    # TODO: Calc how accurate my function is; Average absolute error


if __name__ == '__main__':
    # display_CD()
    pass
