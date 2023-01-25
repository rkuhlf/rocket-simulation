# Uses ABS-Nitrous
# Based strongly on designedmotor_abs, but this is adjusted to be slightly better?

from random import choice, gauss, random
from lib.general import modify_function_multiplication
from src.rocketparts.motorparts.grainGeometry import StarSwirl, multiply_areas

from lib.simulation import MotorSimulation
from lib.logging.logger import MotorLogger
from src.rocketparts.motor import CustomMotor
from src.rocketparts.motorparts.oxtank import OxTank, random_WSMR_temperature
from src.rocketparts.motorparts.injector import Injector, mass_flow_fitted_HTPV
from src.rocketparts.motorparts.combustionchamber import CombustionChamber
from src.rocketparts.motorparts.grain import ABSGrain, star_swirl_modifiers, power_ABS_nitrous_functions
from src.rocketparts.motorparts.pressureSwirlInjector import PSW_modifiers
from src.rocketparts.motorparts.nozzle import Nozzle
from src.environment import Environment

from Visualization.MotorOpticalAnalysis import display_optical_analysis



adjusted_regression_functions = []


def get_sim() -> MotorSimulation:
    # Usually we use 293.15
    # The ID is 6.785 in
    # This length should give us enough room for liquid to expand until we reach
    # This length should be the length of a cylinder that gives you thhe desired total volume
    # Maybe add a little bit to this when I do the actual CG calculation
    ox = OxTank(temperature=293.15, length=2.67, diameter=0.172339, ox_mass=45, front=0)

    geo = StarSwirl(length=0.788, outer_diameter=0.17145)
    grain = ABSGrain(verbose=True, center_of_gravity=3.19, geometry=geo)
    adjusted_regression_functions = generate_regression_functions()
    grain.regression_rate_function = adjusted_regression_functions[-2]

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


def generate_regression_functions():
    global adjusted_regression_functions

    base_algorithms = power_ABS_nitrous_functions

    pressure_swirl_adjusted = []
    # Pressure swirl
    for alteration_method in PSW_modifiers:
        for base_algorithm in base_algorithms:
            pressure_swirl_adjusted.append(alteration_method(base_algorithm))

    star_swirl_adjusted = []
    # Star Swirl
    for alteration_method in star_swirl_modifiers:
        for base_algorithm in pressure_swirl_adjusted:
            star_swirl_adjusted.append(alteration_method(base_algorithm))
    
    adjusted_regression_functions = star_swirl_adjusted
    return adjusted_regression_functions


def get_random_adjusted_ABS_regression_function():
    global adjusted_regression_functions
    
    # We only want to generate this if it asks for it. Basically naive caching
    if len(adjusted_regression_functions) == 0:
        adjusted_regression_functions = generate_regression_functions()
    
    return choice(adjusted_regression_functions)




def get_randomized_sim() -> MotorSimulation:
    """Used for monte carlo simulations. This is just me adding in standard deviations for all of the design parameters for this motor. I tried to be as realistic as possible, but I just randomized the regression laws, and I just made up multiplicative factors for some things."""

    sim = get_sim()
    m: CustomMotor = sim.motor

    # --- Ox Tank ---
    m.ox_tank.temperature = random_WSMR_temperature()
    m.ox_tank.initial_temperature = m.ox_tank.temperature
    # I think we probably get most of the way filled quite often, but sometimes we do not
    # They are looking at a load cell to see if we get completely filled
    # Last year they actually overfilled
    m.ox_tank.ox_mass *= gauss(0.99, 0.02)

    # Commented out because I do not believe this will happen. If it does, we can just borrow someone else's oxidizer
    # if random() < 0.05:
    #     # If, for some reason, we have to drain the entire ox tank, we will only have a ~50% fill
    #     m.ox_tank.ox_mass *= 0.6
    
    # m.ox_tank.initial_mass = m.ox_tank.ox_mass

    # Almost certainly correct; also it makes no difference so this is pointless
    m.ox_tank.length *= gauss(1, 0.005)

    # --- Injector ---
    # They told us exactly what it would be, but I do not believe them; could also simulate something getting stuck in one of them
    m.injector.mass_flow_function = modify_function_multiplication(m.injector.mass_flow_function, gauss(1, 0.02))

    # --- Combustion Chamber ---
    m.cstar_efficiency = min(1, gauss(0.85, 0.04))
    # These are pretty set in stone, but there might be some variation
    m.combustion_chamber.precombustion_chamber.length *= gauss(1, 0.02)
    m.combustion_chamber.postcombustion_chamber.length *= gauss(1, 0.02)
    # I really do not know what we are going to end up at, but I am assuming we can get it accurate, so this does not have much variation from what I think it currently is
    m.combustion_chamber.fuel_grain.geometry.length *= gauss(1, 0.005)

    # --- Fuel Grain ---
    f: ABSGrain = m.fuel_grain

    density_guess = 920
    f.density = gauss(density_guess, density_guess * 0.001)
    f.initial_mass = f.fuel_mass

    f.regression_rate_function = get_random_adjusted_ABS_regression_function()
    
    # TODO: Create a function that interpolates the geometry between the swirled shape and a regular cylinder.
    f.geometry.area_function = multiply_areas(f.geometry.area_function, gauss(0.95, 0.03), gauss(1, 0.005), gauss(1, 0.001))

    # --- Nozzle ---
    # This one is not really a randomization because that would require running CEA again every time, and I can't really be bothered to wait that long
    # This one is still included because it will change the mass flow rates and the pressures
    m.nozzle.throat_radius *= gauss(1, 0.001)
    m.nozzle.efficiency *= min(gauss(0.99, 0.005), 1)

    # TODO: randomize the nozzle performance multiplier
    
    return sim

def get_randomized_percent_fill(percent_fill=0.5):
    sim = get_randomized_sim()
    sim.motor.ox_tank.ox_mass *= percent_fill
    
    return sim

def get_randomized_percent_fill_closure(percent_fill=0.5):
    def inner():
        return get_randomized_percent_fill(percent_fill=percent_fill)
    
    return inner


if __name__ == "__main__":
    sim = get_sim()
    sim.run_simulation()

    display_optical_analysis(sim.logger.full_path)

