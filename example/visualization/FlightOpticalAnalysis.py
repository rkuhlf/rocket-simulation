# OPTICAL ANALYSIS OF THE ROCKET
# Do these graphs after you run a simulation to check whether anything is glitching or broken
# The main thing is that it shows the important graphs for your angles

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from lib.logger import feature_time
from src.simulation.rocket.logger_features import *

def display_forces(data):
    fig, ax = plt.subplots()
    ax.plot(data[feature_time.get_label()], data[feature_z_force.get_label()], label="Vertical Net Force")

    # This not exactly all in the same direction, but close enough
    resistive_forces = data[feature_thrust.get_label()] - data[feature_z_force.get_label()]
    ax.plot(data[feature_time.get_label()], resistive_forces, label="Resistive Forces")
    
    ax.plot(data[feature_time.get_label()], data[feature_thrust.get_label()], label="Thrust")

    ax.set_title("Forces over Time")
    ax.set_xlabel("Time [s]")
    ax.set_ylabel("Force [N]")

    ax.legend(loc="upper right")

    print("All of these lines should be relatively smooth. You should be able to identify all spikes: thrust curve burning out and the deployment of parachutes. In addition, the peak of the resistive forces should come immediately after the net force begins to turn negative, maybe even sooner because of the decreasing air density. Note that small osciallations may occur as the rocket wobbles in the air.")
    plt.show()

def display_lift_drag(data):
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(ncols=2, nrows=2)

    ax1.set_title("Lift Magnitude")
    lift = (data[feature_x_lift.get_label()] ** 2 + \
            data[feature_y_lift.get_label()] ** 2 + \
            data[feature_z_lift.get_label()] ** 2) ** (1/2)
    ax1.plot(data[feature_time.get_label()], lift)
    ax1.set_xlabel("Time [s]")
    ax1.set_ylabel("Stability [Calibers]")

    ax2.set_title("Drag Magnitude")
    lift = (data[feature_x_drag.get_label()] ** 2 + \
            data[feature_y_drag.get_label()] ** 2 + \
            data[feature_z_drag.get_label()] ** 2) ** (1/2)
    ax2.plot(data[feature_time.get_label()], lift)
    ax2.set_xlabel("Time [s]")
    ax2.set_ylabel("Force (N)")

    plt.show()

def display_stability(data):
    # Subplot layout from https://matplotlib.org/3.1.1/gallery/subplots_axes_and_figures/gridspec_and_subplots.html#sphx-glr-gallery-subplots-axes-and-figures-gridspec-and-subplots-py
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(ncols=2, nrows=2)

    # Sample of spanning multiple columns in case I need it
    # gs = axes[0, 0].get_gridspec()
    # # remove the underlying axes
    # for ax in axes[0, :]:
    #     ax.remove()
    
    # ax1 = fig.add_subplot(gs[0, :])
    # ax2 = axes[1, 0]
    # ax3 = axes[1, 1]


    ax1.set_title("Conventional Stability")
    ax1.plot(data[feature_time.get_label()], data[feature_stability_cals.get_label()])
    ax1.set_xlabel("Time [s]")
    ax1.set_ylabel("Stability [Calibers]")

    ax2.set_title("Modern Stability")
    ax2.plot(data[feature_time.get_label()], data[feature_stability_lengths.get_label()])
    ax2.set_xlabel("Time [s]")
    ax2.set_ylabel("Stability [Lengths]")

    print("Your stability margin should not be too high or too low. If it is too high, your rocket may oscillate very quickly due to strong restoring forces, causing it to spin out or turn strongly into the wind. If it is too low, it may pass zero during an actual flight, causing it to flip over. Aim for 1-3 calibers, being careful to look at it dynamically - the transonic region can play a major role.")
    print("An improved understanding of stability suggests that you should be using the stability distance divided by the total length as your rule of thumb. I have seen recommendations of 10-20%.")
    
    ax3.set_title("Rotation")
    ax3.plot(data[feature_time.get_label()], data[feature_theta_down.get_label()])
    ax3.set_xlabel("Time [s]")
    ax3.set_ylabel("Rotation Down [rad]")

    print("The rocket's rotation should be a relatively smooth curve (some small oscillations are fine) until it reaches apogee. Then, if you have no simulated parachutes, you will see all kinds of oscillations. Depending on how stable you are, the rotation might converge towards the end when the air gets denser.")

    ax4.set_title("Angle of Attack")
    ax4.plot(data[feature_time.get_label()], data[feature_AOA.get_label()])
    ax4.set_xlabel("Time [s]")
    ax4.set_ylabel("AOA [rad]")
    print("The angle of attack should show a similar story to the rotation.")

    fig.tight_layout()

    plt.show()

def display_aerodynamics(data):
    # I have considered adding a graph to show what input models you are using, but I decided it would be redundant

    fig, (ax_top, ax_bottom) = plt.subplots(2, 1)

    ax_top.plot(data[feature_time.get_label()], data[feature_AOA.get_label()])
    ax_top.set(title="Angle of Attack Over Time", xlabel="Time [s]", ylabel="AOA [rad]")
    ax_bottom.plot(data[feature_time.get_label()], data[feature_CL.get_label()], label="CL")
    ax_bottom.plot(data[feature_time.get_label()], data[feature_CD.get_label()], label="CD")
    ax_bottom.set(title="CD and CL over Time", xlabel="Time [s]", ylabel="Coefficient")
    ax_bottom.legend(loc="upper right")

    fig.tight_layout()

    print("Both coefficients should be very smooth when graphed over time. If they are not, your data input method does not have enough detail to properly simulate the system. Your coefficient of lift should be roughly proportional to the AOA (at low values), and your CD should increase significantly in the transonic region. If, like mine, yours has spikes all over the place, some thing is majorly wrong.")

    plt.show()

def display_diverging(data):
    # I think that a perfectly balanced system will have a constant restoring coefficient / displacement coefficient
    # In this case I would call that the angular acceleration / angle of attack
    # If it is steadily increasing, then the system will be diverging.
    # If it is steadily decreasing then the system will definitely be converging
    # Unfortunately, if it changes as a function of the rocket's angle of attack, I am unsure how to interpret that.

    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2)
    
    ax1.plot(data[feature_time.get_label()], data[feature_AOA.get_label()])
    ax1.set(title="Angle of Attack Over Time", xlabel="Time [s]", ylabel="AOA [rad]")
    ax2.plot(data[feature_time.get_label()], data[feature_alpha_down.get_label()])
    ax2.set(title="Angular Acceleration Over Time", xlabel="Time [s]", ylabel="Acceleration [rad/s^2]")

    restoration_ratios = data[feature_alpha_down.get_label()] / data[feature_AOA.get_label()]
    ax3.plot(data[feature_time.get_label()], restoration_ratios)
    ax3.set(title="Restoration Ratio Over Time", xlabel="Time [s]", ylabel="Restoration")
    ax4.set(title="Restoration Ratio Over Time", xlabel="Time [s]", ylabel="Restoration")
    ax4.plot(data[feature_time.get_label()], abs(restoration_ratios))
    
    fig.tight_layout()

    print("Under the assumption that the restoring moment is proportional to the angle of attack (which it is at small angles), I presumed that graphing the restoring moment divided by the angle of attack would give us a good idea how the coefficients for the restoring moment are trending. So, if the ratio is tending to increase, the restoring forces should be getting smaller, and your rocket should converge to a rotation. If they are steadily decreasing, your rocket is probably going to start spinning like crazy. Unfortunately, the graphs are not very clear when you reach high angles of attack, because the first assumption breaks down. Double unfortunately, there are little spikes around AOA=0 because of the division by close to 0.")

    plt.show()

def display_overall_flight(data):
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2)

    ax1.plot(data[feature_time.get_label()], data[feature_z_position.get_label()], label="Height [AGL]")
    ax1.plot(data[feature_time.get_label()], data[feature_z_velocity.get_label()], label="Velocity")
    ax1.plot(data[feature_time.get_label()], data[feature_z_acceleration.get_label()], label="Acceleration")
    ax1.set(title="Flight over Time", xlabel="Time [s]", ylabel="Positional Information [m/s^n]")
    ax1.legend(loc="upper right")
    
    ax2.plot(data[feature_x_position.get_label()], data[feature_z_position.get_label()], label="vs x-axis")
    ax2.plot(data[feature_y_position.get_label()], data[feature_z_position.get_label()], label="vs y-axis")
    ax2.set(title="Flight Path", xlabel="Distance [m]", ylabel="Height [m]")
    ax2.legend(loc="upper right")

    ax3.plot(data[feature_time.get_label()], data[feature_theta_down.get_label()], label="Pitch")
    ax3.plot(data[feature_time.get_label()], data[feature_omega_down.get_label()], label="Velocity")
    ax3.plot(data[feature_time.get_label()], data[feature_alpha_down.get_label()], label="Acceleration")
    ax3.set(title="Rotation over Time", xlabel="Time [s]", ylabel="Rotational Information [rad/s^n]")
    ax3.legend(loc="lower right")

    ax4.plot(data[feature_time.get_label()], data[feature_theta_down.get_label()], label="Pitch")
    ax4.plot(data[feature_time.get_label()], data[feature_heading_around.get_label()], label="Target")
    ax4.set(title="Rotation Seeking", xlabel="Time [s]", ylabel="Rotation [rad]")
    ax4.legend(loc="lower right")

    fig.tight_layout()

    plt.show()

def display_optical_analysis(target):
    """
        Shows several graphs (using matplotlib and pandas) of the angles of the rocket flight

        This is designed so that you look at the graphs while you read the output of the console to determine if it is working properly.
    """

    data = pd.read_csv(target)

    funcs: list[callable] = [display_forces, display_stability, display_aerodynamics, display_diverging, display_lift_drag, display_overall_flight]

    for func in funcs:
        try:
            func(data)
        except Exception as e:
            print(f"{func.__name__} threw an error, probably because your logger is not recording the data")
            print(e)


def display_altitude(df, ceiling=None):
    if ceiling is not None:
        plt.plot((0, max(df[feature_time.get_label()])), (ceiling, ceiling), label="Ceiling")
    
    plt.plot(df[feature_time.get_label()], df["altitude"] * 3.281, label="Flight")

    plt.title("Altitude over Time")
    plt.xlabel("Time (s)")
    plt.ylabel("Altitude (ft)")

    plt.legend()
    plt.show()

def display_speed(df):
    fig, ax = plt.subplots()

    ax.plot(df[feature_time.get_label()], df["velocity"] * 3.281, label="Velocity", color="blue")
    ax.set_ylabel("Velocity (ft/s)", color="blue")

    ax2 = ax.twinx()
    ax2.plot(df[feature_time.get_label()], df["mach"], label="Mach Number", color="red")
    ax2.set_ylabel("Mach", color="red")

    ax.set_xlabel("Time (s)")

    plt.title("Velocity over Time")
    plt.show()

def display_acceleration(df):    
    plt.plot(df[feature_time.get_label()], df["acceleration"] * 3.281)

    plt.title("Acceleration over Time")
    plt.xlabel("Time (s)")
    plt.ylabel("Acceleration (ft/s^2)")

    plt.show()

def display_forces(df):
    # No weight because I did not log it
    plt.plot(df[feature_time.get_label()], df["drag"] * 0.225, label="Drag")
    plt.plot(df[feature_time.get_label()], df["thrust"] * 0.225, label="Thrust")

    plt.title("Forces over Time")
    plt.xlabel("Time (s)")
    plt.ylabel("Force (lbs)")

    plt.legend()
    plt.show()


if __name__ == "__main__":
    # display_optical_analysis("Data/Output/output5DOFWind.csv")

    data = pd.read_csv("Analysis/MonteCarloPreDatcom/MonteCarloFlightSimulations/5.csv")

    # display_altitude(data, ceiling=50000)
    # display_speed(data)
    # display_acceleration(data)
    display_forces(data)

    pass
