import matplotlib
from matplotlib import pyplot as plt
import pandas as pd
from Data.Input.models import get_density, get_speed_of_sound
from Helpers.data import interpolated_lookup
from Helpers.general import modify_function_multiplication
from RocketParts.Motor.grainGeometry import StarSwirl, multiply_areas

from simulation import MotorSimulation
from logger import MotorLogger
from RocketParts.motor import CustomMotor
from RocketParts.Motor.oxTank import OxTank
from RocketParts.Motor.injector import Injector, mass_flow_fitted_HTPV
from RocketParts.Motor.combustionChamber import CombustionChamber
from RocketParts.Motor.grain import ABSGrain, Grain, star_swirl_modifiers, power_ABS_nitrous_functions, regression_rate_ABS_nitrous_constant
from RocketParts.Motor.pressureSwirlInjector import PSW_modifiers
from RocketParts.Motor.nozzle import Nozzle
from environment import Environment

from Visualization.MotorOpticalAnalysis import display_optical_analysis


def custom_regression_function(grain: Grain):
    time = grain.motor.environment.time

    base_power_regression = 2.623e-5 * grain.flux ** 0.664

    if time < 5:
        # Double it for the swirl grain effect
        base_power_regression *= 2

    if time < 8:
        # Double it for the pressure swirl
        base_power_regression *= 2

    return base_power_regression

def custom_ox_flow_function(injector: Injector):
    time = injector.simulation.environment.time

    base = mass_flow_fitted_HTPV(injector)

    if time > 8:
        base *= 1.1
    
    if time > 12:
        base *= 1.4

    return base


def get_sim() -> MotorSimulation:
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


AREA = 0.0262677157 # m^2
telemetrum_data = pd.read_csv("Data/Output/TelemetrumData.csv")
CD_data = pd.read_csv("Data/Input/Aerodynamics/FinalGuessAtWSMR.CSV")
motor_output = pd.read_csv("Data/Output/motorOutput.csv")
approximate_burn_time = 30
approximate_parachute_time = 50

# Ignoring everything that happens after parachute because I am not super concerned with tumbling simulations
telemetrum_data = telemetrum_data[telemetrum_data["Time (s)"] < approximate_parachute_time]


def get_mass(row):
    prop_mass = interpolated_lookup(motor_output, "time", row["Time (s)"], "propellant_mass", safe=True)

    return 48 + prop_mass

def compare_to_flight():
    predictions = pd.DataFrame()
    predictions["Time (s)"] = telemetrum_data["Time (s)"]

    net_forces = []
    weights = []
    drags = []
    thrusts = []
    predicted_drags = []
    for index, row in telemetrum_data.iterrows():
        mass = get_mass(row)
        net_force = row["acceleration"] * mass

        weight = mass * 9.81
        
        # If the motor is burning, we have to guess what the drag should be
        density = get_density(row["altitude"] / 1000)
        speed = row["speed"]
        speed_of_sound = get_speed_of_sound(row["altitude"] / 1000)

        CD = interpolated_lookup(CD_data, "Mach", speed / speed_of_sound, "CD", safe=True)
        
        predicted_drags.append(-1/2 * density * speed ** 2 * AREA * CD)
        if row["Time (s)"] < approximate_burn_time:
            drag = 1/2 * density * speed ** 2 * AREA * CD
        else:
            drag = abs(net_force) - abs(weight)
        
        weights.append(-weight)
        net_forces.append(net_force)
        drags.append(-drag)
        
    telemetrum_data["Weight"] = weights
    telemetrum_data["Net Force"] = net_forces
    telemetrum_data["Drag"] = drags
    telemetrum_data["Thrust"] = telemetrum_data["Net Force"] - telemetrum_data["Weight"] - telemetrum_data["Drag"]
    predictions["Drag"] = predicted_drags


    # plt.plot(telemetrum_data["Time (s)"], telemetrum_data["Net Force"])
    # plt.plot(telemetrum_data["Time (s)"], telemetrum_data["Weight"])
    plt.plot(telemetrum_data["Time (s)"], telemetrum_data["Thrust"], label="Actual Thrust")
    # plt.plot(motor_output["time"], motor_output["thrust"], label="Predicted Thrust")

    plt.plot(telemetrum_data["Time (s)"], telemetrum_data["Net Force"], label="Net Force")
    plt.plot(telemetrum_data["Time (s)"], telemetrum_data["Drag"], label="Drag")
    plt.plot(telemetrum_data["Time (s)"], telemetrum_data["Weight"], label="Weight")

    plt.plot(predictions["Time (s)"], predictions["Drag"], label="Predicted Drag")
    plt.legend()
    plt.show()


if __name__ == "__main__":
    # sim = get_sim()
    # sim.run_simulation()

    # print(f"Average Regression: {sim.chamber.fuel_grain.approximate_average_regression_rate(sim.burn_time) * 1000} mm/s")

    # display_optical_analysis(sim.logger.full_path)


    compare_to_flight()

    pass

