

# Not great, but otherwise Matplotlib freaks out
import warnings
warnings.filterwarnings("ignore")


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


from Helpers.visualization import make_matplotlib_medium
from Helpers.data import riemann_sum

def display_overall(data):
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2)
    ax1.plot(data["time"], data["thrust"])
    ax1.set(title="Thrust Over Time", xlabel="Time [s]", ylabel="Thrust [N]")

    ax2.plot(data["time"], data["mass_flow"], label="in")
    ax2.plot(data["time"], data["mass_flow_out"], label="out")
    ax2.set(title="Mass Flow Over Time", xlabel="Time [s]", ylabel="Mass Flow in [kg/s]")
    ax2.legend()

    ax3.plot(data["time"], np.asarray(data["combustion_chamber.pressure"]) / 10 ** 5, label="Chamber")
    ax3.plot(data["time"], np.asarray(data["ox_tank.pressure"]) / 10 ** 5, label="Tank")
    ax3.set(title="Pressures over Time", xlabel="Time [s]", ylabel="Pressure [bar]")
    ax3.legend()

    # TODO Actually plot like exit velocity or something 
    ax4.plot(data["time"], data["specific_impulse"])
    ax4.set(title="Combustion Efficiency", xlabel="Time [s]", ylabel="Specific Impulse [s]")

    fig.tight_layout()
    plt.show()

def display_pressures(data):
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2)
    ax1.plot(data["time"], np.asarray(data["combustion_chamber.pressure"]) / 10 ** 5)
    ax1.plot(data["time"], np.asarray(data["ox_tank.pressure"]) / 10 ** 5)
    ax1.set(title="Pressures over Time", xlabel="Time [s]", ylabel="Pressure [bar]")

    ax2.plot(data["time"], np.array(data["combustion_chamber.fuel_grain.port_diameter"]) * 100)
    ax2.set(title="Grain Diameter", xlabel="Time [s]", ylabel="Diameter [cm]")

    ax3.plot(data["time"], data["combustion_chamber.temperature"])
    ax3.set(title="Chamber Temperatures over Time", xlabel="Time [s]", ylabel="Temperature [K]")

    ax4.plot(data["time"], data["ox_tank.temperature"])
    ax4.set(title="Ox Temperatures over Time", xlabel="Time [s]", ylabel="Temperature [K]")

    fig.tight_layout()
    plt.show()

def display_efficiency(data):
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2)

    ax1.plot(data["time"], data["OF"])
    ax1.set(title="Mixing Ratio", xlabel="Time [s]", ylabel="O/F")

    ax2.plot(data["time"], 1000 * 8.314 / np.array(data["combustion_chamber.ideal_gas_constant"]))
    ax2.set(title="Molecular Weight", xlabel="Time [s]", ylabel="MW [g/mol]")
    
    ax3.plot(data["time"], data["combustion_chamber.cstar"])
    ax3.set(title="Combustion Efficiency", xlabel="Time [s]", ylabel="C* [m/s]")

    ax4.plot(data["time"], data["specific_impulse"])
    ax4.set(title="Combustion Efficiency", xlabel="Time [s]", ylabel="Specific Impulse [s]")

    fig.tight_layout()

    plt.show()

def print_total_impulse(data):
    total_impulse = riemann_sum(data["time"], data["thrust"])
    total_mass = riemann_sum(data["time"], data["mass_flow_out"])
    
    print(f"TOTAL IMPULSE: {total_impulse}")
    burn_time = data["time"].values[-1]
    print(f"BURN TIME: {burn_time}")
    average_thrust = total_impulse / burn_time
    print(f"AVERAGE THRUST: {average_thrust}")
    print(f"SPECIFIC IMPULSE: {total_impulse / (total_mass * 9.81)}")


def display_flows(data):
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2)
    ax1.plot(data["time"], data["thrust"])
    ax1.set(title="Thrust Over Time", xlabel="Time [s]", ylabel="Thrust [N]")

    ax2.plot(data["time"], data["mass_flow"], label="in")
    ax2.plot(data["time"], data["mass_flow_out"], label="out")
    ax2.set(title="Mass Flow Over Time", xlabel="Time [s]", ylabel="Mass Flow in [kg/s]")
    ax2.legend()

    ax3.plot(data["time"], np.asarray(data["ox_flow"]))
    ax3.plot(data["time"], np.asarray(data["fuel_flow"]))
    ax3.set(title="Ox Flow and Fuel Flow", xlabel="Time [s]", ylabel="Flow [kg/s]")

    ax4.plot(data["time"], data["OF"])
    ax4.set(title="O/F over Time", xlabel="Time [s]")

    fig.tight_layout()
    plt.show()



def display_optical_analysis(target):
    """
        Shows several graphs (using matplotlib and pandas) of the angles of the rocket flight

        This is designed so that you look at the graphs while you read the output of the console to determine if it is working properly.
    """

    data = pd.read_csv(target)

    display_pressures(data)
    display_efficiency(data)
    print_total_impulse(data)
    display_flows(data)


    display_overall(data)




if __name__ == "__main__":
    # make_matplotlib_medium()
    display_optical_analysis("Data/Output/motorOutput.csv")