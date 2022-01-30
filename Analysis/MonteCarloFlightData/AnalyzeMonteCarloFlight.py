import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from Helpers.data import hist_box_count


def burn_time(df):
    burning = df[df["thrust"] > 1]

    return max(burning["time"])

# TODO: if I could just decouple the visulation from the simulation of the monte carlo class, I would not have to rewrite all of this stuff

def display_deployment_distribution(df):
    plt.hist(df["Lateral Velocity"], hist_box_count(len(df.index)), histtype='bar')

    plt.title("Range of Lateral Velocities")
    plt.xlabel("Lateral Velocity (m/s)")
    plt.ylabel("Frequency")

    plt.show()

def display_apogee_distribution(df):
    plt.scatter(df["Lateral Velocity"], df["Apogee"])

    plt.title("Apogee Distribution")
    plt.xlabel("Lateral Velocity (m/s)")
    plt.ylabel("Apogee (m)")

    plt.show()

def display_total_impulse_effect(df):
    plt.scatter(df["Total Impulse"], df["Apogee"])

    plt.title("Total Impulse Effect")
    plt.xlabel("Total Impulse (Ns)")
    plt.ylabel("Apogee (m)")

    plt.show()


def best_apogee_analysis(df):
    print(df[df["Apogee"] > 20000][["Apogee", "Lateral Velocity", "Total Impulse", "Mean Wind Speed", "Wind Speed Deviation"]])

def best_motor_analysis(df):
    print(df[df["Total Impulse"] > 100_000][["Apogee", "Lateral Velocity", "Total Impulse", "Mean Wind Speed", "Wind Speed Deviation"]])

def read_sims(path):
    sims = []

    with os.scandir(path) as folder:
        for file in folder:
            sims.append(pd.read_csv(file.path))
    
    return sims
        



def display_altitude_lines(sims):
    for sim in sims:
        plt.plot(sim["time"], sim["altitude"])
    
    plt.show()


if __name__ == "__main__":
    df = pd.read_csv("./Analysis/SAIC3-Temporary/MonteCarloFlightData/output2.csv")

    best_motor_analysis(df)

    # sims = read_sims("./Analysis/SAIC3-Temporary/MonteCarloFlightSimulations")
    # display_altitude_lines(sims)

    pass