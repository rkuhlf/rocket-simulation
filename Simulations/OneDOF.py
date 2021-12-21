# SIMULATE ROCKET IN ONE DEGREE OF FREEDOM
# Simply disable the wind in the environment and shoot the rocket straight up. Because the parachute provides all of the CD on the descent, it doesn't matter that the rocket never turns over

import numpy as np


from environment import Environment
from RocketParts.motor import Motor
from RocketParts.massObject import MassObject
from rocket import Rocket
from RocketParts.parachute import ApogeeParachute
from logger import RocketLogger
from simulation import RocketSimulation
from Data.Input.goddardModels import get_sine_interpolated_center_of_pressure, linear_approximated_normal_force, assumed_zero_AOA_CD

from Visualization.FlightOpticalAnalysis import display_optical_analysis


def get_mass_objects():
    # Everything in meters and kilograms designed around a rocket of length 19 feet or 5.7 meters
    # You can't really fudge this too much because it is also necessary for moment of inertia

    nose_cone_tip = MassObject(center_of_gravity=0.005, mass=0.1)
    nose_cone = MassObject(center_of_gravity=0.699, mass=1.975)
    fiberglass_avionics_tube = MassObject(center_of_gravity=1.52, mass=2.596)
    avionics_bay = MassObject(center_of_gravity=1.52, mass=10)
    ox_tank_shell = MassObject(center_of_gravity=2.59, mass=26.953)
    injector = MassObject(center_of_gravity=3.86, mass=0.2)
    phenolic = MassObject(center_of_gravity=4.36, mass=5)
    carbon_fiber_overwrap = MassObject(center_of_gravity=4.36, mass=2.25)
    nozzle_overwrap = MassObject(center_of_gravity=5.64, mass=0.57)
    fins = MassObject(center_of_gravity=5.51, mass=0.6)
    nozzle = MassObject(center_of_gravity=5.64, mass=10)

    # Should come out to about 60 kg
    return [nose_cone_tip, nose_cone, fiberglass_avionics_tube, ox_tank_shell, injector, phenolic, carbon_fiber_overwrap, fins, nozzle_overwrap, nozzle, avionics_bay]


def get_sim():
    env = Environment(time_increment=0.05, apply_wind=False)
    motor = Motor(front=2, center_of_gravity=2, mass=60, propellant_mass=60, thrust_curve="Data/Input/mmrThrust.csv", environment=env)

    main_parachute = ApogeeParachute(diameter=4.8768)
    rocket = Rocket(radius=0.1016, length=5.7912, rotation=np.array([np.pi / 2, 0.0872665], dtype="float64"),
        environment=env, motor=motor, parachutes=[])
    rocket.set_CP_function(get_sine_interpolated_center_of_pressure)
    rocket.set_CL_function(linear_approximated_normal_force)
    rocket.set_CD_function(assumed_zero_AOA_CD)
    rocket.set_moment_constant(250)

    mass_objects = [motor]
    mass_objects.extend(get_mass_objects())
    rocket.mass_objects = mass_objects

    sim = RocketSimulation(apply_angular_forces=False, environment=env, rocket=rocket)
    motor.simulation = sim


    return sim


if __name__ == "__main__":
    sim = get_sim()
    sim.run_simulation()
    display_optical_analysis(sim.logger.full_path)
    