# ANALYZE THE EFFECTS OF DIFFERENT BODY DIAMETERS
# Show a graph of the aspect ratio over different body diameters
# We are assuming a constant prop frac, and a constant total mass

# Realistically, the only way to do this properly is to create a function to optimize a rocket (Monte Carlo sims in a different file)
# Then supply the diameter of the rocket as a constant and have everything else be optimized.
# This is still insanely hard, I would have to have a very good method for determining the required length.

# Limit the ox tank to under 10 feet: hopefully that will provide a solid lower boundary
# The fuel grain should have some limitations as well. If we have a maximum flux of 500 kg/m^2-s, what does that give us

import numpy as np
import matplotlib.pyplot as plt
import sys
sys.path.append(".")

from RocketParts.Motor.nitrousProperties import calculate_maximum_liquid_expansion
from RocketParts.Motor.grain import determine_optimal_starting_diameter, regression_rate_HTPB_nitrous, find_required_length as find_required_length_fuel
from RocketParts.Motor.oxTank import find_required_length as find_required_length_oxidizer
from RocketParts.Motor.nozzle import find_nozzle_length, find_equilibrium_throat_area
from RocketParts.Motor.injector import determine_required_thickness
from Helpers.general import get_radius, normalized


# I am designing around 70 kg of Nitrous and an HTPB single-port
# Fuel density at 920 kg/m^3 with optimal O/F at 7.1 from Chiaverini's fundamentals of Hybrid Propulsion and regression rate equation from https://classroom.google.com/u/0/c/MzgwNjcyNDIwMDg3/m/NDA0NTQyMjUyODI4/details
# We are assuming the ox starts at 68 F based on past conditions launching at White Sands (740ish psia in ox tank under vapor pressure only - https://www.desmos.com/calculator/x9m7xb6mrb)

# Inner diameters in inches
# possible_diameters = np.linspace(7, 10, 50)
possible_diameters = np.array([7.5])
# inches to meters is 0.0254
possible_diameters *= 0.0254
lengths = []

oxidizer_mass = 52.43 # kg
oxidizer_temperature = 293.15

target_OF = 7

fuel_mass = oxidizer_mass / target_OF
fuel_density = 920 # kg/m^3

print(f"We are looking at a fuel mass of {fuel_mass} kg")

# In theory, the mass of the ox tank will not get any higher than 80 Farenheit while it is sitting on the pad
# Based on this, 0.1 ullage is plenty reasonable. It's hard to calculate safety factor without knowing the accuracy of the heat transfer model
# Probably around SF = 0.1 / 0.75 = 1.3ish
liquid_expansion = calculate_maximum_liquid_expansion(oxidizer_temperature, max_temperature=299.817)
print(f"The volume of the liquid will increase by at most a factor of {liquid_expansion}.")
print(f"In theory, that means you should have an ullage of at minimum {1-1/liquid_expansion}.")


aspect_ratios = []

print()
for d in possible_diameters:
    print(f"TESTING ROCKET OF BODY DIAMETER {d / 0.0254}")
    tank_length = find_required_length_oxidizer(oxidizer_mass, d, oxidizer_temperature, ullage=0.1)

    print("OX TANK LENGTHS")
    print(f"{tank_length} meters")
    print(f"{tank_length * 3.281} feet")

    port_diameter = determine_optimal_starting_diameter(d, fuel_mass, fuel_density, 2, regression_rate_HTPB_nitrous, target_OF)
    grain_length = find_required_length_fuel(port_diameter, d, fuel_mass, fuel_density)

    print("FUEL GRAIN LENGTHS")
    print(f"Lengths are for a port diameter of {port_diameter / 0.0254} inches")
    print(f"{grain_length} meters")
    print(f"{grain_length * 3.281} feet")

    print("AUXILIARY COMBUSTION LENGTHS")
    precombustion = d / 2
    postcombustion = d
    print(f"Precombustion: {precombustion} meters")
    print(f"Precombustion: {precombustion * 3.281} feet")
    print(f"Postcombustion: {postcombustion} meters")
    print(f"Postcombustion: {postcombustion * 3.281} feet")

    print("TOTAL COMBUSTION CHAMBER LENGTH")
    print(f"{precombustion + grain_length + postcombustion} meters")

    print("NOSE CONE LENGTHS")
    nose_cone_length = d * 5
    print(f"{nose_cone_length} meters")
    print(f"{nose_cone_length * 3.281} feet")

    print("NOZZLE LENGTHS")
    # I am assuming the same CC conditions for all of these rockets, giving me epsilon = 5; obviously quite a bit rounded and will be truly optimized later
    # Also assuming C* = 1700 m/s, idk
    throat_area = find_equilibrium_throat_area(1700, 30 * 10 ** 5, 4.8)
    throat_diameter = 2 * get_radius(throat_area)
    # Scale diameters up by the sqrt of the factor that would scale up their areas
    exit_diameter = throat_diameter * 5 ** 0.5
    if exit_diameter > d:
        raise Warning("Your nozzle is wider than your rocket")

    nozzle_length = find_nozzle_length(40 / 180 * np.pi, d, throat_diameter, 15 / 180 * np.pi, exit_diameter)
    print(f"{nozzle_length} meters")
    print(f"{nozzle_length * 3.281} feet")

    print("INJECTOR LENGTHS")
    injector_length = determine_required_thickness(30 * 10 ** 5, d / 2, 0.31, 2.7579e+8)
    print(f"Injector: {injector_length} meters")
    print(f"Injector: {injector_length * 3.281 * 12} in")

    # I can't remember if fins were mounted on top of any of this, so we are going to add a foot for the fin mount
    fin_mount = 0.3 # meters
    # And we are going to add an additional foot for the payload and avionics and recovery that probably don't all fit in the nose cone
    miscellaneous_length = 0.8

    total_length = miscellaneous_length + fin_mount + injector_length + precombustion + postcombustion + nozzle_length + nose_cone_length + grain_length + tank_length
    print(f"TOTAL LENGTH: {total_length} meters")
    print(f"TOTAL LENGTH: {total_length * 3.281} feet")

    aspect_ratio = total_length / d

    print(f"ASPECT RATIO: {aspect_ratio}")

    aspect_ratios.append(aspect_ratio)

    print()

# scale it back to inches
possible_diameters *= 3.281 * 12

fig, (ax1, ax3) = plt.subplots(2, 1)
ax1.plot(possible_diameters, aspect_ratios)
ax1.set(title="Aspect Ratio and Drag Components", xlabel="Inner Diameter [in]", ylabel="Aspect Ratio")

ax2 = ax1.twinx()
# The area is frankly the thing of greatest concern that we are varying here; assumes a constant CD for proportional scale-up and a wall thickness of 0.25
potential_drags = (possible_diameters + 0.5) ** 2
ax2.plot(possible_diameters, potential_drags)
ax2.set(ylabel="Area Multiplier")


ax3.plot(possible_diameters, (np.array(aspect_ratios) - 10) * 0.5 + np.array(potential_drags) * 0.2)
ax3.set(title="Estimated difficulty", xlabel="Inner Diameter [in]", ylabel="Dimensionless Sum")

print("This is about the least rigorously mathematical way to prove anything. This is what people mean when they say that statistics is just justification for lies. This is the kind of math CEOs make when they are BSing their way through an explanation for how to make decisions. It assumes that the difficulty we will face is directly proportional to the sum of the aspect ratio and the area squared, weighted equally. Therefore we want to minimize it. Lucky for me, it happens to come out at around 7.5 to 8 ID.")

fig.tight_layout()

plt.show()

# With an ID of 8 inches, I predict an ox tank length of slightly less than 10 feet
# Any smaller IDs will require an ox tank absurdly long. Other than that, I think we just want the minimum diameter

# We really want the rocket's total length to be less than 15 feet. 