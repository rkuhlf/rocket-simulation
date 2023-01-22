# Generate a table with the ox tank mass over time.
# Useful for analyzing how the drain goes, but does not hook into any simulations of rockets.
import numpy as np


from src.rocketparts.motorparts.oxtank import OxTank
from src.rocketparts.motorparts.nitrousproperties import get_gaseous_nitrous_density, get_nitrous_vapor_pressure, get_liquid_nitrous_density

from src.rocketparts.motorparts.injector import Injector
import matplotlib.pyplot as plt

temperature = 273.15 + 22

tank = OxTank(ox_mass=52.5, length=2.65, radius=0.1905 / 2, temperature=293.15)
ullage = tank.ullage

print("TNK PRES", tank.pressure)
# Alright, actually this depends on the combustion chamber pressure and the injector; I don't even have an approximation for the combustion chamber pressure
# Right now, I think I will go ahead and assume like 33 bar = 3.3e+6 Pa
chamber_pressure = 3.3e+6

time = 0
time_increment = 0.1

times = []
masses = []
ullages = []
gas_masses = []
liquid_masses = []
center_of_masses = []

while tank.ox_mass > 0:
    tank.update_drain(time_increment * 5)

    times.append(time)
    masses.append(tank.ox_mass)
    liquid_masses.append(tank.get_liquid_mass())
    gas_masses.append(tank.get_gas_mass())
    ullages.append(tank.ullage)
    # center_of_masses.append(find_center_of_mass(ullage, volume, length, temperature))

    time += time_increment

fig, (ax1, ax2) = plt.subplots(2, 1)

ax1.plot(times, masses)
ax1.plot(times, liquid_masses)
ax1.plot(times, gas_masses)

ax2.plot(times, ullages)

plt.show()
