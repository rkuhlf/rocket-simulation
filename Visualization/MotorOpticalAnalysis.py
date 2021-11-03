import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def display_pressures(data):
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2)
    ax1.plot(data["time"], np.asarray(data["combustion_chamber.pressure"]) / 10 ** 5)
    ax1.plot(data["time"], np.asarray(data["ox_tank.pressure"]) / 10 ** 5)
    ax1.set(title="Pressures over Time", xlabel="Time [s]", ylabel="Pressure [bar]")

    ax3.plot(data["time"], data["combustion_chamber.temperature"])
    ax3.set(title="Chamber Temperatures over Time")

    ax4.plot(data["time"], data["ox_tank.temperature"])
    ax4.set(title="Ox Temperatures over Time", xlabel="Time [s]", ylabel="Temperature [K]")

    fig.tight_layout()
    plt.show()

def display_flows(data):
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2)
    ax1.plot(data["time"], np.asarray(data["ox_flow"]))
    ax1.plot(data["time"], np.asarray(data["fuel_flow"]))
    ax1.set(title="Ox Flow and Fuel Flow", xlabel="Time [s]", ylabel="Pressure [bar]")

    ax2.plot(data["time"], data["OF"])
    ax2.set(title="O/F over Time")

    # ax4.plot(data["time"], data["ox_tank.temperature"])
    # ax4.set(title="Ox Temperatures over Time", xlabel="Time [s]", ylabel="Temperature [K]")

    fig.tight_layout()
    plt.show()


def display_efficiency(data):
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2)

    ax1.plot(data["time"], data["OF"])
    ax1.set(title="Mixing Ratio", xlabel="Time [s]", ylabel="O/F")

    ax2.plot(data["time"], np.array(data["combustion_chamber.fuel_grain.port_diameter"]) * 100)
    ax2.set(title="Grain Diameter", xlabel="Time [s]", ylabel="Diameter [cm]")

    ax3.plot(data["time"], data["combustion_chamber.cstar"])
    ax3.set(title="Combustion Efficiency", xlabel="Time [s]", ylabel="C* [m/s]")

    ax4.plot(data["time"], data["specific_impulse"])
    ax4.set(title="Combustion Efficiency", xlabel="Time [s]", ylabel="Specific Impulse [s]")

    fig.tight_layout()

    plt.show()


def display_overall(data):
    total_impulse = np.sum(data["thrust"]) * data["time"][1]
    print(f"TOTAL IMPULSE: {total_impulse}")



def display_optical_analysis(target):
    """
        Shows several graphs (using matplotlib and pandas) of the angles of the rocket flight

        This is designed so that you look at the graphs while you read the output of the console to determine if it is working properly.
    """

    data = pd.read_csv(target)

    display_pressures(data)
    display_efficiency(data)
    display_flows(data)




if __name__ == "__main__":

    display_optical_analysis("Data/Output/motorOutput.csv")