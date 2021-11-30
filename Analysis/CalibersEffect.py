# SIMULATE ITERATIVELY TO DETERMINE STABILITIES FOR DIVERGING FLIGHT
# Calculate based on a constant stability margin through the flight
# I believe that you should only get actually diverging flight once you start decelerating. 
# Then, the restorative force begins to decay and any oscillations will start to expand in amplitude

# Just a script to help me understand how the simulation works better

# Conclusions:
# My intuition looks to be somewhat wrong. Given a constant margin of stability, the rocket's course will be identical regardless of the magnitude of stability (given that it is constant)
# I suspect this is because all forces acting on the rocket's rotation are proportional to the stability distance, so the displacement forces that act on a rocket increase only as much as the restoring forces do, which gives it the exact same motion.
# In summary, so far as your stability is positive, you are good; I totally do not understand weathercocking

# After running more simulations, I am still not sure how weathercocking works, but it is clearly having an effect on my simulations


import matplotlib.pyplot as plt
import numpy as np
import sys
sys.path.append(".")

from Simulations.DesignedRocket import get_sim


min_margin = -0.1
max_margin = 25
iters = 50
margins = np.linspace(min_margin, max_margin, iters)

apogees = []

for static_margin in margins:
    sim = get_sim()
    sim.logger = None

    sim.rocket.set_CG_constant(0)
    sim.rocket.set_CP_constant(static_margin * sim.rocket.diameter)

    sim.run_simulation()

    apogees.append(sim.apogee)
    # distances.append(sim.dist_from_start)

    print(f"Finished iteration at {static_margin} calibers")

print(margins, apogees)
fig, ax = plt.subplots()
ax.scatter(margins, apogees)
ax.set(title="Apogee over Stability", xlabel="Stability [calibers]", ylabel="Apogee [m]")

plt.show()