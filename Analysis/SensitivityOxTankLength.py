# LOOP OVER DIFFERENT INITIAL TANK TEMPERATURES FOR OVERALL THRUSTS
# Though we do not have much control over the temperature our rocket will launch at, it is important to know what the effects would be
# Lowest temperature ever recorded involved a leaky valve, but was 50 F, highest was 80 F (supercritical at 97 F) 


# Increasing temperature looks like it increases the total impulse but decreases burn time, affecting the burn time more strongly
# This is actually important as an application because we will get different drag and thrust values, which means that our designs could be incorrect 

import numpy as np
import matplotlib.pyplot as plt
from RocketParts.Motor.oxTank import OxTank
from RocketParts.motor import CustomMotor


from Simulations.DesignedMotorHTPB import get_sim
from Helpers.data import fahrenheit_from_kelvin


m: CustomMotor = get_sim().motor
base_length = m.ox_tank.length

# Gave it 3 inches in meters on both sides
min_len = base_length - 0.0762
max_len = base_length + 0.0762

iterations = 20
lengths = np.linspace(min_len, max_len, iterations)
burn_times = []
total_impulses = []

# Run a range of simulations
for length in lengths:
    try:
        sim = get_sim()
        sim.logger = None

        sim.motor.ox_tank.length = length
        sim.motor.ox_tank.calculate_ullage(constant_temperature=True)

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


