# Uses ABS-Nitrous
# Designed for a 120 kg wet mass rocket with 7.75 inch ID (I forgot to include paraffin thickness for the fuel grain) 
# Can get up to 125_000 Ns for a really long grain, only 92_000 Ns for a 1m grain. Or, if the regression equation is different, I can get 143000 for a really long grain
# Ox mass, combustion efficiency, and regression equation should be the main things


from random import choice, gauss, random
from lib.general import constant, modify_function_multiplication
from src.rocketparts.motorparts.grainGeometry import Annular, StarSwirl, multiply_areas

from lib.simulation import MotorSimulation
from lib.logging.logger import MotorLogger
from src.rocketparts.motor import CustomMotor
from src.rocketparts.motorparts.oxtank import OxTank, random_WSMR_temperature
from src.rocketparts.motorparts.grain import marxman_whitman_ABS_nitrous
from src.rocketparts.motorparts.injector import Injector, mass_flow_fitted_HTPV
from src.rocketparts.motorparts.combustionchamber import CombustionChamber
from src.rocketparts.motorparts.grain import ABSGrain, star_swirl_modifiers, power_ABS_nitrous_functions
from src.rocketparts.motorparts.pressureSwirlInjector import PSW_modifiers
from src.rocketparts.motorparts.nozzle import Nozzle
from src.environment import Environment

from Visualization.MotorOpticalAnalysis import display_optical_analysis


# tank liquid volume is 6400 in^3
# nozzle diameter is 6.4 cm
# Expansion ratio is 5.6
# tank start temp is 293.1
# ABS at 900 specific
# O/F is 6.9
# C* efficiency is 85
# ID is 3.75
# OD is 6.25
# Len is 30
# Injector diameter is 0.2


def get_sim() -> MotorSimulation:
    # Usually we use 293.15
    # The ID is 6.785 in
    # This length should give us enough room for liquid to expand until we reach
    # This length should be the length of a cylinder that gives you thhe desired total volume
    # Maybe add a little bit to this when I do the actual CG calculation
    ox = OxTank(temperature=293.15, length=4.29, diameter=0.172339, ox_mass=45, front=0)

    geo = Annular(length=0.762, outer_diameter=0.15875, port_diameter=0.09525)
    grain = ABSGrain(verbose=True, geometry=geo)
    grain.regression_rate_function = marxman_whitman_ABS_nitrous

    chamber = CombustionChamber(fuel_grain=grain, limit_pressure_change=False)
    
    injector = Injector(ox_tank=ox, combustion_chamber=chamber, orifice_count=5)
    injector.mass_flow_function = mass_flow_fitted_HTPV
    nozzle = Nozzle(throat_diameter=0.045, area_ratio=4.78) # meters

    env = Environment()

    # I found pressure divergence at t_post = 0.2
    motor = CustomMotor(ox_tank=ox, injector=injector, combustion_chamber=chamber, nozzle=nozzle, environment=env, pressurization_time_increment=0.007, post_pressurization_time_increment=0.04)
    motor.data_path = "./Data/Input/CEA/CombustionLookupABS.csv"

    logger = MotorLogger(motor, target="motorOutput.csv", debug_every=0.5)

    sim = MotorSimulation(motor=motor, max_frames=-1, logger=logger, environment=env)

    return sim

if __name__ == "__main__":
    sim = get_sim()
    sim.run_simulation()

    display_optical_analysis(sim.logger.full_path)

