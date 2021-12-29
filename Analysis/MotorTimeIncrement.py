# DETERMINE SIMULATION ACCURACY DEPENDENCE ON TIME INCREMENT
# The motor is dealing with massive pressure changes in very short periods of time, it is important to have good understanding of what the lowest time increment we can get away with is

# Conclusions:
# I actually think that this depends a lot on how I am limiting the pressure change in the motor file. However, with the default settins at 0.5 and 0.4 for positive and negative, it looks like you really need to have delta-t lower than 0.05. In fact, it doesn't really converge until 0.02 (101300)


import numpy as np
import matplotlib.pyplot as plt


from Data.Input.ThrustProfile import scale_saved_curve
from Simulations.DesignedMotorHTPB import get_sim



possible_increments = [0.005, 0.007]
total_impulses = []

for inc in possible_increments:
    sim = get_sim()

    sim.environment.time_increment = inc
    # sim.logger = None

    sim.run_simulation()

    total_impulses.append(sim.total_impulse)
    

fig, ax = plt.subplots()

ax.plot(possible_increments, total_impulses)
ax.set(title="Total Impulse vs Time Increment", xlabel="Increment [s]", ylabel="Total Impulse [Ns]")

fig.tight_layout()

plt.show()


