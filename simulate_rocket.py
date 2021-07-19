# Tanner's model currently reaces apogee at 3158 meters
# My model reaches 2949 (2951 using a polynomial model of air density)
# RASAero reaces 3350 with a converted rocket that is probably too long for how light it is
# The difference is probably due to drag_coefficient implementation and momentum calculations

from environment import Environment
from motor import Motor
from rocket import Rocket
from parachute import Parachute
from logger import Feedback_Logger  # , Logger
from simulation import Simulation
from numpy import array

from Helpers.general import angles_from_vector_3d


# Base
# Uses mostly class defaults
env = Environment({"time_increment": 0.01})
motor = Motor()
parachute = Parachute()
rocket = Rocket(environment=env, motor=motor, parachute=parachute)
logger = Feedback_Logger(
    rocket,
    ['position', 'velocity', 'acceleration', 'rotation', 'angular_velocity',
     'angular_acceleration'])

logger.splitting_arrays = True

sim = Simulation(
    {"apply_angular_forces": True, "max_frames": -1,
     "stopping_errors": False},
    env, rocket, logger)
sim.run_simulation()
