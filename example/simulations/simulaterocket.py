# This is the main entry point into the program.
# It includes an example of how to set up and run a rocket simulation.

from src.environment import Environment
from src.rocketparts.motor import Motor
from rocket import Rocket
from src.rocketparts.parachute import ApogeeParachute, Parachute
from lib.logging.logger import RocketLogger
from lib.simulation import RocketSimulation
from Visualization.FlightOpticalAnalysis import display_optical_analysis



def get_simulation():
    env = Environment(time_increment=0.01, apply_wind=True)
    motor = Motor()

    drogue_parachute = ApogeeParachute(radius=0.3)
    main_parachute = Parachute()

    # By default, this rocket has no lift forces, and the only rotation is caused by drag
    rocket = Rocket(environment=env, motor=motor, parachutes=[drogue_parachute, main_parachute])
    
    logger = RocketLogger(rocket)

    logger.splitting_arrays = True

    sim = RocketSimulation(apply_angular_forces=True, environment=env, rocket=rocket, logger=logger)

    motor.simulation = sim
    
    return sim


def simulate_rocket():
    """Returns a simulation of the rocket flight (from get_simulation)."""

    sim = get_simulation()
    sim.run_simulation()

    return sim


if __name__ == "__main__":
    sim = simulate_rocket()

    display_optical_analysis(sim.logger.full_path)
