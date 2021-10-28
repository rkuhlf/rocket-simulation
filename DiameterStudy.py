# ANALYZE THE EFFECTS OF DIFFERENT BODY DIAMETERS
# Assuming a constant speed profile, we can calculate the importance of coefficient of drag at each mach number.



# To be honest, this is too much of an oversimplification.
# If I would try to calculate using approximations like a constant wall thickness and the volume remaining the same, I don't see why it wouldn't be the minimum possible
# I can't really account for bending moments, which would probably be the main limiter
'''
import numpy as np

from Helpers.general import cylindrical_length


# We will assume that the rocket is a hollow cylinder with flat heads in order to calculate the length
# Based on a rocket diameter of 8 inches and a total length of 252 inches -> 12666.9016 in^3


# The lower limit for diameter is 6 inches for the parachutes
# We need to see if the lower limit for the buckling forces is higher than six inches
possible_diameters = np.array([7, 8, 9])
lengths = []

total_volume = 12667

for d in possible_diameters:
    lengths.append(cylindrical_length(total_volume, d / 2))

print(lengths)

'''



# Realistically, the only way to do this is to create a function to optimize a rocket (Monte Carlo sims in a different file)
# Then supply the diameter of the rocket as a constant and have everything else be optimized.
# This is still insanely hard, I would have to have a very good method for determining the required length.

# For this kind of thing, I am going to start by saying we can look at 6 inch, 7 inch, and 8 inch. We can look in between those later, but I should narrow it down to two first.


# Try to set better physical limitations
# Limit the ox tank to under 10 feet: hopefully that will provide a solid lower boundary
# The fuel grain should have some limitations as well. If we have a maximum flux of 500 kg/m^2-s, what does that give us

import numpy as np

from RocketParts.Motor.nitrousProperties import calculate_maximum_liquid_expansion
from RocketParts.Motor.grain import determine_optimal_starting_diameter, regression_rate_HTPB_nitrous, find_required_length as find_required_length_fuel
from RocketParts.Motor.oxTank import find_required_length as find_required_length_oxidizer


# I am designing around 70 kg of Nitrous and an HTPB single-port
# Fuel density at 920 kg/m^3 with optimal O/F at 7.1 from Chiaverini's fundamentals of Hybrid Propulsion and regression rate equation from https://classroom.google.com/u/0/c/MzgwNjcyNDIwMDg3/m/NDA0NTQyMjUyODI4/details
# We are assuming the ox starts at 68 F based on past conditions launching at White Sands (740ish psia in ox tank under vapor pressure only - https://www.desmos.com/calculator/x9m7xb6mrb)

possible_diameters = np.array([7., 8., 9.])
# inches to meters is 
possible_diameters *= 0.0254
lengths = []

oxidizer_mass = 70 # kg
oxidizer_temperature = 293.15

target_OF = 7.1

fuel_mass = oxidizer_mass / target_OF
fuel_density = 920 # kg/m^3

print(f"We are looking at a fuel mass of {fuel_mass} kg")

# In theory, the mass of the ox tank will not get any higher than 80 Farenheit while it is sitting on the pad
# Based on this, 0.1 ullage is plenty reasonable. It's hard to calculate safety factor without knowing the accuracy of the heat transfer model
# Probably around SF = 0.1 / 0.75 = 1.3ish
liquid_expansion = calculate_maximum_liquid_expansion(oxidizer_temperature, max_temperature=299.817)
print(f"The volume of the liquid will increase by at most a factor of {liquid_expansion}.")
print(f"In theory, that means you should have an ullage of at minimum {1-1/liquid_expansion}.")

print()
for d in possible_diameters:
    print(f"TESTING ROCKET OF BODY DIAMETER {d / 0.0254}")
    tank_length = find_required_length_oxidizer(oxidizer_mass, d, oxidizer_temperature, ullage=0.1)

    print("OX TANK LENGTHS")
    print(f"{tank_length} meters")
    print(f"{tank_length * 3.281} feet")

    port_diameter = determine_optimal_starting_diameter(d, fuel_mass, fuel_density, 4.8, regression_rate_HTPB_nitrous, target_OF)
    grain_length = find_required_length_fuel(port_diameter, d, fuel_mass, fuel_density)

    print("FUEL GRAIN LENGTHS")
    print(f"Lengths are for a port diameter of {port_diameter / 0.0254} inches")
    print(f"{grain_length} meters")
    print(f"{grain_length * 3.281} feet")
    print()
    


# With an ID of 8 inches, I predict an ox tank length of slightly less than 10 feet
# Any smaller IDs will require an ox tank absurdly long. Other than that, I think we just want the minimum diameter

# We really want the rocket's total length to be less than 15 feet. One, 