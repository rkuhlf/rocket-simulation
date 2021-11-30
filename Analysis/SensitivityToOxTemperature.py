# LOOP OVER DIFFERENT INITIAL TANK TEMPERATURES FOR OVERALL THRUSTS
# Though we do not have much control over the temperature our rocket will launch at, it is important to know what the effects would be
# Lowest temperature ever recorded involved a leaky valve, but was 50 F, highest was 80 F (supercritical at 97 F) 


# Increasing temperature looks like it increases the total impulse but decreases burn time, affecting the burn time more strongly

import numpy as np
import matplotlib.pyplot as plt
import sys
sys.path.append(".")

from Simulations.DesignedMotor import get_sim


# Iterating from the limits of theoretically reasonable temperatures in Kelvin
min_temp = 283
max_temp = 300

iterations = 20
start_temps = np.linspace(min_temp, max_temp, iterations)
burn_times = []
total_impulses = []

# Run a range of simulations
for temp in start_temps:
    sim = get_sim()

    sim.motor.ox_tank.temperature = temp
    sim.logger = None

    sim.run_simulation()

    total_impulses.append(sim.total_impulse)
    burn_times.append(sim.burn_time)

    print(f"Simulated temp {temp}, ended after {sim.burn_time} with {sim.total_impulse}")
    

fig, (ax1, ax2) = plt.subplots(2)

ax1.plot(start_temps, total_impulses)
ax1.set(title="Total Impulse vs Starting Temperature", xlabel="Temp [K]", ylabel="Total Impulse [Ns]")

ax2.plot(start_temps, burn_times)
ax2.set(title="Burn Time vs Starting Temperature", xlabel="Temp [K]", ylabel="Burn Time [s]")


fig.tight_layout()

plt.show()


