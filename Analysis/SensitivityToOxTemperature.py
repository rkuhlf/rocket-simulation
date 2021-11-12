# LOOP OVER DIFFERENT INITIAL TANK TEMPERATURES FOR OVERALL THRUSTS


import numpy as np
import matplotlib.pyplot as plt
import sys
sys.path.append(".")

from Data.Input.ThrustProfile import scale_saved_curve
from Simulations.DesignedMotor import get_sim


# Iterating from the limits of theoretically possible to the probably completely unstable in terms of temperature
min_temp = 283
max_temp = 300

# This is really slow, even without logging anything
iterations = 20
start_temps = np.linspace(min_temp, max_temp, iterations)
total_impulses = []

for temp in start_temps:
    sim = get_sim()

    sim.motor.ox_tank.temperature = temp
    # sim.logger = None

    sim.run_simulation()

    total_impulses.append(sim.total_impulse)
    

fig, ax = plt.subplots()

ax.plot(start_temps, total_impulses)
ax.set(title="Total Impulse vs Starting Temperature", xlabel="Temp [K]", ylabel="Total Impulse [Ns]")

fig.tight_layout()

plt.show()


