# SIMULATE THE MOTOR I DESIGNED FOR MMR
# Unfortunately, I am going to have to just specify chamber pressure as constant
# With that inaccuracy, I am not even going to bother making any monte carlo style optimizers


# FIXME: at the moment, the combustion chamber pressure is probably far lower than reasonable, so I am just setting it constant. Unfortunately, this completely messes up the way the simulation works. The thrust is mostly dependent on the chamber pressure, so it just gives a really high value 

import sys
sys.path.append(".")

from simulation import MotorSimulation
from logger import MotorLogger
from RocketParts.motor import CustomMotor
from RocketParts.Motor.oxTank import OxTank
from RocketParts.Motor.injector import Injector
from RocketParts.Motor.combustionChamber import CombustionChamber
from RocketParts.Motor.grain import Grain, regression_rate_HTPB_nitrous
from RocketParts.Motor.nozzle import Nozzle
from environment import Environment

from Visualization.MotorOpticalAnalysis import display_optical_analysis



def get_sim():
    ox = OxTank(temperature=293.15, length=2.54, diameter=0.1905, ox_mass=52.43)

    grain = Grain(verbose=True, length=0.78, port_diameter=0.15, outer_diameter=0.1905)
    grain.set_regression_rate_function(regression_rate_HTPB_nitrous)

    chamber = CombustionChamber(fuel_grain=grain)
    chamber.set_pressure_constant(25 * 10**5) # Pa
    
    injector = Injector(ox_tank=ox, combustion_chamber=chamber, orifice_count=4, orifice_diameter=0.005)
    # Stuttgart optimized at 30 bar, but that gives me a totally funny shape because the pressure never reaches it
    # 0.08 gives me a reasonable thrust profile for the pressure I am workin at
    nozzle = Nozzle(throat_diameter=0.045, area_ratio=5.72) # meters
    env = Environment(time_increment=0.01)

    motor = CustomMotor(ox_tank=ox, injector=injector, combustion_chamber=chamber, nozzle=nozzle, environment=env)

    logger = MotorLogger(motor, target="motorOutput.csv")

    sim = MotorSimulation(motor=motor, max_frames=-1, logger=logger, environment=env)

    return sim



if __name__ == "__main__":
    sim = get_sim()
    sim.run_simulation()

    display_optical_analysis(sim.logger.full_path)

