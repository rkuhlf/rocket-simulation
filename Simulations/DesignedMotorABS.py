# Uses ABS-Nitrous
# Designed for a 120 kg wet mass rocket with 7.75 inch ID (I forgot to include paraffin thickness for the fuel grain) 
# Can get up to 125_000 Ns for a really long grain, only 92_000 Ns for a 1m grain. Or, if the regression equation is different, I can get 143000 for a really long grain
# Ox mass, combustion efficiency, and regression equation should be the main things


from random import gauss

from simulation import MotorSimulation
from logger import MotorLogger
from RocketParts.motor import CustomMotor
from RocketParts.Motor.oxTank import OxTank, random_WSMR_temperature
from RocketParts.Motor.injector import Injector
from RocketParts.Motor.combustionChamber import CombustionChamber
from RocketParts.Motor.grain import ABSGrain, marxman_whitman_ABS_nitrous
from RocketParts.Motor.nozzle import Nozzle
from environment import Environment

from Visualization.MotorOpticalAnalysis import display_optical_analysis


def get_sim() -> MotorSimulation:
    # Usually we use 293.15
    ox = OxTank(temperature=293.15, length=2.54, diameter=0.1905, ox_mass=52.43, front=0)

    # This is why you cannot simply use a cylindrical port. 4.5 meters (for the whitmore model) is too long, simple as that
    grain = ABSGrain(verbose=True, length=1.3, port_diameter=0.12, outer_diameter=0.1651, center_of_gravity=3.4)
    grain.regression_rate_function = marxman_whitman_ABS_nitrous

    chamber = CombustionChamber(fuel_grain=grain, limit_pressure_change=False)
    
    injector = Injector(ox_tank=ox, combustion_chamber=chamber, orifice_count=4, orifice_diameter=0.005)
    nozzle = Nozzle(throat_diameter=0.045, area_ratio=4.78) # meters

    env = Environment()

    # I found pressure divergence at t_post = 0.2
    motor = CustomMotor(ox_tank=ox, injector=injector, combustion_chamber=chamber, nozzle=nozzle, environment=env, pressurization_time_increment=0.007, post_pressurization_time_increment=0.04)
    motor.data_path = "./Data/Input/CEA/CombustionLookupABS.csv"

    logger = MotorLogger(motor, target="motorOutput.csv", debug_every=0.5)

    sim = MotorSimulation(motor=motor, max_frames=-1, logger=logger, environment=env)

    return sim

def get_randomized_sim() -> MotorSimulation:
    """Used for monte carlo simulations. This is just me adding in standard deviations for all of the design parameters for this motor. I tried to be as realistic as possible, but I just randomized the regression laws, and I just made up multiplicative factors for some things."""

    sim = get_sim()
    m: CustomMotor = sim.motor

    # --- Ox Tank ---
    m.ox_tank.temperature = random_WSMR_temperature()
    m.ox_tank.initial_temperature = m.ox_tank.temperature
    # I think we probably get most of the way filled quite often, but sometimes we do not
    m.ox_tank.ox_mass *= min(1, gauss(0.9, 0.1))
    m.ox_tank.initial_mass = m.ox_tank.ox_mass

    # Almost certainly correct
    m.ox_tank.length *= gauss(1, 0.005)

    # --- Injector ---
    # TODO: I need to redo the models of injector flow the same way I did regression equations; it is already sort of close; replace this with a function in the thing that makes a random injector
    m.injector.discharge_coefficient = min(1, gauss(0.7, 0.15))
    m.injector.orifice_diameter *= gauss(1, 0.03)

    # --- Combustion Chamber ---
    m.cstar_efficiency = min(1, gauss(0.83, 0.06))
    # These are pretty set in stone, but there might be some variation
    m.combustion_chamber.precombustion_chamber.length *= gauss(1, 0.01)
    m.combustion_chamber.postcombustion_chamber.length *= gauss(1, 0.01)
    # I really do not know what we are going to end up at, but I am assuming we can get it accurate, so this does not have much variation from what I think it currently is
    m.combustion_chamber.fuel_grain.length *= gauss(1, 0.02)

    # --- Fuel Grain ---
    f: ABSGrain = m.fuel_grain
    # Different varieties have different values
    f.density *= gauss(1, 0.05)
    f.port_radius *= gauss(1, 0.002)
    f.initial_mass = f.fuel_mass
    f.initial_radius = f.port_radius
    f.randomize_regression_algorithm()

    # --- Nozzle ---
    # This one is not really a randomization because that would require running CEA again every time, and I can't really be bothered to wait that long
    # This one is still included because it will change the mass flow rates and the pressures
    m.nozzle.throat_radius *= gauss(1, 0.001)

    
    return sim



if __name__ == "__main__":
    sim = get_sim()
    sim.run_simulation()

    display_optical_analysis(sim.logger.full_path)

