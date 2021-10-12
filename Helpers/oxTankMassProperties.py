# Generate a table with the ox tank mass over time
import numpy as np

import sys
sys.path.append(".")


from RocketParts.Motor.oxTank import find_center_of_mass, find_ullage
from RocketParts.Motor.nitrousProperties import find_gaseous_nitrous_density, find_nitrous_vapor_pressure, find_liquid_nitrous_density

# TODO: Finish implementing the injector stuff then start using another one
from RocketParts.Motor.injector import find_mass_flow_single_phase_incompressible, find_total_cross_sectional_area
import matplotlib.pyplot as plt

# Alright, actually this depends on the combustion chamber pressure and the injector; I don't even have an approximation for the combustion chamber pressure
# Right now, I think I will go ahead and assume like 33 bar = 3.3e+6 Pa

ox_mass = 68.5  # kg
# 3ish cubic feet converted to meters cubed
volume = 3 / 35.3147
# 4 feet long to 3.3 feet long
length = 4 / 3.28084
temperature = 273.15 + 22

# assumes constant temperature
ullage = find_ullage(ox_mass, volume, 273)[0]
tank_pressure = find_nitrous_vapor_pressure(temperature) * 10**5
print("TNK PRES", tank_pressure)
chamber_pressure = 3.3e+6
injector_area = find_total_cross_sectional_area(5, 0.005)
# This doesn't really matter, it is a tiny effect so long as it is much higher than the orifice total area
injector_face_area = np.pi * 0.5 **2

print(injector_area)
print(injector_face_area)

print("SPI", find_mass_flow_single_phase_incompressible(find_liquid_nitrous_density(temperature), 
                                                                            tank_pressure - chamber_pressure,
                                                                            injector_area, injector_face_area))

time = 0
time_increment = 0.1

times = []
masses = []
center_of_masses = []

while ox_mass > 0:
    old_gas_mass = volume * ullage * find_gaseous_nitrous_density(temperature)
    # m-dot_SPI is currently imaginary
    ox_mass -= time_increment * find_mass_flow_single_phase_incompressible(find_liquid_nitrous_density(temperature), 
                                                                            tank_pressure - chamber_pressure,
                                                                            injector_area, injector_face_area)

    ullage, temperature_change = find_ullage(ox_mass, volume, temperature, constant_temperature=False, already_gas_mass=old_gas_mass)
    print(temperature_change)
    times.append(time)
    masses.append(ox_mass)
    center_of_masses.append(find_center_of_mass(ullage, volume, length, temperature))

    time += time_increment



plt.plot(time, masses)
plt.plot(time, center_of_masses)

plt.show()
