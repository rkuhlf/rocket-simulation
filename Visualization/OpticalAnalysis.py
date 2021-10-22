# OPTICAL ANALYSIS OF THE ROCKET
# Do these graphs after you run a simulation to check whether anything is glitching or broken
# The main thing is that it shows the important graphs for your angles


# FIXME: Delete this once I fix it
# I can clearly see from Blender that there is an issue. For some reason, the restoring force is added to the nose cone when the rocket is near flipped
# In addition, the oscillation appears to diverge rapidly
# TODO: My best guess is that the CD and CL are just totally broken
# I don't really have very much faith that this is going to make the model work, but they are broken

# There is clearly a restoring force, since the rocket oscillates about its main heading
# The main heading might have a mistake in it (for some reason it moves towards 0 over time), but it is close enough to zero that the rocket should be moving straight up

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def display_forces(data):
    
    fig, ax = plt.subplots()
    ax.plot(data['time'], data['Net Force3'], label="Vertical Net Force")

    # This not exactly all in the same direction, but close enough
    resistive_forces = data['Thrust'] - data['Net Force3']
    ax.plot(data['time'], resistive_forces, label="Resistive Forces")
    
    ax.plot(data['time'], data['Thrust'], label="Thrust")

    ax.set_title("Forces over Time")
    ax.set_xlabel("Time [s]")
    ax.set_ylabel("Force [N]")

    ax.legend(loc="upper right")

    print("All of these lines should be relatively smooth. You should be able to identify all spikes: thrust curve burning out and the deployment of parachutes. In addition, the peak of the resistive forces should come immediately after the net force begins to turn negative, maybe even sooner because of the decreasing air density. Note that small osciallations may occur as the rocket wobbles in the air.")
    plt.show()

def display_optical_analysis():
    """
        Shows several graphs (using matplotlib and pandas) of the angles of the rocket flight

        This is designed so that you look at the graphs while you read the output of the console to determine if it is working properly.
    """

    data = pd.read_csv("Data/Output/outputIncorrectRestoration.csv")

    # display_forces(data)


    # TODO: Graph the stability over time


    fig, ax = plt.subplots()
    ax.plot(data["time"], data["rotation2"])

    plt.show()

    # AOA looks to be calculated correctly
    # fig, ax = plt.subplots()
    # ax.plot(data["time"], data["AOA"])

    # plt.show()

    fig, (ax_top, ax_bottom) = plt.subplots(2, 1)
    ax_top.plot(data["time"], data["AOA"])
    ax_bottom.plot(data["time"], data["CL"])
    ax_bottom.plot(data["time"], data["CD"])

    plt.show()


    # If the rocket started off pointed straight up, the angular acceleration (2) should always be negative







if __name__ == "__main__":
    display_optical_analysis()
