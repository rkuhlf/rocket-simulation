from math import pi

from src.data.input.chemistry.nitrousproperties import calculate_temperature, get_specific_enthalpy_of_liquid_nitrous

# The approximate volume of a 7" ox tank that is 8' long.
tank_volume = 3.14 * 0.0889 ** 2 * 2.4 # m^3
ox_mass = 52 # kg
# Assumes it's all liquid at whatever temperature.
enthalpy = get_specific_enthalpy_of_liquid_nitrous(293) * ox_mass

# temperature = calculate_temperature(tank_volume, ox_mass, enthalpy, iters=20)
# print(temperature)


temperature = calculate_temperature(tank_volume, ox_mass, -11346, iters=20)
print(temperature)






import matplotlib.pyplot as plt

from src.rocketparts.motorparts.oxtank import OxTank

temperature = 273.15 + 22

tank = OxTank(ox_mass=52.5, length=2.65, radius=0.1905 / 2, temperature=293.15)
ullage = tank.ullage


# The approximate volume of a 7" ox tank that is 8' long.
tank_volume = tank.volume
ox_mass = tank.ox_mass # kg
enthalpy = get_specific_enthalpy_of_liquid_nitrous(295.1) * ox_mass

temperature = calculate_temperature(tank_volume, ox_mass, enthalpy, iters=10)
print("TNK temp", tank.temperature)
print(temperature)
exit()

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
    # Should drain 5 kg per second.
    tank.update_mass(-time_increment * 5)

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
