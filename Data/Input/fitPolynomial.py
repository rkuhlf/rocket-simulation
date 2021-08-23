# Unfortunately, I have some models that were made using lmfit and some that were made using np polynomials. In te future I would like to use lmfit

from numpy.polynomial import Polynomial
from numpy import polyval
import pandas as pd
import numpy as np
import lmfit
import matplotlib.pyplot as plt


def fit_density():
    # If you are using VS Code, paths are relative to the project folder
    data = pd.read_csv("Data/Input/airQuantities.csv")

    print(data["Altitude"])
    print(data["Density"])

    # Learn what a Chebyshev poly is
    # c = Chebyshev.fit(data["Altitude"], data["Density"], deg=2)
    p = np.polyfit(data["Altitude"], data["Density"], deg=2)

    print(p)
    # print(p(2))

    # p2 = np.polynomial.Polynomial([0.62472132, -0.4696968, 0.12166262])


def fit_altitude_mach():
    data = pd.read_csv("Data/Input/airQuantities.csv")

    data = data[data["Altitude"] < 11]

    p = np.polyfit(data["Altitude"], data["Speed of sound"], deg=2)

    print(p)


def fit_coefficient_of_drag():
    # TODO: This is really not great. Make a better mapping function
    # I could do my own if statement regression thing, but I think it is just easiest to hard code it
    turbulent_flow = 1.05  # mach

    data = pd.read_csv("Data/Input/aerodynamicQualities.csv")

    laminar = data[data["Mach"] < turbulent_flow]
    turbulent = data[data["Mach"] >= turbulent_flow]

    p = np.polyfit(laminar["Mach"], laminar["CD"], deg=5)
    print(p)

    p = np.polyfit(turbulent["Mach"], turbulent["CD"], deg=5)
    print(p)


def combine_parameters(a, b):
    # merges two parameters objects
    pass


def fit_coefficient_of_lift():
    # This idea is inspired by the metod that was developed for calculatin the eventual height of a child given data points
    # Basically you just add in different components of the equation once you get to the cutoff
    # Te cutoff can also be fit, but I tink having good guesses will make it a lot better
    # The only issue is that all of the functions have to approach a constant value when they approac infinity
    # Maybe we can even interpolate between adding each function in. Definitely do tis - problem described by https://stackoverflow.com/questions/54507297/piecewise-function-lmfit would be solved
    # It could be done through multiplication by a step model in lmfit. I am familiar wit logistic and linear models
    # I tink loistic is infinitely smoot

    # One function to match the main subsonic curve
    # One function that only has an impact up to a point to fit the teeny loop at the beginning
    # One function that only has an affect at supersonic speeds
    # See if tere is conditional addin for lmfit functions

    data = pd.read_csv("Data/Input/aerodynamicQualities.csv")
    x = data["Mach"]
    y = data["CD"]
    weights = np.linspace(1, 0.5, num=len(x))

    # Tis is were meta-prorammin would be reat, since we need to make functions wit unique aruments. Also for constructin te polynomials more easily

    def low_speed_interpolator_func(
            x, low_speed_amplitude, low_speed_center, low_speed_deviation):

        normalized_value = (x - low_speed_center) / low_speed_deviation

        normalized_value[normalized_value < 0] = 0

        normalized_value[normalized_value > 1] = 1

        return low_speed_amplitude * normalized_value

    low_speed_interpolator = lmfit.Model(low_speed_interpolator_func)
    # Make the amplitude parameter fixed


    def transonic_interpolator_func(
            x, transonic_amplitude, transonic_center, transonic_deviation):

        normalized_value = (x - transonic_center) / transonic_deviation
        normalized_value[normalized_value < 0] = 0

        normalized_value[normalized_value > 1] = 1

        return transonic_amplitude * normalized_value

    transonic_interpolator = lmfit.Model(transonic_interpolator_func)
    print(transonic_interpolator.param_names)

    def low_speed_func(
            x, c_low_speed0, c_low_speed1, c_low_speed2, c_low_speed3):

        return c_low_speed0 + c_low_speed1 * x ** 1 + c_low_speed2 * x ** 2 + c_low_speed3 * x ** 3

    low_speed = lmfit.Model(low_speed_func)
    print(low_speed.param_names)

    def base_subsonic_func(
            x, c_base_subsonic0, c_base_subsonic1, c_base_subsonic2,
            c_base_subsonic3):

        return (c_base_subsonic0 + c_base_subsonic1 * x ** 1) / (c_base_subsonic2 + c_base_subsonic3 * x ** 1)

    base_subsonic = lmfit.Model(base_subsonic_func)
    print(base_subsonic.make_params())

    def transonic_func(
            x, c_transonic0, c_transonic1, c_transonic2,
            c_transonic3):

        return (c_transonic0 + c_transonic1 * x ** 1) / (c_transonic2 + c_transonic3 * x ** 1)

    transonic = lmfit.Model(transonic_func)

    # + transonic_interpolator * transonic
    model = low_speed_interpolator * low_speed + base_subsonic + transonic_interpolator * transonic

    print(model.components)


    # Determine reasonable initial values for parameters
    # I tink I actually want to mere all of te oter parameters
    params = model.make_params()
    # Amplitudes should only go between 0 and 1
    params['transonic_amplitude'].set(value=1, vary=False)
    params['transonic_center'].set(value=0.9, vary=True, min=0.7, max=1.1)
    params['transonic_deviation'].set(value=0.18, vary=True, min=0, max=0.4)

    # Do differently so it always starts at one and ends at zero some unknown distance away
    # Amplitude is neative so it decreases
    params['low_speed_amplitude'].set(value=-1, vary=False)
    params['low_speed_center'].set(value=0, vary=True, min=0, max=0.2)
    params['low_speed_deviation'].set(value=0.15, vary=True, min=0, max=0.5)


    # Polynomial coefficients are all based on simple principles
    params['c_low_speed0'].set(value=-0.01, vary=True)
    params['c_low_speed1'].set(value=0.0, vary=True)
    params['c_low_speed2'].set(value=0.0, vary=True)
    params['c_low_speed3'].set(value=0.0, vary=True)

    params['c_transonic0'].set(value=0.4, vary=True)
    params['c_transonic1'].set(value=0.0, vary=True)
    params['c_transonic2'].set(value=1.0, vary=True)
    params['c_transonic3'].set(value=0.0, vary=True)

    # Frankly, te base subsonic is te main problem for poor fittin. It sould be different - rit now it tends towards infinities on eiter side
    params['c_base_subsonic0'].set(value=0.2, vary=True)
    params['c_base_subsonic1'].set(value=0.0, vary=True)
    params['c_base_subsonic2'].set(value=1.0, vary=True)
    params['c_base_subsonic3'].set(value=0.0, vary=True)

    print(params)

    result = model.fit(y, params, x=x)

    result.plot_fit()
    plt.show()

    print(result.fit_report())

# I really just want sometin tat interpolates linearly between all of te points
# owever, tat requires a ton of if statements, wic brins us back to te same problem as before were te proram is too slow
# I tink te tin tat makes te most sense

# Eventually I just ave up on mat and manually plotted out a few points in fityk to create a polyline


coords = [
    0.00947, 0.900636, 0.0183, 1.00537, 0.031, 1.05994, 0.0425, 1.07916,
    0.0504, 1.08585, 0.0576, 1.08763, 0.0709, 1.08633, 0.0799, 1.08428,
    0.1734, 1.0572, 0.2203, 1.04842, 0.2853, 1.04026, 0.3305, 1.03797, 0.381,
    1.0365, 0.4424, 1.03937, 0.499, 1.0436, 0.5833, 1.05822, 0.6495, 1.07973,
    0.6794, 1.09261, 0.6897, 1.09689, 0.7018, 1.102, 0.8007, 1.08501, 0.9693,
    1.32587, 1.048, 1.4036, 1.1889, 1.32451, 1.401, 1.1858, 1.574, 1.0957,
    1.708, 1.0399, 1.894, 0.9803, 2.134, 0.9305, 2.43, 0.8822, 2.752, 0.8443,
    2.988, 0.808, 3.458, 0.7558, 4.22, 0.6919, 4.638, 0.6615, 5.209, 0.6257,
    6.14, 0.5771, 7.24, 0.5404, 8.561, 0.5101, 9.957, 0.488, 14.336, 0.4738,
    24.996, 0.4635]

x_coords = coords[::2]
y_coords = coords[1::2]


if (__name__ == "__main__"):
    fit_coefficient_of_lift()
