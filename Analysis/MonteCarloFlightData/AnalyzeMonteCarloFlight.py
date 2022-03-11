import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from Helpers.data import hist_box_count, plot_all_sims, read_sims


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

def display_drift_distribution(df):
    plt.scatter(df["Landing Distance"], df["Apogee"])

    plt.title("Apogee Distribution")
    plt.xlabel("Drift (m)")
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


def display_altitude_lines(sims):
    plot_all_sims(sims)
    
    plt.show()

def convert_to_calibers(sims, caliber=0.1778):
    for sim in sims:
        sim["CP"] /= caliber
        sim["CG"] /= caliber
        sim["RASAero CP"] /= caliber
        sim["custom CG"] /= caliber
    
    return sims


def display_flight_stability(sim, caliber=0.1778):
    sim = convert_to_calibers([sim], caliber)[0]

    plt.plot(sim["time"], sim["CP"], label="CP")
    plt.plot(sim["time"], sim["CG"], label="CG")

    plt.plot(sim["time"], sim["RASAero CP"], label="RASAero CP")
    plt.plot(sim["time"], sim["custom CG"], label="Custom CG")

    plt.title("Stability Predictions")
    plt.ylabel("Distance from Nose Tip (cal)")
    plt.xlabel("Time (s)")
    plt.xlim(-1, 31)


    plt.legend()

    plt.show()

def display_stabilities(sims, caliber=0.1778):
    sims = convert_to_calibers(sims, caliber)

    # CP,CG,custom CG,RASAero CP
    plot_all_sims(sims, y="CP")
    plot_all_sims(sims, y="CG")

    plt.show()

    plot_all_sims(sims, y="RASAero CP")
    plot_all_sims(sims, y="custom CG")

    plt.show()


if __name__ == "__main__":
    for i in range(100):
        df = pd.read_csv(f"./Analysis/LighterRocketFlight/MonteCarloFlightSimulations/{i + 1}.csv")

        display_flight_stability(df)

    # sims = read_sims("./Analysis/Lighter/MonteCarloFlightSimulations")
    # display_stabilities(sims)

    # df = pd.read_csv("./Analysis/LighterRocketFlight/MonteCarloFlightData/output.csv")

    # display_deployment_distribution(df)

    pass