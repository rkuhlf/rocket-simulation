# RUN A BASIC SIMULATION OF A HYBRID MOTOR
# All of the math is located within different files, and the motor file brings them all together
# This script simply instantiates them, runs the simulation, then makes a ton of graphs
# Right now, all of the inputs are based off of the Heros 3 rocket, developed at Stuttgart, because I am trying to confirm that my simulated output vaguely matches theirs


import matplotlib.pyplot as plt
import numpy as np

from simulation import MotorSimulation
from logger import MotorLogger
from rocketparts.motor import CustomMotor
from rocketparts.motor.oxtank import OxTank
from rocketparts.motor.injector import Injector, mass_flow_fitted_HTPV
from rocketparts.motor.combustionchamber import CombustionChamber
from rocketparts.motor.grain import Grain
from rocketparts.motor.nozzle import Nozzle
from environment import Environment

from visualization.MotorOpticalAnalysis import display_optical_analysis



def get_sim():
    ox = OxTank(temperature=300, front=0)

    grain = Grain(verbose=True, length=0.38, center_of_gravity=3.4)
    chamber = CombustionChamber(fuel_grain=grain)
    injector = Injector(ox_tank=ox, combustion_chamber=chamber)
    injector.orifice_count = 4
    injector.mass_flow_function = mass_flow_fitted_HTPV

    nozzle = Nozzle(throat_diameter=0.04, fuel_grain=grain) # meters
    env = Environment(time_increment=0.01)

    motor = CustomMotor(ox_tank=ox, injector=injector, combustion_chamber=chamber, nozzle=nozzle, environment=env)

    logger = MotorLogger(motor, target="motorOutput.csv")

    sim = MotorSimulation(motor=motor, max_frames=-1, logger=logger, environment=env)

    return sim



if __name__ == "__main__":
    sim = get_sim()
    sim.run_simulation()

    display_optical_analysis(sim.logger.full_path)
