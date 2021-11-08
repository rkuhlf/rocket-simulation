# COMPARE DIFFERENT SIMULATIONS
# Mostly generates graphs for MMR
# Also does quite a bit of debugging to figure out why they are different

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def display_altitude(openRocket=None, rasaero=None, no_angles=None):
    fig, ax = plt.subplots()

    if openRocket is not None:
        ax.plot(openRocket["Time (s)"], openRocket["Altitude (m)"] * 3.28084, label="OpenRocket")

    if rasaero is not None:
        ax.plot(rasaero["Time (sec)"], rasaero["Altitude (ft)"], label="RASAero")

    if no_angles is not None:
        ax.plot(no_angles["time"], no_angles["position3"] * 3.28084, label="1 DOF")
    
    ax.set(title="Altitude AGL over Time", xlabel="Time (sec)", ylabel="Altitude (ft)")
    ax.legend(loc="upper right")

    plt.show()

def display_drag(openRocket=None, rasaero=None, no_angles=None):
    fig, (ax1, ax2) = plt.subplots(2)

    ax1.set(title="CD over Time", xlabel="Time (sec)", ylabel="Coefficient of Drag")
    ax2.set(title="Drag over Time", xlabel="Time (sec)", ylabel="Drag (N)")


    if openRocket is not None:
        # Hard code the CD of the parachute
        openRocket['Drag coefficient (​)'] = openRocket['Drag coefficient (​)'].fillna(0.97)

        ax1.plot(openRocket["Time (s)"], openRocket["Drag coefficient (​)"], label="OpenRocket")
        ax2.plot(openRocket["Time (s)"], openRocket["Drag force (N)"], label="OpenRocket")

    if rasaero is not None:
        ax1.plot(rasaero["Time (sec)"], rasaero["CD"], label="RASAero")
        ax2.plot(rasaero["Time (sec)"], rasaero["Drag (lb)"] * 0.45359237 * 9.81, label="RASAero")

    if no_angles is not None:
        ax1.plot(no_angles["time"], no_angles["CD"], label="1 DOF")

        drag = (no_angles["Drag1"] ** 2 + no_angles["Drag2"] ** 2 + no_angles["Drag3"] ** 2) ** (1/2)

        ax2.plot(no_angles["time"], drag)    
    
    ax1.legend(loc="upper right")
    fig.tight_layout()
    plt.show()

def display_mach(openRocket=None, rasaero=None, no_angles=None):
    fig, ax = plt.subplots()

    if openRocket is not None:
        ax.plot(openRocket["Time (s)"], openRocket["Mach number (​)"] * np.sign(openRocket["Vertical velocity (m/s)"]), label="OpenRocket")

    if rasaero is not None:
        ax.plot(rasaero["Time (sec)"], rasaero["Mach Number"] * np.sign(rasaero["Vel-V (ft/sec)"]), label="RASAero")

    if no_angles is not None:
        ax.plot(no_angles["time"], no_angles["Mach"] * np.sign(no_angles["relative velocity3"]), label="1 DOF")

    ax.axhspan(0.8, 1.2, color='red', alpha=0.5)

    
    ax.set(title="Mach Number over Time", xlabel="Time (sec)", ylabel="Mach")
    ax.legend(loc="upper right")

    plt.show()

def display_forces(openRocket=None, rasaero=None, no_angles=None):
    """Plot the net forces for all supplied data"""

    fig, ax = plt.subplots()

    if openRocket is not None:
        ax.plot(openRocket["Time (s)"], openRocket["Total acceleration (m/s²)"] * (openRocket["Mass (g)"] / 1000) * np.sign(openRocket["Vertical acceleration (m/s²)"]), label="OpenRocket")

    if rasaero is not None:
        ax.plot(rasaero["Time (sec)"], (rasaero["Accel (ft/sec^2)"] / 3.28084) * (rasaero["Weight (lb)"] * 0.45359237), label="RASAero")

    if no_angles is not None:
        net_force = (no_angles["Net Force1"] ** 2 + no_angles["Net Force2"] ** 2 + no_angles["Net Force3"] ** 2) ** (1/2)

        ax.plot(no_angles["time"], net_force * np.sign(no_angles["Net Force3"]), label="1 DOF")
    
    ax.set(title="Net Force over Time", xlabel="Time (sec)", ylabel="Force (N)")
    ax.legend(loc="upper right")

    plt.show()

def display_thrust(openRocket=None, rasaero=None, no_angles=None):
    # This one should be identical for all of them
    fig, ax = plt.subplots()

    if openRocket is not None:
        ax.plot(openRocket["Time (s)"], openRocket["Thrust (N)"], label="OpenRocket")

    if rasaero is not None:
        ax.plot(rasaero["Time (sec)"], rasaero["Thrust (lb)"] * 4.44822, label="RASAero")

    if no_angles is not None:
        ax.plot(no_angles["time"], no_angles["Thrust"], label="1 DOF")
    
    ax.set(title="Thrust over Time", xlabel="Time (sec)", ylabel="Force (N)")
    ax.legend(loc="upper right")

    plt.show()

def display_weight(openRocket=None, rasaero=None, no_angles=None):
    # This one should be identical for all of them
    fig, ax = plt.subplots()

    if openRocket is not None:
        ax.plot(openRocket["Time (s)"], openRocket["Mass (g)"] * 9.81 / 1000, label="OpenRocket")

    if rasaero is not None:
        ax.plot(rasaero["Time (sec)"], rasaero["Weight (lb)"] * 4.44822, label="RASAero")

    if no_angles is not None:
        ax.plot(no_angles["time"], -1 * no_angles["Gravity3"], label="1 DOF")
    
    ax.set(title="Weight over Time", xlabel="Time (sec)", ylabel="Force (N)")
    ax.legend(loc="upper right")

    plt.show()


if __name__ == "__main__":
    openRocket = pd.read_csv("Data/Output/ThirdPartySimulations/OpenRocketData.csv")
    rasaero = pd.read_csv("Data/Output/ThirdPartySimulations/RasaeroAltitudeTime.CSV")
    no_angles = pd.read_csv("Data/Output/output.csv")

    display_altitude(openRocket=openRocket, rasaero=rasaero, no_angles=no_angles)
    display_drag(openRocket=openRocket, rasaero=rasaero, no_angles=no_angles)
    display_forces(openRocket=openRocket, rasaero=rasaero, no_angles=no_angles)
    display_mach(openRocket=openRocket, rasaero=rasaero, no_angles=no_angles)

    display_thrust(openRocket=openRocket, rasaero=rasaero, no_angles=no_angles)
    display_weight(openRocket=openRocket, rasaero=rasaero, no_angles=no_angles)

    # TODO: add the finished 1 DOF and 5 DOF model simulations to this