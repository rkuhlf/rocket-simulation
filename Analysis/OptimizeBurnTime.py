# LOOP OVER DIFFERENT BURN TIMES TO DETERMINE ALTITUDE
# Uses the O6300 thrust curve
# Scales it up linearly
# Displays the apogee and gees off of the rail as measures of success and risk

# Conclusion:
# I would say that we will go highest if our burn time is around 28 seconds. 
# It looks like stability off the rail is not really an issue, ignoring all frictional effects
# After 30 seconds of burn time, any increase results in highly variable apogee. I am slightly concerned that this is highly determined by my totally random wind simulation
# All of this assumes we are using a O6300 shape exactly - meaning that the liquid-phase would run out at 22-ish seconds

# Second Conclusion:
# 26 seconds of total burn looks the best for our optimized smaller rocket
# After looking more closely at the base thrust curve, I think it is liquid for about 0.8, which gives 21 seconds of liquid


import numpy as np
import matplotlib.pyplot as plt
import sys
sys.path.append(".")

from Data.Input.ThrustProfile import scale_saved_curve
# from SimulateRocket import get_simulation as get_sim
from Simulations.DesignedRocket import get_sim

base_curve = "Data/Input/thrustCurveO6300.csv"

# With only 60 kg of propellant, it is more like 200 * 60 * 9.81 = 117720
# Right now, the original simulation uses 220000
total_impulse = 130000 # Ns

# Iterating from the limits of theoretically possible to the probably completely unstable in terms of burn time
min_time = 3
max_time = 50

# This is really slow, even without logging anything
iterations = 100
burn_times = np.linspace(min_time, max_time, iterations)
apogees = []
gees_off_rail = []
velocities_off_rail = []

for burn_time in burn_times:
    # Create a new thrust curve with the new burn time
    average_thrust = total_impulse / burn_time
    target_path = f"./Data/Input/Temporary/generatedThrustCurve{burn_time}.csv"
    scale_saved_curve(base_curve, burn_time, average_thrust, target_path)
    
    sim = get_sim()

    sim.rocket.motor.set_thrust_data_path(target_path)
    sim.set_logger(None)


    sim.run_simulation()

    apogees.append(sim.apogee)
    gees_off_rail.append(sim.rail_gees)
    velocities_off_rail.append(sim.rail_velocity)
    

fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2)

ax1.plot(burn_times, apogees)
ax1.set(title="Apogee at Burn Times", xlabel="Burn Time [s]", ylabel="Apogee [m]")

print(gees_off_rail)
ax2.plot(burn_times, gees_off_rail)
ax2.set(title="Acceleration Stability off Rail", xlabel="Burn Time [s]", ylabel="gees")

print(velocities_off_rail)
ax4.plot(burn_times, velocities_off_rail)
ax4.set(title="Velocity Stability off Rail", xlabel="Burn Time [s]", ylabel="Velocity [m/s]")


fig.tight_layout()

plt.show()


