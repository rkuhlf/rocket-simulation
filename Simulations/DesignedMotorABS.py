# SIMULATE THE MOTOR I DESIGNED FOR MMR
# Uses HTPB-Nitrous
# Designed for a 120 kg wet mass rocket with 7.75 inch ID (I forgot to include paraffin thickness for the fuel grain) 
# Can get up to 125_000 Ns for a really long grain, only 92_000 Ns for a 1m grain. Or, if the regression equation is different, I can get 143000 for a really long grain

# TODO: create a designed file like this for ABS and Paraffin also


from simulation import MotorSimulation
from logger import MotorLogger
from RocketParts.motor import CustomMotor
from RocketParts.Motor.oxTank import OxTank
from RocketParts.Motor.injector import Injector
from RocketParts.Motor.combustionChamber import CombustionChamber
from RocketParts.Motor.grain import ABSGrain, marxman_whitman_ABS_nitrous
from RocketParts.Motor.nozzle import Nozzle
from environment import Environment

from Visualization.MotorOpticalAnalysis import display_optical_analysis


def get_sim():
    # Usually we use 293.15
    ox = OxTank(temperature=293.15, length=2.54, diameter=0.1905, ox_mass=52.43)

    # This is why you cannot simply use a cylindrical port. 4.5 meters (for the whitmore model) is too long, simple as that
    grain = ABSGrain(verbose=True, length=1.3, port_diameter=0.12, outer_diameter=0.1651)
    grain.regression_rate_function = marxman_whitman_ABS_nitrous

    chamber = CombustionChamber(fuel_grain=grain, limit_pressure_change=False)
    
    injector = Injector(ox_tank=ox, combustion_chamber=chamber, orifice_count=4, orifice_diameter=0.005)
    nozzle = Nozzle(throat_diameter=0.045, area_ratio=4.78) # meters

    env = Environment()

    # I found pressure divergence at t_post = 0.2
    motor = CustomMotor(ox_tank=ox, injector=injector, combustion_chamber=chamber, nozzle=nozzle, environment=env, pressurization_time_increment=0.01, post_pressurization_time_increment=0.05)
    motor.data_path = "./Data/Input/CombustionLookupABS.csv"

    logger = MotorLogger(motor, target="motorOutput.csv", debug_every=0.5)

    sim = MotorSimulation(motor=motor, max_frames=-1, logger=logger, environment=env)

    return sim



if __name__ == "__main__":
    sim = get_sim()
    sim.run_simulation()

    display_optical_analysis(sim.logger.full_path)

