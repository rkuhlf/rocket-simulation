# LOOP OVER DIFFERENT HEAD LOSS VALUES

# Results: It's very important. Try to minimize it.

import traceback
import numpy as np
import matplotlib.pyplot as plt
from lib.general import constant


from example.simulations.fill.fillsimulation_eclipse_titan import get_sim

iterations = 20
min_loss = 0
max_loss = 2_000_000 # 20 bar
head_loss_range = np.linspace(min_loss, max_loss, iterations)

fill_amount = []
fill_time = []

# Run a range of simulations
for head_loss in head_loss_range:
    try:
        sim = get_sim()
        sim.logger = None

        sim.head_loss = constant(head_loss)

        sim.run_simulation()

        fill_amount.append(sim.run_tank.ox_mass)
        fill_time.append(sim.time)


        print(f"Simulated fill with {head_loss} Pa loss, ended after {fill_time[-1]} s with {fill_amount[-1]} kg")
    except Exception as e:
        print("Sim failed; probably went past nitrous critical point")
        print(f"Exception was {e}")
        print(print(traceback.format_exc()))

fig, (ax1, ax2) = plt.subplots(2)

head_loss_range = head_loss_range[:len(fill_amount)]
ax1.plot(head_loss_range, fill_amount)
ax1.set(title="Fill Amount vs Loss", xlabel="Head Loss [Pa]", ylabel="Fill Amount [kg]")

ax2.plot(head_loss_range, fill_time)
ax2.set(title="Fill Time vs Loss", xlabel="Head Loss [Pa]", ylabel="Fill Time [s]")


fig.tight_layout()

plt.show()


