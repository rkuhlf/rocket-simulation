# OPTICAL ANALYSIS OF THE ROCKET
# Do these graphs after you run a simulation to check whether anything is glitching or broken
# The main thing is that it shows the important graphs for your angles

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def display_optical_analysis():
    """
        Shows several graphs (using matplotlib and pandas) of the angles of the rocket flight
    """

    data = pd.read_csv("Data/Output/output.csv")


    data.plot.line(x='time', y='acceleration3')

    plt.show()




if __name__ == "__main__":
    display_optical_analysis()
