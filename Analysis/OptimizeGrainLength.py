# How much does the length of the fuel grain affect the performance of the motor
# For one of the designed motors, it gave a pretty clear peak at 1 meter. That will totally depend on other contraints
# It actually had a higher impact than I was expecting, with a 5% loss if it was half a meter shorter or longer. That is a 5000 foot difference in apogee. Get the length of your fuel grain correct.
# Note: The endpoint behavior is not particularly clear for these graphs simply because the grain becomes so long or so short that the CEA data does not have the O/F ratio listed

import numpy as np
import matplotlib.pyplot as plt


from Simulations.DesignedMotorABS import get_sim
# from Simulations.DesignedMotorHTPB import get_sim

# In meters
min_length = 0.1
max_length = 5

iterations = 10
grain_lengths = np.linspace(min_length, max_length, iterations)
burn_times = []
total_impulses = []
specific_impulse_used = []
specific_impulse_total = []

# Run a range of simulations
for length in grain_lengths:
    sim = get_sim()

    sim.motor.combustion_chamber.fuel_grain.length = length
    # TODO: I do not know how to make this happen automatically
    sim.motor.initial_mass = sim.motor.propellant_mass
    sim.logger = None
    sim.motor.fuel_grain.verbose = False

    sim.run_simulation()

    total_impulses.append(sim.total_impulse)
    burn_times.append(sim.burn_time)
    specific_impulse_total.append(sim.total_specific_impulse)
    specific_impulse_used.append(sim.used_specific_impulse)

    print(f"Simulated len {length}, ended after {sim.burn_time} with {sim.total_impulse}")
    

fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2)

ax1.plot(grain_lengths, total_impulses)
ax1.set(title="Total Impulse vs Grain Length", xlabel="Length [m]", ylabel="Total Impulse [Ns]")

ax2.plot(grain_lengths, burn_times)
ax2.set(title="Burn Time vs Grain Length", xlabel="Length [m]", ylabel="Burn Time [s]")

ax3.plot(grain_lengths, specific_impulse_total, label="Total")
ax3.plot(grain_lengths, specific_impulse_used, label="Used")
ax3.set(title="Specific Impulse vs Grain Length", xlabel="Length [m]", ylabel="Specific Impulse [s]")
ax3.legend()

fig.tight_layout()

plt.show()


