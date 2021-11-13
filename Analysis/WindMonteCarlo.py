# RUN MULTIPLE SIMULATIONS; VARY WIND
# This should give us a good idea of the varying kinds of drift we will get (once I get parachutes working)
# It should also give us a range for the kinds of Mach and velocity we will be going, as well as the variability in apogee; basically summarizing what happens because of our stability

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import sys
sys.path.append(".")

from Simulations.DesignedRocket import get_sim


def simulate_monte_carlo(sim_function, iters=10, debug=True):
    """Run multiple of the same simulations and return all of their results"""
    apogees = []
    distances = []

    try:
        for i in range(iters):
            sim = sim_function()

            sim.logger = None

            sim.run_simulation()

            apogees.append(sim.apogee)
            distances.append(sim.dist_from_start)

            if debug:
                print(f"Finished iteration {i}")
    finally:
        return apogees, distances


def graph_monte_carlo(distances, apogees):
    fig, ax = plt.subplots()

    ax.scatter(distances, apogees)
    ax.set(title="Flight Variation with Wind", xlabel="Drift Distance (m)", ylabel="Apogee (m)")

    plt.show()


def save_monte_carlo(apogees, distances):
    data = pd.DataFrame({
        'Apogee': apogees,
            'Drift': distances,
        })

    data.to_csv("Data/Input/windMonteCarlo.csv")


if __name__ == "__main__":
    distances, apogees = simulate_monte_carlo(get_sim, 50)
    graph_monte_carlo(distances, apogees)

    save_monte_carlo(distances, apogees)
