import sys

sys.path.append(".")



from Helpers.general import angles_from_vector_3d
import matplotlib.pyplot as plt
import numpy as np
from numpy import array
from simulation import Simulation
from logger import Feedback_Logger  # , Logger
from RocketParts.parachute import ApogeeParachute
from rocket import Rocket
from RocketParts.motor import Motor
from environment import Environment





# Just using apogee as an indicator of convergence


# Uses mostly class defaults. No wind so I can compare them
# Notice that it is a 17 second sim to apogee
# just curious to see the behavior over the higher values

# At the current state of the model, it looks like you can't get any better data by decreasing delta T past 0.0024

def frange(x, y, jump):
    while x < y:
        yield x
        x += jump


time_deltas = list(frange(0.0001, 0.01, jump=0.0001)) + list(frange(0.01, 0.1, jump=0.01)) + list(frange(0.1, 3, jump=0.1))
apogees = []
for time_delta in time_deltas:
    env = Environment({"time_increment": time_delta, "apply_wind": False})
    motor = Motor()
    rocket = Rocket(environment=env, motor=motor, parachutes=[])

    sim = Simulation(
        {"apply_angular_forces": True, "max_frames": -1,
         "stopping_errors": False},
        env, rocket)
    sim.run_simulation()

    apogee = sim.apogee()
    apogees.append(apogee)

    print(time_delta)
    print(apogee)

print(time_deltas)
print(apogees)

plt.plot(time_deltas, apogees)
plt.show()



# Base (pasted from the SimulateRocket.py file)
# Uses mostly class defaults
# Notice that it is a 17 second sim to apogee
# 1 gives me 1064 meters, very big max speed
# 0.5 returns 1642, much lower max speed
# 0.1 gives me 1277
# 0.05 gives me 937
# 0.01 gives me 1720
# 0.005 -> 2009
# 0.001 -> 2074
# 0.0005 -> 2074
# 0.0001 -> 2074