# OPTIMIZE ANGLE GIVEN WIND
# We may be given the choice of a range of launch angles; it is important to select the correct one.
# I believe that a positive rotation down is pointing away from the wind in this simulation

# Conclusions:
# It looks like we lose about 100 meters (300 feet) for every degree off of optimal until you reach 5 degrees off, when it starts to increase rapidly.
# With the wind simulation what it is right now, I think that the best angle is 4 degrees away from the wind

import numpy as np
import matplotlib.pyplot as plt
import sys
sys.path.append(".")


from Helpers.general import angles_from_vector_3d
from Simulations.DesignedRocket import get_sim


min_angle = -20 * np.pi / 180
max_angle = -min_angle
iters = 40
angles = np.linspace(min_angle, max_angle, iters)

apogees = []
drifts = []

for start_angle in angles:
    sim = get_sim()
    env = sim.environment

    # It is trivial to determine that you should be launching either directly into or directly away from the wind
    air_direction = angles_from_vector_3d(env.get_air_speed(sim.rocket.altitude))[0]

    sim.rocket.rotation = np.array([air_direction, start_angle])

    sim.run_simulation()

    apogee = sim.apogee
    drift = sim.dist_from_start

    apogees.append(apogee)
    drifts.append(drift)

    print(f"Starting from {start_angle * 180 / np.pi} degrees down, the rocket flew {apogee} meters into the air and landed {drift} meters away from where it started.")


fig, (ax1, ax2) = plt.subplots(2)

ax1.plot(angles, apogees)
ax1.set(title="Apogee versus Angle", xlabel="Angle [rad]", ylabel="Apogee [m]")
ax2.plot(angles, drifts)
ax2.set(title="Drift versus Angle", xlabel="Angle [rad]", ylabel="Drift [m]")

fig.tight_layout()

plt.show()