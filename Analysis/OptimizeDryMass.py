# DETERMINE THE BEST DRY MASS TO MAXIMIZE APOGEE
# Because drag is not proportional to mass, it is minimized the more dry mass we have in the rocket (same concept as ballistic coefficient in bullets)
# Loops over a predetermined set of mass changes to figure which ones give the best apogee
# More than likely, less mass will be better. I just want to confirm it so we don't waste a ton of time on mass reduction studies


import numpy as np
import matplotlib.pyplot as plt
import sys
sys.path.append(".")

# from SimulateRocket import get_simulation as get_sim
from Simulations.DesignedRocket import get_sim


# TODO: Changing the mass like this will affect stability slightly because it changes the moment of inertia. I need to understand stability better, because I don't know if we want a higher or lower moment


min_change = -20
max_change = 20
iterations = 3
mass_changes = np.linspace(min_change, max_change, iterations)

for mass_change in mass_changes:
    sim = get_sim()

    sim.set_logger(None)

    sim.rocket.change_mass(mass_change, exclude_objects=[sim.rocket.motor])

    print("Total mass in script", sim.rocket.total_mass)

    sim.run_simulation()

    apogees.append(sim.apogee)
    gees_off_rail.append(sim.rail_gees)
    velocities_off_rail.append(sim.rail_velocity)
    

fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2)

ax1.plot(mass_changes, apogees)
ax1.set(title="Apogee at Mass Change", xlabel="Mass Change [kg]", ylabel="Apogee [m]")

print(gees_off_rail)
ax2.plot(mass_changes, gees_off_rail)
ax2.set(title="Acceleration Stability off Rail", xlabel="Mass Change [kg]", ylabel="gees")

print(velocities_off_rail)
ax4.plot(mass_changes, velocities_off_rail)
ax4.set(title="Velocity Stability off Rail", xlabel="Mass Change [kg]", ylabel="Velocity [m/s]")


fig.tight_layout()

plt.show()

