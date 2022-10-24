from typing import Callable

from RocketParts.Motor.grainGeometry import StarSwirl
from simulation import MotorSimulation
from logger import MotorLogger
from RocketParts.motor import CustomMotor
from RocketParts.Motor.oxTank import OxTank
from RocketParts.Motor.injector import Injector, mass_flow_fitted_HTPV
from RocketParts.Motor.combustionChamber import CombustionChamber
from RocketParts.Motor.grain import ABSGrain, Grain
from RocketParts.Motor.nozzle import Nozzle
from environment import Environment

from Visualization.MotorOpticalAnalysis import display_optical_analysis


def custom_regression_function(grain: Grain) -> Callable:
    time = grain.motor.environment.time

    base_power_regression = 2.623e-5 * grain.flux ** 0.664

    if time < 5:
        # Double it for the swirl grain effect
        base_power_regression *= 2

    if time < 8:
        # Double it for the pressure swirl
        base_power_regression *= 2

    return base_power_regression

def custom_ox_flow_function(injector: Injector) -> Callable:
    time = injector.simulation.environment.time

    base = mass_flow_fitted_HTPV(injector)

    if time > 8:
        base *= 1.1
    
    if time > 12:
        base *= 1.4

    return base


def get_sim() -> MotorSimulation:
    """Attempt to recreate the inputs and functions that actually occurred when Horizon 1 launched in 2022.
    """
    # ox mass is based on the 80 lbs that they recorded
    # Temperature is 67.5 F converted to Kelvin
    ox = OxTank(temperature=293, length=2.67, diameter=0.172339, ox_mass=36.3, front=0)

    geo = StarSwirl(length=0.788, outer_diameter=0.17145)
    grain = ABSGrain(verbose=True, center_of_gravity=3.19, geometry=geo)
    grain.regression_rate_function = custom_regression_function
    grain.density = 980
    grain.initial_mass = grain.fuel_mass

    chamber = CombustionChamber(fuel_grain=grain, limit_pressure_change=False)
    
    injector = Injector(ox_tank=ox, combustion_chamber=chamber, orifice_count=5)
    injector.mass_flow_function = custom_ox_flow_function
    nozzle = Nozzle(throat_diameter=0.045, area_ratio=4.78) # meters

    env = Environment()

    motor = CustomMotor(ox_tank=ox, injector=injector, combustion_chamber=chamber, nozzle=nozzle, environment=env, pressurization_time_increment=0.007, post_pressurization_time_increment=0.04)
    motor.data_path = "./Data/Input/CEA/CombustionLookupABS.csv"
    grain.motor = motor
    motor.cstar_efficiency = 0.9

    logger = MotorLogger(motor, target="motorOutput.csv", debug_every=0.5)

    sim = MotorSimulation(motor=motor, max_frames=-1, logger=logger, environment=env)
    injector.simulation = sim

    return sim



if __name__ == "__main__":
    sim = get_sim()
    sim.logger.target = "flightMotor2022-Temporary.csv"

    sim.run_simulation()
    

    display_optical_analysis(sim.logger.full_path)

