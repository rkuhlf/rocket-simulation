from numpy.polynomial import Polynomial
from numpy import polyval
import pandas as pd
import numpy as np


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



if (__name__ == "__main__"):
    fit_altitude_mach()
