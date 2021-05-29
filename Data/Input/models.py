# Stores the fitted polynomials that are outputted from fitPolynomial.py
# They have to be transferred manually

import numpy as np



def get_density(altitude):
    return np.polyval([0.00287959, -0.1096957, 1.21608074], altitude)


def get_speed_of_sound(altitude):
    # For some reason it flattens out here
    if (altitude > 11):
        altitude = 11

    return np.polyval(
        [-2.64851747e-02, - 3.81579975e+00, 3.40273658e+02],
        altitude)



def get_coefficient_of_drag(mach, angle_of_attack=0):
    # Currently using the data from the Raven.CDX1 example RasAero file
    # laminar
    if mach < 1.05:
        return np.polyval(
            [4.70927343, -12.39902486, 12.82128281, -5.79253425, 1.00385474,
             1.01004552],
            mach)

    return np.polyval(
        [-1.70456402e-06, 1.30617668e-04, -3.86403536e-03, 5.54072679e-02, -
         3.91568896e-01, 1.60204340e+00],
        mach)
