# RUN MULTIPLE SIMULATIONS; VARY WIND
# This should give us a good idea of the varying kinds of drift we will get (once I get parachutes working)
# It should also give us a range for the kinds of Mach and velocity we will be going, as well as the variability in apogee; basically summarizing what happens because of our stability
# Recovery is also going to be concerned with what kind of lateral velocities we will be seeing at apogee to affect our parachute deployment

# Conclusions:
# I am still getting relatively low stability, I think this is more because I am simulating badly than our rocket is designed poorly
# Nevertheless, my lateral velocities look to be clustered around 80 m/s, with a max of 140 m/s (460 ft/s)

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


from Simulations.DesignedRocket import get_sim


def simulate_monte_carlo(sim_function, iters=10, debug=True):
    """Run multiple of the same simulations and return all of their results"""
    apogees = []
    distances = []
    lateral_velocities = []

    try:
        for i in range(iters):
            sim = sim_function()

            sim.logger = None

            sim.run_simulation()

            apogees.append(sim.apogee)
            distances.append(sim.dist_from_start)
            lateral_velocities.append(sim.apogee_lateral_velocity)

            if debug:
                print(f"Finished iteration {i}, flew {sim.apogee} meters into the air.")
    finally:
        return distances, apogees, lateral_velocities


def graph_monte_carlo(distances, apogees, lateral_velocities):
    fig, ax = plt.subplots()

    ax.scatter(distances, apogees)
    ax.set(title="Flight Variation with Wind", xlabel="Drift Distance (m)", ylabel="Apogee (m)")

    plt.show()

    fig, ax = plt.subplots()

    ax.scatter(lateral_velocities, apogees)
    ax.set(title="Lateral Velocity at Apogee", xlabel="Lateral Velocity (m/s)", ylabel="Apogee (m)")

    plt.show()


def save_monte_carlo(apogees, distances, lateral_velocities, path="Data/Output/windMonteCarlo.csv"):
    data = pd.DataFrame({
            'Apogee': apogees,
            'Drift': distances,
            'Lateral Velocities': lateral_velocities
        })

    data.to_csv(path)


def load_monte_carlo():
    data = pd.read_csv("Data/Input/windMonteCarlo.csv")

    return data["Apogee"], data["Drift"]

if __name__ == "__main__":
    distances, apogees, lateral_velocities = simulate_monte_carlo(get_sim, 50)
    graph_monte_carlo(distances, apogees, lateral_velocities)

    save_monte_carlo(distances, apogees, lateral_velocities, path="Data/Output/newWind.csv")
