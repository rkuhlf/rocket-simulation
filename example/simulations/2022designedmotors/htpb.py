# SIMULATE HTPB-Nitrous
# Depending on which model of regression we use, we get either 120_000 Ns or 97_000 Ns. That is a 20% difference. Already, this is just for regression of a cylindrical tube. I have no idea how much worse it is going to get for complex geometry

from lib.simulation import MotorSimulation
from lib.logger import MotorLogger
from rocketparts.motor import CustomMotor
from rocketparts.motor.oxtank import OxTank
from rocketparts.motor.injector import Injector
from rocketparts.motor.combustionchamber import CombustionChamber
from rocketparts.motor.grain import HTPBGrain, marxman_doran_HTPB_nitrous, whitmore_regression_model
from rocketparts.motor.nozzle import Nozzle
from src.environment import Environment

from Visualization.MotorOpticalAnalysis import display_optical_analysis


def get_sim():
    # Usually we use 293.15
    ox = OxTank(temperature=293.15, length=2.54, diameter=0.1905, ox_mass=52.43)

    grain = HTPBGrain(verbose=True, length=0.88, port_diameter=0.11, outer_diameter=0.1651)
    # grain.regression_rate_function = whitmore_regression_model

    chamber = CombustionChamber(fuel_grain=grain, limit_pressure_change=False)
    
    injector = Injector(ox_tank=ox, combustion_chamber=chamber, orifice_count=4, orifice_diameter=0.005)
    nozzle = Nozzle(throat_diameter=0.045, area_ratio=4.78) # meters

    env = Environment()

    # I found pressure divergence at t_post = 0.2
    motor = CustomMotor(ox_tank=ox, injector=injector, combustion_chamber=chamber, nozzle=nozzle, environment=env, pressurization_time_increment=0.01, post_pressurization_time_increment=0.05)
    motor.data_path = "./Data/Input/CEA/CombustionLookupHTPB.csv"

    logger = MotorLogger(motor, target="motorOutput.csv", debug_every=0.5)

    sim = MotorSimulation(motor=motor, max_frames=-1, logger=logger, environment=env)

    return sim



if __name__ == "__main__":
    sim = get_sim()
    sim.run_simulation()

    display_optical_analysis(sim.logger.full_path)

