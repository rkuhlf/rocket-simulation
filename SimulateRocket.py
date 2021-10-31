# SIMULATE A SINGLE ROCKET
# This is the main entry point into the program
# If you want some other examples for how to run a simulation, or other applications of the rocket simulation, look under Simulations/

from numpy import array

from environment import Environment
from RocketParts.motor import Motor
from rocket import Rocket
from RocketParts.parachute import ApogeeParachute, Parachute
from logger import Feedback_Logger  # , Logger
from simulation import Simulation
from Simulations.verifiedSimulation import VerifiedSimulation


def get_simulation():
    # additional function because it turns out I need access to this in other files
    env = Environment({"time_increment": 0.01, "apply_wind": True})
    motor = Motor()

    drogue_parachute = ApogeeParachute({"radius": 0.2})
    main_parachute = Parachute()
    rocket = Rocket(environment=env, motor=motor, parachutes=[drogue_parachute, main_parachute])
    
    logger = Feedback_Logger(
        rocket,
        ['position', 'velocity', 'acceleration', 'rotation', 'angular_velocity',
        'angular_acceleration'], target="output.csv")

    logger.splitting_arrays = True

    sim = Simulation(
        {"apply_angular_forces": True, "max_frames": -1,
        "stopping_errors": False},
        env, rocket, logger)

    motor.simulation = sim
    
    return sim


def simulate_rocket():
    sim = get_simulation()
    sim.run_simulation()

    return sim


if __name__ == "__main__":
    sim = simulate_rocket()

    from Visualization.FlightOpticalAnalysis import display_optical_analysis
    display_optical_analysis(sim.logger.full_path)
