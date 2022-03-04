# Uses ABS-Nitrous
# Designed for a 120 kg wet mass rocket with 7.75 inch ID (I forgot to include paraffin thickness for the fuel grain) 
# Can get up to 125_000 Ns for a really long grain, only 92_000 Ns for a 1m grain. Or, if the regression equation is different, I can get 143000 for a really long grain
# Ox mass, combustion efficiency, and regression equation should be the main things


from random import choice, gauss, random
from Helpers.general import modify_function_multiplication
from RocketParts.Motor.grainGeometry import StarSwirl, multiply_areas

from simulation import MotorSimulation
from logger import MotorLogger
from RocketParts.motor import CustomMotor
from RocketParts.Motor.oxTank import OxTank, random_WSMR_temperature
from RocketParts.Motor.injector import Injector, mass_flow_fitted_HTPV
from RocketParts.Motor.combustionChamber import CombustionChamber
from RocketParts.Motor.grain import ABSGrain, star_swirl_modifiers, power_ABS_nitrous_functions
from RocketParts.Motor.pressureSwirlInjector import PSW_modifiers
from RocketParts.Motor.nozzle import Nozzle
from environment import Environment

from Visualization.MotorOpticalAnalysis import display_optical_analysis



adjusted_regression_functions = []


def get_sim() -> MotorSimulation:
    # Usually we use 293.15
    # The ID is 6.785 in
    # This length should give us enough room for liquid to expand until we reach
    ox = OxTank(temperature=293.15, length=2.67, diameter=0.172339, ox_mass=45, front=0)

    geo = StarSwirl(length=0.78, outer_diameter=0.17145)
    # Start of ox tank is 63 inches. Middle of fuel grain is 191 inches. That should be 3.25 meters away
    grain = ABSGrain(verbose=True, center_of_gravity=3.2512, geometry=geo)
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
    m.ox_tank.ox_mass *= min(1, gauss(0.93, 0.06))

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
    m.combustion_chamber.precombustion_chamber.length *= gauss(1, 0.01)
    m.combustion_chamber.postcombustion_chamber.length *= gauss(1, 0.01)
    # I really do not know what we are going to end up at, but I am assuming we can get it accurate, so this does not have much variation from what I think it currently is
    m.combustion_chamber.fuel_grain.geometry.length *= gauss(1, 0.005)

    # --- Fuel Grain ---
    f: ABSGrain = m.fuel_grain
    # Different varieties have different values
    f.density *= gauss(1, 0.05)
    # f.port_radius *= gauss(1, 0.002)
    f.initial_mass = f.fuel_mass
    # f.initial_radius = f.port_radius
    f.regression_rate_function = get_random_adjusted_ABS_regression_function()
    
    f.geometry.area_function = multiply_areas(f.geometry.area_function, gauss(0.95, 0.03), gauss(1, 0.005), gauss(1, 0.001))

    # --- Nozzle ---
    # This one is not really a randomization because that would require running CEA again every time, and I can't really be bothered to wait that long
    # This one is still included because it will change the mass flow rates and the pressures
    m.nozzle.throat_radius *= gauss(1, 0.001)

    # TODO: randomize the nozzle performance multiplier
    
    return sim



if __name__ == "__main__":
    sim = get_sim()
    sim.run_simulation()

    display_optical_analysis(sim.logger.full_path)

