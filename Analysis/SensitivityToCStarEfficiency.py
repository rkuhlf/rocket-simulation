# How much does the combustion efficiency affect the performance of the motor
# Conclusion:
# The c* combustion efficiency has an almost perfectly linear relationship with the total impulse because it is highly correlated with the burn time
# It would be inaccurate to scale the thrust based on the combustion efficiency, you should be scaling the burn time.


import numpy as np
import matplotlib.pyplot as plt

from Simulations.DesignedMotor import get_sim

# As a percentage of 1
min_efficiency = 0.1
max_efficiency = 1

iterations = 30
combustion_efficiencies = np.linspace(min_efficiency, max_efficiency, iterations)
burn_times = []
total_impulses = []
specific_impulse_used = []
specific_impulse_total = []

# Run a range of simulations
for efficiency in combustion_efficiencies:
    sim = get_sim()

    sim.motor.cstar_efficiency = efficiency
    sim.logger = None

    sim.run_simulation()

    total_impulses.append(sim.total_impulse)
    burn_times.append(sim.burn_time)
    specific_impulse_total.append(sim.total_specific_impulse)
    specific_impulse_used.append(sim.used_specific_impulse)

    print(f"Simulated c* {efficiency}, ended after {sim.burn_time} with {sim.total_impulse}")
    

fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2)

ax1.plot(combustion_efficiencies, total_impulses)
ax1.set(title="Total Impulse vs C* Efficiency", xlabel="C* Efficiency", ylabel="Total Impulse [Ns]")

ax2.plot(combustion_efficiencies, burn_times)
ax2.set(title="Burn Time vs C* Efficiency", xlabel="C* Efficiency", ylabel="Burn Time [s]")

ax3.plot(combustion_efficiencies, specific_impulse_total, label="Total")
ax3.plot(combustion_efficiencies, specific_impulse_used, label="Used")
ax3.set(title="Specific Impulse vs C* Efficiency", xlabel="C* Efficiency", ylabel="Specific Impulse [s]")
ax3.legend()

fig.tight_layout()

plt.show()


