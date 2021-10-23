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

# Drag and lift forces are perfectly correct. However, the angular acceleration is incorrect - it provides an acceleration downwards once the rocket points far enough downwards, but it should still be pushing the fins back down

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


    # TODO: I would really love some kind of graph that shows if the system is diverging or not.
    # I think that a perfectly balanced system will have a constant restoring coefficient / displacement coefficient
    # In this case I would call that the angular acceleration / angle of attack
    # If it is steadily increasing, then the system will be diverging.
    # If it is steadily decreasing then the system will definitely be converging
    # Unfortunately, if it changes as a function of the rocket's angle of attack, I am unsure how to interpret that.

    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2)
    restoration_ratios = data["angular_acceleration2"] / data["AOA"]
    ax1.plot(data["time"], restoration_ratios)
    ax2.plot(data["time"], abs(restoration_ratios))
    ax3.plot(data["time"], data["AOA"])

    plt.show()


    # TODO: I think I graph of the target heading over time has several good indicators to determine if your stuff is working correctly. It also demonstrates the importance of not being overstable
    # It starts off actually more horizontal than your rocket is, since gravity is playing a major role in slowing down the rocket vertically.
    # However, before your rocket has enough time to fall (rotate too much), it provides propulsion that completely dominates gravity, giving you a target heading really close to what you started with (should be slightly larger)






if __name__ == "__main__":
    display_optical_analysis()
