import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from Helpers.data import hist_box_count


if __name__ == "__main__":
    df = pd.read_csv("./Analysis/MonteCarloFlightData/output.csv")

    print(df)

    # print(df[df["Lateral Velocity"] > 150])
    # print(df[df["Apogee"] > 20000][["Apogee", "Lateral Velocity", "Total Impulse", "Mean Wind Speed", "Wind Speed Deviation"]])

    plt.hist(df[["Lateral Velocity"]], hist_box_count(len(df.index)), histtype='bar', weights=100*np.ones(len(df.index))/len(df.index))

    plt.title("Range of Lateral Velocities")
    plt.xlabel("Lateral Velocity (m/s)")
    plt.ylabel("Frequency")

    plt.show()