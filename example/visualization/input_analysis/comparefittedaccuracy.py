# USE GRAPHS TO DEMONSTRATE ACCURACY OF data MODELS
# Display the input points along with the fitted line to match them
# It's important to visually verify that we aren't getting significant error in the inputs

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from src.constants import aero_path, atmosphere_path

from src.data.input.models import *


def plot_density_comparison():
    data = pd.read_csv(f"{atmosphere_path}/airQuantities.csv")

    inputs = np.arange(0, 20, 0.1)
    outputs = get_density(inputs)

    data.plot.scatter(x='Altitude', y='Density')
    plt.plot(inputs, outputs, 'r')


def plot_aero_comparison():
    data = pd.read_csv(f"{aero_path}/aerodynamicQualities.csv")

    # Rasaero outputs to a max mach of 21
    inputs = np.arange(0, 25, 0.1)

    outputs = list(map(get_splined_coefficient_of_drag, inputs))
    # outputs = get_coefficient_of_drag(inputs)

    data.plot.scatter(x='Mach', y='CD')
    plt.plot(inputs, outputs, 'r')


def plot_mach_comparison():
    data = pd.read_csv(f"{atmosphere_path}/airQuantities.csv")

    inputs = np.arange(0, 40, 0.1)

    outputs = list(map(get_speed_of_sound, inputs))

    data.plot.scatter(x='Altitude', y='Speed of sound')
    plt.plot(inputs, outputs, 'r')


if __name__ == "__main__":
    plot_density_comparison()
    plot_aero_comparison()
    plot_mach_comparison()

    plt.show()