# RUN A BASIC SIMULATION OF A HYBRID MOTOR
# All of the math is located within different files, and the motor file brings them all together
# This script simply instantiates them, runs the simulation, then makes a ton of graphs
# Right now, all of the inputs are based off of the Heros 3 rocket, developed at Stuttgart, because I am trying to confirm that my simulated output vaguely matches theirs
# TODO: Make this file run


import matplotlib.pyplot as plt
import numpy as np

from simulation import MotorSimulation
from Logging.logger import MotorLogger
from RocketParts.motor import CustomMotor
from RocketParts.Motor.oxTank import OxTank
from RocketParts.Motor.injector import Injector
from RocketParts.Motor.combustionChamber import CombustionChamber
from RocketParts.Motor.grain import Grain
from RocketParts.Motor.nozzle import Nozzle
from environment import Environment

from Visualization.MotorOpticalAnalysis import display_optical_analysis



def get_sim():
    ox = OxTank(temperature=300)
    # print(ox.temperature)
    grain = Grain(verbose=True, length=0.38)
    chamber = CombustionChamber(fuel_grain=grain)
    injector = Injector(ox_tank=ox, combustion_chamber=chamber)
    # Stuttgart optimized at 30 bar, but that gives me a totally funny shape because the pressure never reaches it

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
