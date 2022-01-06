# COMPARE DIFFERENT SIMULATIONS
# Mostly generates graphs for MMR
# Also does quite a bit of debugging to figure out why they are different

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


from Helpers.visualization import make_matplotlib_big

# TODO: This should use some kind of data structure to avoid all of the repetition
def display_altitude(openRocket=None, rasaero=None, no_angles=None, DIY_angles=None, rockSim=None, show=True):
    fig, ax = plt.subplots()

    apogees = []

    if openRocket is not None:
        altitudes = openRocket["Altitude (m)"] * 3.28084
        ax.plot(openRocket["Time (s)"], altitudes, label="OpenRocket")

        apogee = max(altitudes)
        print(f"OpenRocket predicts apogee of {apogee}")
        apogees.append(apogee)

    if rasaero is not None:
        altitudes = rasaero["Altitude (ft)"]
        ax.plot(rasaero["Time (sec)"], altitudes, label="RASAero")

        apogee = max(altitudes)
        print(f"RASAero predicts apogee of {apogee}")
        apogees.append(apogee)

    if no_angles is not None:
        altitudes = no_angles["position3"] * 3.28084
        ax.plot(no_angles["time"], altitudes, label="1 DOF")

        apogee = max(altitudes)
        print(f"1 DOF predicts apogee of {apogee}")
        apogees.append(apogee)

    if DIY_angles is not None:
        altitudes = DIY_angles["position3"] * 3.28084
        ax.plot(DIY_angles["time"], altitudes, label="5 DOF")

        apogee = max(altitudes)
        print(f"5 DOF predicts apogee of {apogee}")
        apogees.append(apogee)
    
    print(f"APOGEE: {np.average(apogees)}")


    ax.set(title="Altitude AGL over Time", xlabel="Time (sec)", ylabel="Altitude (ft)")
    ax.legend(loc="upper left")

    if show:
        plt.show()

def display_drag(openRocket=None, rasaero=None, no_angles=None, DIY_angles=None, rockSim=None, show=True):
    fig, (ax1, ax2) = plt.subplots(2)

    ax1.set(title="CD over Time", xlabel="Time (sec)", ylabel="Coefficient of Drag")
    ax2.set(title="Drag over Time", xlabel="Time (sec)", ylabel="Drag (N)")

    max_drags = []

    if openRocket is not None:
        # Hard code the CD of the parachute
        openRocket['Drag coefficient ()'] = openRocket['Drag coefficient ()'].fillna(0.97)

        ax1.plot(openRocket["Time (s)"], openRocket["Drag coefficient ()"], label="OpenRocket")

        drag_forces = openRocket["Drag force (N)"]
        ax2.plot(openRocket["Time (s)"], drag_forces, label="OpenRocket")

        max_drags.append(max(drag_forces))

    if rasaero is not None:
        ax1.plot(rasaero["Time (sec)"], rasaero["CD"], label="RASAero")
        drag_forces = rasaero["Drag (lb)"] * 0.45359237 * 9.81
        ax2.plot(rasaero["Time (sec)"], drag_forces, label="RASAero")

        max_drags.append(max(drag_forces))

    if no_angles is not None:
        ax1.plot(no_angles["time"], no_angles["CD"], label="1 DOF")

        drag_forces = (no_angles["Drag1"] ** 2 + no_angles["Drag2"] ** 2 + no_angles["Drag3"] ** 2) ** (1/2)
        ax2.plot(no_angles["time"], drag_forces)  

        max_drags.append(np.max(drag_forces))

    if DIY_angles is not None:
        ax1.plot(DIY_angles["time"], DIY_angles["CD"], label="5 DOF")

        drag_forces = (DIY_angles["Drag1"] ** 2 + DIY_angles["Drag2"] ** 2 + DIY_angles["Drag3"] ** 2) ** (1/2)
        ax2.plot(DIY_angles["time"], drag_forces)  

        max_drags.append(max(drag_forces))

    if rockSim is not None:
        ax1.plot(rockSim["Time"], rockSim["Cd"], label="rockSim")
        drag_forces = rockSim["Drag force"]
        ax2.plot(rockSim["Time"], drag_forces, label="rockSim")

        max_drags.append(max(drag_forces))
    
    print(max_drags)

    print(f"MAX DRAG: {np.average(max_drags)} N")


    ax1.legend(loc="upper right")
    fig.tight_layout()
    if show:
        plt.show()

def display_mach(openRocket=None, rasaero=None, no_angles=None, DIY_angles=None, rockSim=None, show=True):
    fig, ax = plt.subplots()

    max_machs = []

    if openRocket is not None:
        
        ax.plot(openRocket["Time (s)"], openRocket["Mach number ()"] * np.sign(openRocket["Vertical velocity (m/s)"]), label="OpenRocket")

        max_machs.append(np.max(openRocket["Mach number ()"]))

    if rasaero is not None:
        ax.plot(rasaero["Time (sec)"], rasaero["Mach Number"] * np.sign(rasaero["Vel-V (ft/sec)"]), label="RASAero")

        max_machs.append(np.max(rasaero["Mach Number"]))

    if no_angles is not None:
        ax.plot(no_angles["time"], no_angles["Mach"] * np.sign(no_angles["relative velocity3"]), label="1 DOF")

        max_machs.append(np.max(no_angles["Mach"]))

    if DIY_angles is not None:
        ax.plot(DIY_angles["time"], DIY_angles["Mach"] * np.sign(DIY_angles["relative velocity3"]), label="5 DOF")

        max_machs.append(np.max(DIY_angles["Mach"]))



    ax.axhspan(0.8, 1.2, color='red', alpha=0.3)
    # TODO: add a text label that matches when you zoom


    print(np.average(max_machs))

    
    ax.set(title="Mach Number over Time", xlabel="Time (sec)", ylabel="Mach")
    ax.legend(loc="upper right")

    if show:
        plt.show()

def display_forces(openRocket=None, rasaero=None, no_angles=None, DIY_angles=None, rockSim=None, show=True):
    """Plot the net forces for all supplied data"""

    fig, ax = plt.subplots()

    if openRocket is not None:
        ax.plot(openRocket["Time (s)"], openRocket["Total acceleration (m/s)"] * (openRocket["Mass (g)"] / 1000) * np.sign(openRocket["Vertical acceleration (m/s)"]), label="OpenRocket")

    if rasaero is not None:
        ax.plot(rasaero["Time (sec)"], (rasaero["Accel (ft/sec^2)"] / 3.28084) * (rasaero["Weight (lb)"] * 0.45359237), label="RASAero")

    if no_angles is not None:
        net_force = (no_angles["Net Force1"] ** 2 + no_angles["Net Force2"] ** 2 + no_angles["Net Force3"] ** 2) ** (1/2)

        ax.plot(no_angles["time"], net_force * np.sign(no_angles["Net Force3"]), label="1 DOF")

    if DIY_angles is not None:
        net_force = (DIY_angles["Net Force1"] ** 2 + DIY_angles["Net Force2"] ** 2 + DIY_angles["Net Force3"] ** 2) ** (1/2)

        ax.plot(DIY_angles["time"], net_force * np.sign(DIY_angles["Net Force3"]), label="5 DOF")
    
    ax.set(title="Net Force over Time", xlabel="Time (sec)", ylabel="Force (N)")
    ax.axhline(y=0, color='gray', linestyle='-')

    ax.legend(loc="upper right")

    if show:
        plt.show()

def display_thrust(openRocket=None, rasaero=None, no_angles=None, DIY_angles=None, rockSim=None, show=True):
    # This one should be identical for all of them
    fig, ax = plt.subplots()

    if openRocket is not None:
        ax.plot(openRocket["Time (s)"], openRocket["Thrust (N)"], label="OpenRocket")

    if rasaero is not None:
        ax.plot(rasaero["Time (sec)"], rasaero["Thrust (lb)"] * 4.44822, label="RASAero")

    if no_angles is not None:
        ax.plot(no_angles["time"], no_angles["Thrust"], label="1 DOF")

    if DIY_angles is not None:
        ax.plot(DIY_angles["time"], DIY_angles["Thrust"], label="5 DOF")
    
    ax.set(title="Thrust over Time", xlabel="Time (sec)", ylabel="Force (N)")
    ax.legend(loc="upper right")

    if show:
        plt.show()

def display_weight(openRocket=None, rasaero=None, no_angles=None, DIY_angles=None, rockSim=None, show=True):
    # This one should be identical for all of them
    fig, ax = plt.subplots()

    if openRocket is not None:
        ax.plot(openRocket["Time (s)"], openRocket["Mass (g)"] * 9.81 / 1000, label="OpenRocket")

    if rasaero is not None:
        ax.plot(rasaero["Time (sec)"], rasaero["Weight (lb)"] * 4.44822, label="RASAero")

    if no_angles is not None:
        ax.plot(no_angles["time"], -1 * no_angles["Gravity3"], label="1 DOF")

    if DIY_angles is not None:
        ax.plot(DIY_angles["time"], -1 * DIY_angles["Gravity3"], label="5 DOF")
    
    ax.set(title="Weight over Time", xlabel="Time (sec)", ylabel="Force (N)")
    ax.legend(loc="upper right")

    if show:
        plt.show()

def display_velocity(openRocket=None, rasaero=None, no_angles=None, DIY_angles=None, rockSim=None, show=True):
    fig, ax = plt.subplots()

    max_velocities = []

    if openRocket is not None:
        velocities = openRocket["Vertical velocity (m/s)"]
        ax.plot(openRocket["Time (s)"], velocities, label="OpenRocket")

        max_velocities.append(np.max(velocities))

    if rasaero is not None:
        velocities = rasaero["Vel-V (ft/sec)"] / 3.28084
        ax.plot(rasaero["Time (sec)"], velocities, label="RASAero")

        max_velocities.append(np.max(velocities))


    if no_angles is not None:
        velocities = no_angles["velocity3"]
        ax.plot(no_angles["time"], velocities, label="1 DOF")

        max_velocities.append(np.max(velocities))

    if DIY_angles is not None:
        velocities = DIY_angles["velocity3"]
        ax.plot(DIY_angles["time"], velocities, label="5 DOF")

        max_velocities.append(np.max(velocities))

    print(f"AVERAGE MAX VELOCITY: {np.average(max_velocities)}")

    
    ax.set(title="Vertical Velocity over Time", xlabel="Time (sec)", ylabel="Velocity (m/s)")
    ax.legend(loc="upper right")

    if show:
        plt.show()


def display_angles(openRocket=None, rasaero=None, no_angles=None, DIY_angles=None, rockSim=None, show=True):
    # This one should be identical for all of them
    fig, ax = plt.subplots()

    if openRocket is not None:
        ax.plot(openRocket["Time (s)"], openRocket["Angle of attack ()"], label="OpenRocket")

    if rasaero is not None:
        ax.plot(rasaero["Time (sec)"], np.abs(rasaero["Angle of Attack (deg)"]), label="RASAero")

    if no_angles is not None:
        ax.plot(no_angles["time"], np.zeros(len(no_angles["time"])), label="1 DOF")

    if DIY_angles is not None:
        ax.plot(DIY_angles["time"], DIY_angles["AOA"] * 180 / np.pi, label="5 DOF")
    
    ax.set(title="AOA over Time", xlabel="Time (sec)", ylabel="Angle of Attack (deg)")
    ax.legend(loc="upper right")

    if show:
        plt.show()

def display_all_forces(rasaero=None, no_angles=None):
    # Use scaling to make them line up by matching the burnouts, apogees, and landings
    fig, ax = plt.subplots()

    if rasaero is not None:
        ax.plot(rasaero["Time (sec)"], rasaero["Weight (lb)"] * 4.44822, label="Weight")
        ax.plot(rasaero["Time (sec)"], rasaero["Drag (lb)"] * 4.44822, label="Drag")
        ax.plot(rasaero["Time (sec)"], rasaero["Thrust (lb)"] * 4.44822, label="Thrust")

    if no_angles is not None:
        ax.plot(no_angles["time"], no_angles["Gravity3"], label="Weight")
        ax.plot(no_angles["time"], no_angles["Drag3"] * 4.44822, label="Drag")
        ax.plot(no_angles["time"], no_angles["Thrust"] * 4.44822, label="Thrust")

    ax.set(title="Rocket Forces", xlabel="Time (s)", ylabel="Magnitude (N)")
    
    plt.legend()

    plt.show()


if __name__ == "__main__":
    openRocket = pd.read_csv("Data/Output/ThirdPartySimulations/OpenRocketData.csv")
    rasaero = pd.read_csv("Data/Output/ThirdPartySimulations/RasaeroAltitudeTime.CSV")
    no_angles = pd.read_csv("Data/Output/parachuteDebugging.csv")
    DIY_angles = pd.read_csv("Data/Output/output5DOFWind.csv")
    # rockSim = pd.read_csv("Data/Output/ThirdPartySimulations/RockSim.csv")
    
    make_matplotlib_big()

    # rasaero["Real Drag"] = rasaero["CD"] * 0.0023769 * rasaero["Velocity (ft/sec)"] ** 2

    # plt.plot(rasaero["Time (sec)"], rasaero["Drag (lb)"])
    # plt.plot(rasaero["Time (sec)"], rasaero["Real Drag"])



    display_altitude(openRocket=openRocket, rasaero=rasaero, no_angles=no_angles, DIY_angles=DIY_angles)#, rockSim=rockSim)
    display_drag(openRocket=openRocket, rasaero=rasaero, no_angles=no_angles, DIY_angles=DIY_angles)#, rockSim=rockSim)
    # display_forces(openRocket=openRocket, rasaero=rasaero, no_angles=no_angles, DIY_angles=DIY_angles)#, rockSim=rockSim)
    # display_mach(openRocket=openRocket, rasaero=rasaero, no_angles=no_angles, DIY_angles=DIY_angles)#, rockSim=rockSim)
    display_velocity(openRocket=openRocket, rasaero=rasaero, no_angles=no_angles, DIY_angles=DIY_angles)#, rockSim=rockSim)

    display_thrust(openRocket=openRocket, rasaero=rasaero, no_angles=no_angles, DIY_angles=DIY_angles)#, rockSim=rockSim)
    display_weight(openRocket=openRocket, rasaero=rasaero, no_angles=no_angles, DIY_angles=DIY_angles)#, rockSim=rockSim)
    # display_angles(openRocket=openRocket, rasaero=rasaero, no_angles=no_angles, DIY_angles=DIY_angles)#, rockSim=rockSim)

    display_all_forces(rasaero=rasaero, no_angles=no_angles)
