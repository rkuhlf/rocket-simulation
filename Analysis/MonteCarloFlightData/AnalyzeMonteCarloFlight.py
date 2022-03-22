import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from Helpers.data import hist_box_count, plot_all_sims, read_sims

def failed_rockets(df, apogee_cutoff=2500):
    return df[df["Apogee"] < apogee_cutoff]

def burn_time(df):
    burning = df[df["thrust"] > 1]

    return max(burning["time"])

# TODO: if I could just decouple the visualization from the simulation of the monte carlo class, I would not have to rewrite all of this stuff

def display_deployment_distribution(df):
    plt.hist(df["Lateral Velocity"], hist_box_count(len(df.index)), histtype='bar')

    plt.title("Range of Lateral Velocities")
    plt.xlabel("Lateral Velocity (m/s)")
    plt.ylabel("Frequency")

    plt.show()

def display_max_mach_distribution(df):
    plt.hist(df["Max Mach"], hist_box_count(len(df.index)), histtype='bar')

    plt.title("Range of Mach Number")
    plt.xlabel("Mach ()")
    plt.ylabel("Frequency")

    plt.show()

def display_AOA_velocities(df):
    plt.scatter(df["Mean Wind Speed"], df["Max Velocity"])

    plt.title("AOA Determining Velocities")
    plt.xlabel("Wind Speed (m/s)")
    plt.ylabel("Max Speed (m/s)")

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
    sims = convert_to_calibers([sim], caliber)[0]

    plt.plot(sim["time"], sim["CP"])
    plt.plot(sim["time"], sim["CG"])

    plt.plot(sim["time"], sim["RASAero CP"])
    plt.plot(sim["time"], sim["custom CG"])

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
    # df = pd.read_csv("./Analysis/ShortenedRocketFlight4/MonteCarloFlightSimulations/1.csv")

    # display_flight_stability(df)

    # sims = read_sims("./Analysis/ShortenedRocketFlight4/MonteCarloFlightSimulations")
    # display_stabilities(sims)


    df = pd.read_csv("./Analysis/ShortenedRocketFlight4/MonteCarloFlightData/output.csv")

    df = failed_rockets(df)
    # display_drift_distribution(df)
    # display_total_impulse_effect(df)
    display_AOA_velocities(df)


    pass