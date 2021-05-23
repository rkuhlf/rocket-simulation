# Tanner's model currently reaces apogee at 3158 meters
# My model reaches 2949
# RASAero reaces 3350 with a converted rocket that is probably too long for how light it is
# The difference is probably due to drag_coefficient implementation and momentum calculations

from environment import Environment
from motor import Motor
from rocket import Rocket
from parachute import Parachute
from logger import Feedback_Logger  # or just Logger
from simulation import Simulation


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
    {"apply_angular_forces": True, "max_frames": -1},
    env, rocket, logger)
sim.run_simulation()


# Example 1
"""
environment = Environment()
motor = Motor()
rocket = Rocket(environment=environment, motor=motor)


logger = Feedback_Logger(
    rocket,
    ['position', 'velocity', 'acceleration', 'rotation',
     'angular_velocity', 'angular_acceleration'])
rocket.logger = logger

sim = Simulation(environment, rocket, logger)

sim.run_simulation()
"""


# Example 2
"""
rocket = Rocket()
rocket.load_preset("TannerModel")


logger = Logger(rocket, ['position', 'rotation'])

sim = Simulation(rocket.environment, rocket, logger)

sim.run_simulation()
"""
