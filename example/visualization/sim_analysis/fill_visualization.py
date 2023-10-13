



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

def plot_pressure_difference(data: pd.DataFrame):
    # Compare the difference from the vapor in one tank to the vapor in the other.
    # Not showing head loss or anything.
    plt.title("Tank Pressure Difference")
    plt.xlabel(feature_time.get_label())
    plt.ylabel(f"time [{Units.s.value}]")
    plt.plot(data[feature_time.get_label()], 
             data[feature_fill_tank_pressure.get_label()] - data[feature_run_tank_pressure.get_label()])

def plot_pressures(data: pd.DataFrame):
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2)

    plt.sca(ax1)
    plot_feature(data, feature_time, feature_fill_tank_pressure, feature_run_tank_pressure)

    plt.sca(ax2)
    plot_feature(data, feature_time, feature_fill_tank_temperature, feature_run_tank_temperature)

    plt.sca(ax3)
    plot_feature(data, feature_time, feature_head_loss)

    plt.sca(ax4)
    plot_pressure_difference(data)

def plot_masses(data: pd.DataFrame):
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2)

    plt.sca(ax1)
    plot_feature(data, feature_time, feature_fill_tank_mass)

    plt.sca(ax2)
    plot_feature(data, feature_time, feature_run_tank_mass)

    plt.sca(ax3)
    plot_feature(data, feature_time, feature_flow_rate)

    plt.sca(ax4)
    plot_pressure_difference(data)

def display_detailed(data: pd.DataFrame):
    plot_masses(data)
    plt.show()

    plot_pressures(data)
    plt.show()

def display_optical_analysis(target):
    data = pd.read_csv(target)
    display_detailed(data)


if __name__ == "__main__":
    # make_matplotlib_medium()

    target = f"{output_path}/fillOutput.csv"

    data = pd.read_csv(target)

    display_detailed(data)