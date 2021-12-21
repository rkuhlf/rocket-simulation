# How much does the length of the fuel grain affect the performance of the motor
# For one of the designed motors, it gave a pretty clear peak at 1 meter. That will totally depend on other contraints
# It actually had a higher impact than I was expecting, with a 5% loss if it was half a meter shorter or longer. That is a 5000 foot difference in apogee. Get the length of your fuel grain correct.


import numpy as np
import matplotlib.pyplot as plt


from Simulations.DesignedMotor import get_sim

# In meters
min_length = 0.1
max_length = 2

iterations = 30
grain_lengths = np.linspace(min_length, max_length, iterations)
burn_times = []
total_impulses = []
# TODO: add specific impulses; right now I am not 100% sure in my calculations (of which there should be two - divided by that which burned and divided by the total that is actually there)

# Run a range of simulations
for length in grain_lengths:
    sim = get_sim()

    sim.motor.combustion_chamber.fuel_grain.length = length
    sim.logger = None

    sim.run_simulation()

    total_impulses.append(sim.total_impulse)
    burn_times.append(sim.burn_time)

    print(f"Simulated len {length}, ended after {sim.burn_time} with {sim.total_impulse}")
    

fig, (ax1, ax2) = plt.subplots(2)

ax1.plot(grain_lengths, total_impulses)
ax1.set(title="Total Impulse vs Grain Length", xlabel="Length [m]", ylabel="Total Impulse [Ns]")

ax2.plot(grain_lengths, burn_times)
ax2.set(title="Burn Time vs Grain Length", xlabel="Length [m]", ylabel="Burn Time [s]")


fig.tight_layout()

plt.show()


