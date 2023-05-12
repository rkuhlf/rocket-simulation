import numpy as np
from src.data.input.chemistry.nitrousproperties import *
from lib.general import cylindrical_volume, cylindrical_length

# TODO: create equation to maximize the volume and limit the stress given a cylindrical shape, eventually do it for a hemi-spherical shape
def find_safety_factor(pressure, radius, thickness, failure_strength):
    stress = pressure * radius / thickness
    return failure_strength / stress


def find_minimum_wall_thickness(pressure, radius, safety_factor, failure_strength):
    return pressure * radius * safety_factor / failure_strength

def get_tank_length(volume, radius, hemispherical_ends=False):
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

    gas_mass = gas_volume * get_gaseous_nitrous_density(temperature)
    liquid_mass = liquid_volume * get_liquid_nitrous_density(temperature)

    return (liquid_center_of_mass * liquid_mass + gas_center_of_mass * gas_mass) / (liquid_mass + gas_mass)


def get_combined_total_heat_capacity(gaseous_mass, liquid_mass,
                                      gaseous_specific_heat,
                                      liquid_specific_heat):
    '''
        Returns the total heat capacity of a liquid-gas system.
        Assumes thermodynamic equilibrium.
        Usually in kJ/K, but it just depends on the inputs; make sure they match
    '''
    return gaseous_mass * gaseous_specific_heat + liquid_mass * liquid_specific_heat

def find_ullage(
        ox_mass, volume, temperature, constant_temperature=True,
        already_gas_mass=0, iterations=3, iters_so_far=0,
        temperature_change_so_far=0):
    '''
        Iteratively solve for the ullage in the ox tank, accounting for change in temperature (if constant_temperature=False)
        Assumes we have a saturated solution, and will warn otherwise
    '''

    # if the temperature is changing, we need to know how much is already in gas phase
    # Because the change in phase is associated with a temperature change, we need to recalculate to adjust the densities. Since this is cyclical, we'll just loop through a couple of times and hope it converges (it should, unless the temperature is so large it causes more phase change than the initial)
    # If the temperature is constant, we will not account for the enthalpy absorbed by nitrous shifting to the gas phase
    liquid_density = get_liquid_nitrous_density(temperature)
    gas_density = get_gaseous_nitrous_density(temperature)

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

    liquid_mass = (volume - ox_mass / gas_density) / (1 / liquid_density - 1 / gas_density)

    gas_mass = ox_mass - liquid_mass

    ullage = (gas_mass / gas_density) / volume

    if not constant_temperature and iters_so_far < iterations:
        newly_evaporated_gas = gas_mass - already_gas_mass
        heat_absorbed = newly_evaporated_gas * \
            get_heat_of_vaporization(temperature)

        total_heat_capacity = get_combined_total_heat_capacity(
            gas_mass, liquid_mass,
            get_gaseous_heat_capacity(temperature),
            get_liquid_heat_capacity(temperature))
        temperature_change = -heat_absorbed / total_heat_capacity


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



if __name__ == '__main__':
    # print(find_minimum_wall_thickness(5.688*10**6, 0.09525, 1.5, 2.551e+8)) # 6061 T6
    # print(get_length(70.61538462 / get_liquid_nitrous_density(280), 0.1905 / 2))
    
    # print(find_specific_enthalpy_of_gaseous_nitrous(273 - 0))
    ox_mass = 45  # kg
    # 4ish cubic feet converted to meters cubed
    volume = 4 / 35.3147
    # print(find_ullage(ox_mass, volume, 298, constant_temperature=False))
    # print(find_ullage(ox_mass, volume, 298, constant_temperature=True))

    # Rewrite this find_required_length
    # print(find_required_volume(45, ullage=0.1))
    # print(cylindrical_length(find_required_volume(45, ullage=0.1), 0.0861695))

    # print(find_required_length(45, 0.1723136, ullage=0.1))

    # print(calculate_maximum_liquid_expansion(293.15, max_temperature=302))

    # 0.0588 m^3
    # 0.086 m is the radius (6.785 in)
    # print(cylindrical_length(0.0588, 0.0861695))

    # Check Rowan's model.
    # At 263.7 K with 6.9 kg in the tank, do I get 2.6 kg liquid as well?
    print(find_ullage(
        6.9, # kg
        0.06806, # m^3
        263.7,
        constant_temperature=True
    ))

    print(get_liquid_nitrous_density(263.7) * 0.06806 * (1 - 0.9581503090925062))
    
