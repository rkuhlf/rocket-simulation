# SEVERAL FUNCTIONS TO DESIGN A ROCKET
# At the moment, I am setting it up to design the rocket for the math model review for Goddard 2021
# We are using HTPB and Nitrous
# We have a seven and a half inch ID and an 8 inch OD for the entire rocket
# Based off of some runs of the OptimizeBurnTime.py file for a similar size rocket, we want to aim for a liquid burn time of about 22 seconds
# I am going for a dry mass of 60 kg based off of a preliminary DiameterStudy


# TODO: figure out how to scrape CEA data from HTPB without showing it on the Github page but still maintaining access to it on all of my devices
# TODO: scrape HTPB CEA data
# TODO: separate HTPB CEA from Paraffin CEA
# TODO: figure out optimum O/F ratio from HTPB CEA

import numpy as np
import sys
sys.path.append(".")

from Helpers.design import get_propellant_mass, get_ox_mass, get_fuel_mass
# from Helpers.general import get_radius

from RocketParts.Motor.nitrousProperties import get_liquid_nitrous_density, get_gaseous_nitrous_density, get_nitrous_vapor_pressure

from RocketParts.Motor.grain import determine_optimal_starting_diameter, regression_rate_HTPB_nitrous, find_required_length as find_required_length_fuel
from RocketParts.Motor.oxTank import find_required_length as find_required_length_oxidizer
from RocketParts.Motor.injector import determine_required_thickness, determine_orifice_count_MR, find_mass_flow_MR, get_cross_sectional_area
from RocketParts.Motor.nozzle import find_nozzle_length, find_equilibrium_throat_area, find_equilibrium_throat_diameter, determine_expansion_ratio


#region PRESETS
total_mass = 120 # kg
outer_diameter = 0.2032 # meters
inner_diameter = outer_diameter - 0.0127 # meters

liquid_burn_time = 21 # seconds

combustion_chamber_pressure = 25 * 10 ** 5
# Determined in the OptimizeOFAtPressure.py script
OF = 6.93
# Based on the combustion chamber and a constant optimum OF, we can figure out what C* to optimize to - it looks like we should get around 1600 m/s, theoretically
# Once again, it would be better to do the adjustments for the nozzle programmatically
cstar = 1600 # m/s
fuel_density = 920 # kg / m^3

# TODO: redesign this so that we can atmospheric pressure programatically - I will have to rewrite environment to take data for atmospheric pressure as a function of time, then do the motor simulation repeatedly with different area ratios
# This number is slightly lower than where I predict the rocket to be about halfway through the burn (10-ish seconds)
# TODO: check that it isn't going to get seriously over-expanded at the bottom and break the flow
exterior_pressure = 75000 # Pa


ox_tank_initial_temperature = 293 # Kelvin
# Calculated from OxTankCG.py
ox_tank_average_temperature = 283 # Kelvin

injector_CD = 0.68
injector_diameter = 0.005
#endregion

propellant_mass = get_propellant_mass(total_mass)
ox_mass = get_ox_mass(propellant_mass, OF)
fuel_mass = get_fuel_mass(propellant_mass, OF)

# Looks like we always end up with about 5 kg of oxidizer left over as gas, that means we need to burn through 5 less than that to get the right burn time for the liquid; Scale it up to include fuel proportional to OF
nozzle_mass_flow = (ox_mass - 5) * (1 + 1 / OF) / liquid_burn_time
print(nozzle_mass_flow)

# TODO: double check this gamma value after I finish optimizing the other stuff; it is very important to get it right
optimized_area_ratio = determine_expansion_ratio(combustion_chamber_pressure, exterior_pressure, 1.22)

# Check the diameter of the nozzle isn't going to exceed the diameter of the rocket
inlet_diameter = inner_diameter * 0.75
throat_diameter = find_equilibrium_throat_diameter(cstar, combustion_chamber_pressure, nozzle_mass_flow)
exit_diameter = throat_diameter * optimized_area_ratio ** (1/2)

nozzle_length = find_nozzle_length(40 * np.pi / 180, inlet_diameter, throat_diameter, 15 * np.pi/180, exit_diameter, conical_proportion=0.8)

print(f"The rocket's throat diameter should be {throat_diameter} meters and the exit diameter should be {exit_diameter} meters, giving an area ratio of {optimized_area_ratio}. Inlet diameter is guesstimated at {inlet_diameter} meters")


ox_flow = nozzle_mass_flow * OF / (OF + 1)
print(ox_flow)

# 4030567 Pa is taken from OxTankCG.py
# Side note, injector design is extremely dependent on ox tank pressure
unrounded_orifices = determine_orifice_count_MR(ox_flow, (4030567 - combustion_chamber_pressure), get_liquid_nitrous_density(ox_tank_average_temperature), get_gaseous_nitrous_density(ox_tank_average_temperature), injector_diameter, injector_CD)
orifices = round(unrounded_orifices)
print(f"To be fully optimized, you should really have {unrounded_orifices} orifices. Unfortunately, the closest you can get is {orifices}")

# This only works because the area scales linearly with the flow
new_nozzle_flow = nozzle_mass_flow * orifices / unrounded_orifices
new_burn_time = liquid_burn_time * unrounded_orifices / orifices

print(f"This gives you a nozzle flow rate of {new_nozzle_flow} kg/s and a total burn time of {new_burn_time} seconds to optimize your fuel grain with")

fuel_flow = new_nozzle_flow / (OF + 1)
ox_flow = new_nozzle_flow * OF / (OF + 1)

print(f"Your target average fuel flow is now {fuel_flow} kg/s, and you target ox flow is {ox_flow} kg/s")

# Assumes the combustion chamber pressurizes instantly
print(f"In addition, you now have an initial ox flow rate of {find_mass_flow_MR(get_nitrous_vapor_pressure(ox_tank_initial_temperature) * 10**5 - combustion_chamber_pressure, get_liquid_nitrous_density(ox_tank_initial_temperature), get_gaseous_nitrous_density(ox_tank_initial_temperature), get_cross_sectional_area(orifices, injector_diameter), coefficient_of_discharge=0.68)}")


port_diameter = determine_optimal_starting_diameter(inner_diameter, fuel_mass, fuel_density, ox_flow, regression_rate_HTPB_nitrous, OF)
grain_length = find_required_length_fuel(port_diameter, inner_diameter, fuel_mass, fuel_density)

print(f"A port diameter of {port_diameter} meters and a length of {grain_length} meters should mean that your fuel burns up at about the same time as your ox runs out.")
print(f"That is {port_diameter * 3.28 * 12} inches and {grain_length * 3.28} feet")


# Calculate the total length of the rocket that we are looking at
tank_length = find_required_length_oxidizer(ox_mass, inner_diameter, ullage=0.1)
print(f"The ox tank has a length of {tank_length} meters, or {tank_length * 3.28} feet")


print(f"The nozzle has a total length of {nozzle_length} meters, or {nozzle_length * 3.28 * 12} inches")