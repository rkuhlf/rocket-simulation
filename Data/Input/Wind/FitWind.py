# FIT WIND DATA
# Since the wind is not a super important aspect of the simulation, I really do not want it to take up a lot of processing power
# So, rather than looking up the data from a file, I fit a function to it

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit


# Data from 1992 to 2011
data = pd.read_csv("Data/Input/Wind/WSMRSpeedAltitude.csv")
print(data)

def fit_altitude_speed():
    # Does not match the first parts very well
    def polynomial(x, a, b, c, d, e, f):
        return a * b * x + c * x ** 2 + d * x ** 3 + e * x ** 4 + f * x ** 5

    # gives weird behavior around 0
    def polynomial_fraction(x, a, b, c, d, e, f):
        numerator = a * b * x + c * x ** 2
        denominator = d + e * x + f * x ** 2

        return numerator / denominator

    def piecewise_linear(x, a1, a2, a3, a4, m1, m2, m3, m4, m5, b1, b2, b3, b4, b5):
        mask1 = (x <= a1) * 1
        
        mask2 = (a1 < x) * (x <= a2)

        mask3 = (a2 < x) *  (x <= a3)

        mask4 = (a3 < x) *  (x <= a4)

        mask5 = (x > a4) * 1

        return mask1 * (x * m1 + b1) + mask2 * (x * m2 + b2) + mask3 * (x * m3 + b3) + mask4 * (x * m4 + b4) + mask5 * (x * m5 + b5)

    # print(piecewise_linear(np.arange(0, 10, 0.1), 2, 4, 6, 0.1, 0.2, 0.3, 0.4, 0, 0, 0, 0))


    func = piecewise_linear
    guesses = [500, 7000, 10700, 15000, 0, 0, 0, 0, 0, 3, 3, 5, 15, 2] # None
    popt, pcov = curve_fit(func, data["Altitude"], data["Speed"], guesses)

    return func, popt


def display_fit(func, popt):
    fig, ax = plt.subplots()

    ax.plot(data["Altitude"], data["Speed"], 'b-', label='data')


    ax.plot(data["Altitude"], func(data["Altitude"], *popt), "r-")

    ax.set(title="Speed at Altitude Comparison", xlabel="Altitude (meters)", ylabel="Wind Speed (m/s)")

    plt.show()



if __name__ == "__main__":
    function, parameters = fit_altitude_speed()
    display_fit(function, parameters)


