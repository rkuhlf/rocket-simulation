import numpy as np
import matplotlib.pyplot as plt
import sys

sys.path.append(".")

from RocketParts.Motor.nitrousProperties import *

# atm it is mostly DOD, I'm not sure I want it like that, especially when I add it into the frame-by-frame sim


def find_combined_total_heat_capacity(gaseous_mass, liquid_mass,
                                      gaseous_specific_heat,
                                      liquid_specific_heat):
    # kJ / K
    # Notice that we use mass. This is a scientific thing. You do not heat up a volume of something, you heat up a mass of particles.
    return gaseous_mass * gaseous_specific_heat + liquid_mass * liquid_specific_heat


# This is the main one for the overall engine sim
def find_ullage(
        ox_mass, volume, temperature, constant_temperature=True,
        already_gas_mass=0, iterations=3, iters_so_far=0,
        temperature_change_so_far=0):
    # if the temperature is changing, we need to know how much is already in gas phase
    # Because the change in phase is associated with a temperature change, we need to recalculate to adjust the densities. Since this is cyclical, we'll just loop through a couple of times and hope it converges (it should, unless the temperature is so large it causes more phase change than the initial)
    # If the temperature is constant, we will not account for the enthalpy absorbed by nitrous shifting to the gas phase
    liquid_density = find_liquid_nitrous_density(temperature)
    gas_density = find_gaseous_nitrous_density(temperature)

    #region Algebraic Proof for phase mass
    # volume = gas_volume + liquid_volume
    # mass = gas_mass + liquid_mass
    # gas_mass = mass - liquid_mass

    # volume = gas_mass / gas_density + liquid_mass / liquid_density
    # Substitute; volume = (mass - liquid_mass) / gas_density + liquid_mass / liquid_density
    # Distribute and Undistribute to separate the liquid mass
    # volume = mass / gas_density - liquid_mass / gas_density + liquid_mass / liquid_density
    # volume = mass / gas_density + liquid_mass * (1 / liquid_density - 1 / gas_density)

    # liquid_mass = (volume - mass / gas_density) / (1 / liquid_density - 1 / gas_density)
    #endregion

    liquid_mass = (
        volume - ox_mass / gas_density) / (1 / liquid_density - 1 / gas_density)
    gas_mass = ox_mass - liquid_mass

    ullage = (gas_mass / gas_density) / volume

    if not constant_temperature and iters_so_far < iterations:
        newly_evaporated_gas = gas_mass - already_gas_mass
        heat_absorbed = newly_evaporated_gas * \
            find_heat_of_vaporization(temperature)
        print("absorbed", heat_absorbed) # currently imaginary
        total_heat_capacity = find_combined_total_heat_capacity(
            gas_mass, liquid_mass,
            find_gaseous_heat_capacity(temperature),
            find_liquid_heat_capacity(temperature))
        temperature_change = -heat_absorbed / total_heat_capacity
        print(temperature_change)

        return find_ullage(
            ox_mass, volume, temperature + temperature_change,
            constant_temperature=False, already_gas_mass=gas_mass,
            iterations=iterations, iters_so_far=iters_so_far + 1,
            temperature_change_so_far=temperature_change_so_far +
            temperature_change)


    if ullage > 1:
        raise Warning(
            "Your ox tank is filled completely with gas. Be sure to use your own calculations for density rather than the saturated model.")
        return 1
    elif ullage < 0:
        raise ValueError(
            "Your ox tank is overfull. I don't know what happens when you put more volume of liquid than can fit into a container, but there are likely going to be some extra stresses here.")

    return [ullage, temperature_change_so_far]


def find_safety_factor(pressure, radius, thickness, failure_strength):
    stress = pressure * radius / thickness
    return failure_strength / stress


def find_minimum_wall_thickness(
        pressure, radius, safety_factor, failure_strength):
    return pressure * radius * safety_factor / failure_strength



def find_nitrous_volume(mass, temperature, ullage=0):
    # This ullage adjustment is an approximation, and not a very good one
    return (mass / find_liquid_nitrous_density(temperature)) / (1 - ullage)

# TODO: Implement the hemispherial end adjustment (should increase required length)


def get_length(volume, radius, hemispherical_ends=False):
    if hemispherical_ends:
        end_volume = 4 / 3 * np.pi * radius ** 3
        volume -= end_volume
        straight_length = volume / (np.pi * radius ** 2)

        # The spheres provide two radiuses of length on either end
        return straight_length + radius * 2
    else:  # cylindrical ends
        return volume / (np.pi * radius ** 2)

def find_center_of_mass(ullage, volume, length, temperature):
    # All centers of mass are with reference to the top of the ox tank
    # The current calculations do not account for hemispherical end caps
    gas_center_of_mass = length * ullage / 2
    gas_end_distance = length * ullage
    liquid_center_of_mass = gas_end_distance + length * (1 - ullage) / 2

    gas_volume = ullage * volume
    liquid_volume = volume - gas_volume

    gas_mass = gas_volume * find_gaseous_nitrous_density(temperature)
    liquid_mass = liquid_volume * find_liquid_nitrous_density(temperature)

    return (liquid_center_of_mass * liquid_mass + gas_center_of_mass * gas_mass) / (liquid_mass + gas_mass)



if __name__ == '__main__':
    print(find_minimum_wall_thickness(5.688*10**6, 0.1016, 1.5, 2.7579e+8))
    '''
    # print(find_specific_enthalpy_of_gaseous_nitrous(273 - 0))
    ox_mass = 68.5  # kg
    # 3ish cubic feet converted to meters cubed
    volume = 3 / 35.3147
    print(find_ullage(ox_mass, volume, 273, constant_temperature=False))
    print(find_ullage(ox_mass, volume, 273, constant_temperature=True))
    '''

    '''
    # print(find_gaseous_nitrous_density(273.15 + 40))
    ox_mass = 68.5  # kg
    # 3ish cubic feet converted to meters cubed
    volume = 3 / 35.3147
    print(find_ullage(ox_mass, volume, 273))


    volumes = np.linspace(2.8, 10) / 35.3147
    ullages = []
    for v in volumes:
        ullages.append(find_ullage(ox_mass, v, 273))

    plt.plot(volumes, ullages)
    plt.show()

    # Conclusions:
    # It doesn't take that much of a volume increase to give your nitrous way more breathing room
    # That means that decreasing the mass by 5% will give us a more than 5% increase in ullage
    # As you increase the volume though, you get less and less ullage.
    '''


    '''
    meop = 2000  # psi
    radius = 5  # in
    thickness = 0.5  # in
    failure_strength = 40000  # psi

    print(find_safety_factor(meop, radius, thickness, failure_strength))
    print(find_minimum_wall_thickness(meop, radius, 2, failure_strength))

    # Structural stuff
    ox_mass = 68.4  # kg
    temperature = 273.15  # Kelvin

    print(find_nitrous_volume(ox_mass, temperature, ullage=0)
          * 35.3147)  # multiplication converts to ft^3
    print(find_nitrous_volume(ox_mass, temperature, ullage=0.15) * 35.3147)
    # multiplying the radius converts it to meters, multiplying the output converts m to ft
    print(
        get_length(
            find_nitrous_volume(ox_mass, temperature, ullage=0.15),
            radius * 0.0254) * 3.28084)
    '''
