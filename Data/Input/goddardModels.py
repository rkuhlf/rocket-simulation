# DATA MODELS FOR GODDARD SIMULATIONS
# Center of pressure and drag coefficient come from other sources, I define how to look them up here

# Stores the fitted polynomials that are outputted from fitPolynomial.py
# They have to be transferred manually

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from math import isnan


from Helpers.data import interpolated_lookup, interpolated_lookup_2D


# This code should run regardless of how you import this file
# The idea is that it is a drop-in replacement for the RASAero data whenever you want to do it
data = pd.read_csv('Data/Input/aerodynamicQualities.csv')
mach = data['Mach']
alpha = data['Alpha']
# TODO: add the difference; should be the last fix (unless drag is really messed up)
CD = data['CD Power-Off']
CL = data['CL']
CP = data['CP']


def get_sine_interpolated_center_of_pressure(mach, alpha):
    # I believe the self is necessary for using as a class function
    if isnan(alpha):
        raise Exception("Your angle of attack is NaN")

    degrees = alpha * 180 / np.pi

    upside_down = 5.29
    perpendicular_AOA = 3.3

    if degrees > 90:
        # We are just going to do some sine interpolation to put CP where the fins are, I don't really know
        return upside_down + np.sin(alpha) * (perpendicular_AOA - upside_down)

    # We don't have any data for lookups beyond four
    if degrees > 4:
        zero_AOA = interpolated_lookup(data, "Mach", mach, "CP") * 0.0254
        # Hard coding in 3.3 meters for the center of pressure at angle of attack of 90 degrees
        # This is based off of what openrocket looks like
        

        return zero_AOA + np.sin(alpha) * (perpendicular_AOA - zero_AOA)

    
    # We know alpha is small enough to be contained in the RASAero data
    return interpolated_lookup_2D(data, "Mach", "Alpha", mach, degrees, "CP")  * 0.0254


def linear_approximated_normal_force(mach, alpha):
    # This is giving values way higher than Open Rocket seems to be using
    # This is literally the only issue in the entire model. For some inexplicable reason the lift force coefficient works if it is a factor of 1000 smaller
    # I am getting values around a max of five outputted from OpenRocket
    return np.sin(alpha) * interpolated_lookup(data, "Mach", mach, "CNalpha (0 to 4 deg) (per rad)")


def assumed_zero_AOA_CD(mach, alpha):
    # Hopefully angle of attack never gets so high that this assumption is a major issue
    return interpolated_lookup(data, "Mach", mach, "CD")

    

def display_sine_interpolation():
    # Unfortunately, this is really slow. Also, based on the visual, something is ever so slightly broken (some of the lines aren't between the dots). To be honest, it is close enough for now
    alphas = np.linspace(0, 4 * np.pi / 180, 5)
    machs = np.linspace(0, 15, 100)

    for m in machs:
        outputs = []
        for a in alphas:
            outputs.append(get_sine_interpolated_center_of_pressure(m, a))

        plt.plot(alphas, outputs)

    for m in machs:
        mach_isoline = data[np.abs(data["Mach"] - m) < 0.01]
        plt.scatter(mach_isoline["Alpha"] * np.pi / 180, mach_isoline["CP"])

    plt.show()


if __name__ == '__main__':
    display_sine_interpolation()
