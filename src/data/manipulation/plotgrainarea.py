# Graph the areas output by the blender simulation for the fuel grain over time.

import matplotlib.pyplot as plt
import pandas as pd
from src.constants import input_path


def plot_port_volume(data: pd.DataFrame):
    plt.xlabel("Length Regressed (mm)")
    plt.ylabel("Port Volume (ft^3)")
    # Convert from m^3 to ft^3
    plt.plot(data["LengthRegressed"] * 1000, data["PortVolume"] * 35.3147)

def plot_port_area(data: pd.DataFrame):
    plt.xlabel("Length Regressed (mm)")
    plt.ylabel("Port Area (in^2)")
    # 1550 converts from m^2 to in^2
    plt.plot(data["LengthRegressed"] * 1000, data["PortArea"] * 1550)

def plot_burn_area(data: pd.DataFrame):
    plt.xlabel("Length Regressed (mm)")
    plt.ylabel("Burn Area (m^2)")
    plt.plot(data["LengthRegressed"] * 1000, data["BurnArea"])

def plot_all_areas(data: pd.DataFrame):
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2)

    plt.sca(ax1)
    plot_burn_area(data)

    plt.sca(ax2)
    plot_port_area(data)

    plt.sca(ax4)
    plot_port_volume(data)
    


if __name__ == "__main__":
    data = pd.read_csv(f"{input_path}/regression/regressionlookup.csv")

    plot_all_areas(data)
    plt.show()