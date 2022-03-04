from numpy import blackman
import pandas as pd
import matplotlib.pyplot as plt

from Helpers.data import hist_box_count, plot_all_sims, read_sims
from Helpers.visualization import make_matplotlib_big


def display_overview(characteristic_figures):
    plt.scatter(characteristic_figures["Burn Time"], characteristic_figures["Total Impulse"])

    plt.title("Motor Comprehensive Monte Carlo")
    plt.xlabel("Burn Time (s)")
    plt.ylabel("Total Impulse (Ns)")

    plt.show()

def display_efficiency(characteristic_figures):
    plt.hist(characteristic_figures[["Total Specific Impulse", "Used Specific Impulse"]].transpose(), hist_box_count(len(characteristic_figures)), histtype='bar', label=["Total Specific Impulse", "Used Specific Impulse"])
    plt.legend()

    plt.title("Monte Carlo Motor Efficiencies")
    plt.xlabel("Efficiency [s]")
    plt.ylabel("Frequency")

    plt.show()

def display_average_thrust(characteristic_figures):
    plt.scatter(characteristic_figures["Total Impulse"], characteristic_figures["Average Thrust"])

    plt.title("Monte Carlo Motor Average Thrust")
    # We should be aiming for all of the average thrust values to be above a certain threshold, which will give us a good liftoff, and we want everything to be as far to the right as possible
    plt.ylabel("Average Thrust (N)")
    plt.xlabel("Total Impulse (Ns)")

    plt.show()

def display_cstar_importance(characteristic_figures):
    fig, (ax1, ax2) = plt.subplots(1, 2)

    ax1.scatter(characteristic_figures["Combustion Efficiency"], characteristic_figures["Total Impulse"])
    ax1.set(title="Monte Carlo C* Efficiency Importance", xlabel="C* Efficiency ()", ylabel="Total Impulse (Ns)")

    ax2.scatter(characteristic_figures["Combustion Efficiency"], characteristic_figures["Burn Time"])
    ax2.set(title="Monte Carlo C* Efficiency Importance", xlabel="C* Efficiency ()", ylabel="Burn Time (s)")

    fig.tight_layout()

    plt.show()

def display_OF_correlation(characteristic_figures):
    fig, (ax1, ax2) = plt.subplots(1, 2)

    ax1.scatter(characteristic_figures["Average OF"], characteristic_figures["Total Impulse"])
    ax1.set(title="Monte Carlo OF Importance", xlabel="O/F ()", ylabel="Total Impulse (Ns)")

    ax2.scatter(characteristic_figures["Average Regression"] * 1000, characteristic_figures["Total Impulse"])
    ax2.set(title="Monte Carlo Regression Rate Importance", xlabel="Regression Rate (mm/s)", ylabel="Total Impulse (Ns)")

    fig.tight_layout()

    plt.show()

def display_end_temperature_distribution(sims):
    start_temps = []
    end_temps = []

    for sim in sims:
        try:
            start_temps.append((sim.iloc[0]["ox_tank.temperature"] - 273.15) * 9/5 + 32)
            end_temps.append((sim.iloc[-1]["ox_tank.temperature"] - 273) * 9/5 + 32)
        except Exception:
            print("Skipping because of error; probable non-simulation included in folder")
    
    plt.scatter(end_temps, start_temps)
    plt.xlabel("Final Temperature (F)")
    plt.ylabel("Initial Temperature (F)")
    plt.title("Range of Final Temperatures")

    plt.show()

def display_final_mass_distribution(sims):
    propellant_mass = []

    for sim in sims:
        try:
            # 54 kg is the dry mass of the rocket
            propellant_mass.append((sim.iloc[-1]["propellant_mass"]) + 54)
        except Exception:
            print("Skipping because of error; probable non-simulation included in folder")
    
    plt.hist(propellant_mass, bins=13)
    plt.xlabel("Final Mass (kg)")
    plt.ylabel("Frequency")
    plt.title("Distribution of Deployment Masses")

    plt.show()


#region Many curves
thin_lines = {
    "linewidth": 1.5,
    "alpha": 0.3
}

dark_green = {
    "color": (31/255, 145/255, 38/255)
}

black = {
    "color": (0/255, 0/255, 0/255)
}

def display_curves(sims):
    plot_all_sims(sims, x="time", y="thrust", **thin_lines, **black)
    plt.title("Thrust Curves")
    plt.xlabel("Time (s)")
    plt.ylabel("Thrust (N)")

    plt.show()

def display_CG_movement(sims):
    plot_all_sims(sims, x="time", y="propellant_CG", **thin_lines, **black)
    plt.title("CG Curves")
    plt.xlabel("Time (s)")
    plt.ylabel("Distance (m)")

    plt.show()

def display_regression(characteristic_figures, sims):
    fig, (ax1, ax2) = plt.subplots(1, 2)

    # Convert from m to mm
    ax1.hist(characteristic_figures["Length Regressed"] * 1000, hist_box_count(len(characteristic_figures)))
    ax1.set(title="Distribution of Ending Regression", xlabel="Length Regressed (mm)")

    plt.sca(ax2)
    plot_all_sims(sims, "time", "combustion_chamber.fuel_grain.geometry.length_regressed", **thin_lines, **black)
    ax2.set(title="Regression Lines", xlabel="Time (s)", ylabel="Length Regressed (m)")

    fig.tight_layout()

    plt.show()

#endregion

def display_general(characteristic_figures, sims):
    display_overview(characteristic_figures)
    display_efficiency(characteristic_figures)
    display_average_thrust(characteristic_figures)
    display_cstar_importance(characteristic_figures)
    display_OF_correlation(characteristic_figures)
    display_regression(characteristic_figures, sims)
    


if __name__ == "__main__":
    folder = "Analysis/MotorMonteCarloLowerCombustion-Temporary"
    sims = read_sims(folder)
    characteristic_figures = pd.read_csv(f"{folder}/output.csv")

    # display_end_temperature_distribution(sims)
    # display_final_mass_distribution(sims)
    # make_matplotlib_big()
    # display_general(characteristic_figures, sims)
    display_curves(sims)
    # display_regression(characteristic_figures, sims)
    # display_regression(characteristic_figures, sims)

    # print(sims)
    