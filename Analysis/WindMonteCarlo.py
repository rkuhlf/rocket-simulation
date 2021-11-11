# RUN MULTIPLE SIMULATIONS; VARY WIND
# This should give us a good idea of the varying kinds of drift we will get (once I get parachutes working)
# It should also give us a good range for the kinds of Mach and velocity we will be going, as well as the variability in apogee

import numpy as np
import matplotlib.pyplot as plt
import sys
sys.path.append(".")

from Data.Input.ThrustProfile import scale_saved_curve
# from SimulateRocket import get_simulation as get_sim
from Simulations.DesignedRocket import get_sim

iters = 1

apogees = []
distances = []

for i in range(iters):
    sim = get_sim()

    sim.logger = None

    sim.run_simulation()

    apogees.append(sim.apogee)
    distances.append(sim.dist_from_start)


plt.scatter(distances, apogees)
plt.show()


