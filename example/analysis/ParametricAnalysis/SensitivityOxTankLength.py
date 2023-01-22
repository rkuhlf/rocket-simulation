# LOOP OVER DIFFERENT INITIAL TANK TEMPERATURES FOR OVERALL THRUSTS
# Though we do not have much control over the temperature our rocket will launch at, it is important to know what the effects would be
# Lowest temperature ever recorded involved a leaky valve, but was 50 F, highest was 80 F (supercritical at 97 F) 


# Increasing temperature looks like it increases the total impulse but decreases burn time, affecting the burn time more strongly
# This is actually important as an application because we will get different drag and thrust values, which means that our designs could be incorrect 

import numpy as np
import matplotlib.pyplot as plt
from src.rocketparts.motorparts.oxtank import OxTank
from src.rocketparts.motor import CustomMotor


from Simulations.DesignedMotorHTPB import get_sim
from lib.data import fahrenheit_from_kelvin


m: CustomMotor = get_sim().motor
base_length = m.ox_tank.length

# Gave it 3 inches in meters on both sides
deviation = 1
min_len = base_length - deviation
max_len = base_length + deviation

iterations = 20
lengths = np.linspace(min_len, max_len, iterations)
burn_times = []
total_impulses = []

# Run a range of simulations
for length in lengths:
    try:
        sim = get_sim()
        sim.logger = None

        m: CustomMotor = sim.motor
        m.ox_tank.length = length
        m.ox_tank.calculate_phase_distribution()

        sim.run_simulation()

        total_impulses.append(sim.total_impulse)
        burn_times.append(sim.burn_time)

        print(f"Simulated length {length}, ended after {sim.burn_time} with {sim.total_impulse}")
    except Exception as e:
        print("Sim failed; probably went past nitrous critical point")

fig, (ax1, ax2) = plt.subplots(2)

lengths = lengths[:len(total_impulses)]
ax1.plot(lengths, total_impulses)
ax1.set(title="Total Impulse vs Length", xlabel="Length [m]", ylabel="Total Impulse [Ns]")

ax2.plot(lengths, burn_times)
ax2.set(title="Burn Time vs Length", xlabel="Length [m]", ylabel="Burn Time [s]")


fig.tight_layout()

plt.show()


