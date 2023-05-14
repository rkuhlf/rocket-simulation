import matplotlib.pyplot as plt
from math import pi

import numpy as np

from src.data.input.chemistry.nitrousproperties import calculate_heat, calculate_temperature, get_specific_enthalpy_of_liquid_nitrous

from src.rocketparts.motorparts.oxtank import OxTank


def check_temp():
    temperature = 273.15 + 22

    tank = OxTank(ox_mass=45, length=2.65, radius=0.1905 / 2, temperature=293.15)
    ullage = tank.ullage


    # The approximate volume of a 7" ox tank that is 8' long.
    tank_volume = tank._volume
    ox_mass = tank.ox_mass # kg
    enthalpy = get_specific_enthalpy_of_liquid_nitrous(289.7) * ox_mass

    guessed_heat = calculate_heat(tank_volume, ox_mass, 287.017, iters=30)
    print(guessed_heat)
    print(enthalpy)
    temperature = calculate_temperature(tank_volume, ox_mass, enthalpy, iters=10)
    print(temperature)

def test_calculate_heat(tank_volume, ox_mass, heats):
    for actual_heat in heats:
        # print(actual_heat)
        try:
            temp = calculate_temperature(tank_volume, ox_mass, actual_heat, iters=30)[0]
            guessed_heat = calculate_heat(tank_volume, ox_mass, temp, iters=30)
            print(f"{temp:.2f}: guess({guessed_heat:.0f}); actually({actual_heat:.0f})", flush=True)
        except ValueError as e:
            print("Skipping because it was too hot to hold in the tank.")


def plot_drain():
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



if __name__ == "__main__":
    tank_volume = 3.14 * 0.0889 ** 2 * 2.65 # m^3
    ox_mass = 45 # kg
    # This is just a scaling that shows the full heating curve usually (depending on volume).
    min_heat, max_heat = -1000 * ox_mass, -100 * ox_mass
    test_calculate_heat(tank_volume, ox_mass, np.linspace(min_heat, max_heat))