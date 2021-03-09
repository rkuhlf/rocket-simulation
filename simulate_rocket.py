# Tanner's model currently reaces apogee at 3158 meters
# My model reaches 4081
# The difference is probably due to drag_coefficient implementation and momentum calculations

from environment import Environment
from motor import Motor
from rocket import Rocket
from logger import Feedback_Logger  # or just Logger
from simulation import Simulation


environment = Environment()


motor = Motor()
rocket = Rocket(environment=environment, motor=motor)
rocket.save_preset()


logger = Feedback_Logger(
    rocket,
    ['position', 'velocity', 'acceleration', 'rotation',
     'angular_velocity', 'angular_acceleration'])
rocket.logger = logger


sim = Simulation(environment, rocket, logger)

sim.run_simulation()
