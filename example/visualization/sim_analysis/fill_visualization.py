



# Not great, but otherwise Matplotlib freaks out
import warnings
warnings.filterwarnings("ignore")


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


from lib.logging.logger_features import plot_feature
from lib.visualization import make_matplotlib_medium
from lib.data import riemann_sum
from example.constants import output_path
from src.simulation.fill.logger_features import *


def plot_masses(data: pd.DataFrame):
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2)

    plt.sca(ax1)
    plot_feature(data, feature_time, feature_fill_tank_mass)

    plt.sca(ax2)
    plot_feature(data, feature_time, feature_run_tank_mass)

    plt.sca(ax3)
    plot_feature(data, feature_time, feature_flow_rate)

    plt.sca(ax4)
    # Compare the difference from the vapor in one tank to the vapor in the other.
    # Not showing head loss or anything.
    plt.title("Tank Pressure Difference")
    plt.xlabel(feature_time.get_label())
    plt.ylabel(f"time {Units.s.value}")
    plt.plot(data[feature_time.get_label()], 
             data[feature_fill_tank_pressure.get_label()] - data[feature_run_tank_pressure.get_label()])

def display_detailed(data: pd.DataFrame):
    plot_masses(data)
    plt.show()

if __name__ == "__main__":
    # make_matplotlib_medium()

    target = f"{output_path}/output copy.csv"

    data = pd.read_csv(target)

    # display_regression(data)
    # display_optical_analysis(target)
    display_detailed(data)