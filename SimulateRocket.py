# Tanner's model currently reaces apogee at 3158 meters
# My model reaches 2949 (2951 using a polynomial model of air density)
# RASAero reaces 3350 with a converted rocket that is probably too long for how light it is
# The difference is probably due to drag_coefficient implementation and momentum calculations

from environment import Environment
from RocketParts.motor import Motor
from rocket import Rocket
from RocketParts.parachute import ApogeeParachute, Parachute
from logger import Feedback_Logger  # , Logger
from simulation import Simulation
from numpy import array


# Base
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
env = Environment({"time_increment": 0.01, "apply_wind": True})
motor = Motor()
drogue_parachute = ApogeeParachute({"radius": 0.2})
main_parachute = Parachute()
rocket = Rocket(environment=env, motor=motor, parachutes=[drogue_parachute, main_parachute])
logger = Feedback_Logger(
    rocket,
    ['position', 'velocity', 'acceleration', 'rotation', 'angular_velocity',
     'angular_acceleration'])

logger.splitting_arrays = True

sim = Simulation(
    {"apply_angular_forces": False, "max_frames": -1,
     "stopping_errors": False},
    env, rocket, logger)
sim.run_simulation()
