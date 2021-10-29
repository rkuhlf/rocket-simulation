# LOOP OVER DIFFERENT BURN TIMES TO DETERMINE ALTITUDE
# Uses the O6300 thrust curve
# Scales it up linearly
# Displays the apogee and gees off of the rail as measures of success and risk

# Conclusion:


import numpy as np
import matplotlib.pyplot as plt
import sys
sys.path.append(".")

from Data.Input.ThrustProfile import scale_saved_curve
from SimulateRocket import get_simulation


base_curve = "Data/Input/thrustCurveO6300.csv"

total_impulse = 200000 # Ns

min_time = 3
max_time = 50

iterations = 20
burn_times = np.linspace(min_time, max_time, iterations)
apogees = []
gees_off_rail = []

for burn_time in burn_times:
    # Create a new thrust curve with the new burn time
    average_thrust = total_impulse / burn_time
    target_path = f"./Data/Input/Temporary/generatedThrustCurve{burn_time}.csv"
    scale_saved_curve(base_curve, burn_time, average_thrust, target_path)
    
    sim = get_simulation()

    sim.rocket.motor.set_thrust_data_path(target_path)

    sim.run_simulation()

    apogees.append(sim.apogee)
    gees_off_rail.append(sim.rail_gees)
    

fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2)

ax1.plot(burn_times, apogees)
ax1.set(title="Apogee at Burn Times", xlabel="Burn Time [s]", ylabel="Apogee [m]")

print(gees_off_rail)
ax2.plot(burn_times, gees_off_rail)
ax2.set(title="Acceleration Stability off Rail", xlabel="Burn Time [s]", ylabel="gees")


fig.tight_layout()

plt.show()