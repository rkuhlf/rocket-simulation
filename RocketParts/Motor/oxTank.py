# OXIDIZER TANK OBJECT
# Describes the ox tank - mostly just how to calculate ullage
# In addition, it provides some design equations for determining the safety of the tank given the thickness and pressure

import numpy as np
import matplotlib.pyplot as plt
import sys

sys.path.append(".")

from preset_object import PresetObject
from Helpers.general import cylindrical_volume, cylindrical_length
from RocketParts.Motor.nitrousProperties import *


#region DESIGN EQUATIONS

# TODO: create equation to maximize the volume and limit the stress given a cylindrical shape, eventually do it for a hemi-spherical shape

def find_safety_factor(pressure, radius, thickness, failure_strength):
    stress = pressure * radius / thickness
    return failure_strength / stress


def find_minimum_wall_thickness(
        pressure, radius, safety_factor, failure_strength):
    return pressure * radius * safety_factor / failure_strength

def find_nitrous_volume(mass, temperature, ullage=0):
    # This ullage adjustment is an approximation, and not a very good one
    return (mass / get_liquid_nitrous_density(temperature)) / (1 - ullage)


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

    gas_mass = gas_volume * get_gaseous_nitrous_density(temperature)
    liquid_mass = liquid_volume * get_liquid_nitrous_density(temperature)

    return (liquid_center_of_mass * liquid_mass + gas_center_of_mass * gas_mass) / (liquid_mass + gas_mass)
#endregion


#region DATA-ORIENTED EQUATIONS

def find_combined_total_heat_capacity(gaseous_mass, liquid_mass,
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
            find_heat_of_vaporization(temperature)

        total_heat_capacity = find_combined_total_heat_capacity(
            gas_mass, liquid_mass,
            find_gaseous_heat_capacity(temperature),
            find_liquid_heat_capacity(temperature))
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

def find_required_length(ox_mass, diameter, temperature, ullage=0.15):
    # This requires a teeny bit more algebra. I need to rearrange the continuity equations to get the required volume from the ullage and the mass
    pass
#endregion



class OxTank(PresetObject):
    '''
        Ox tank model of the rocket
        Stores the oxidizer in terms of the temperature, total volume, and loaded ox mass
        Has a cached ullage value, but the system is not defined by it.
        At the moment, it does not simulate the gas-only phase

        Notice that all of your inputs will have to be in SI base units, because these class uses many look ups of Nitrous properties that are in SI base units
    '''


    def __init__(self, config={}):

        # TODO: figure out the optimal value for this
        self.temperature = 30 + 273.15 # Kelvin
        self.length = 3.7 # m
        self.radius = 0.1016 # m
        self.ox_mass = 70.0 # kg


        super().overwrite_defaults(config)

        self.volume = self.get_volume()

        # Initialize the ullage in-place after declaring it
        self.ullage = 0
        self.calculate_ullage()

    def set_temperature(self, temperature):
        self.temperature = temperature
        self.calculate_ullage()

    #region Getters
    def get_volume(self):
        '''
            Calculate the volume of a cylinder with flat heads
        '''
        return cylindrical_volume(self.length, self.radius)

    def get_gas_volume(self):
        return self.get_volume() * self.ullage

    def get_liquid_volume(self):
        return self.get_volume() * (1 - self.ullage)

    def get_gas_mass(self):
        return self.get_gas_volume() * get_gaseous_nitrous_density(self.temperature)

    def get_liquid_mass(self):
        return self.get_liquid_volume() * get_liquid_nitrous_density(self.temperature)

    def get_center_of_mass(self):
        # All centers of mass are with reference to the top of the ox tank
        # The current calculations do not account for hemispherical end caps
        gas_center_of_mass = self.length * self.ullage / 2
        gas_end_distance = self.length * self.ullage
        liquid_center_of_mass = gas_end_distance + self.length * (1 - self.ullage) / 2


        return (liquid_center_of_mass * self.get_liquid_mass() + gas_center_of_mass * self.get_gas_mass()) / (self.get_liquid_mass() + self.get_gas_mass())

    def get_combined_total_heat_capacity(self):
        # kJ / K
        # Notice that we use mass. This is a scientific thing. You do not heat up a volume of something, you heat up a mass of particles.
        gaseous_specific_heat = find_gaseous_heat_capacity(self.temperature)
        liquid_specific_heat = find_liquid_heat_capacity(self.temperature)

        return self.get_gas_mass() * gaseous_specific_heat + self.get_liquid_mass() * liquid_specific_heat

    def get_pressure(self):
        '''
            Return the pressure of the system in Pa
        '''

        # it is converted from bar
        return get_nitrous_vapor_pressure(self.temperature) * 100000

    #endregion

    def calculate_ullage(self, constant_temperature=False, iterations=3, iters_so_far=0, warnings=True):
        # FIXME: Right now, there are a lot of issues in the gas only phase. It spikes up to make the thing match
        """
        Calculate indicates that it will not return a value, but there are side effects to the object - it changes the object.
        In this case it returns the ullage fraction and changes the temperature
        """

        liquid_density = get_liquid_nitrous_density(self.temperature)
        gas_density = get_gaseous_nitrous_density(self.temperature)

        already_gas_mass = self.get_gas_mass()
        # This is slightly inaccurate, but it only really triggers during the gas only phase
        already_gas_mass = min(self.ox_mass, already_gas_mass)

        liquid_mass = (self.volume - self.ox_mass / gas_density) / (1 / liquid_density - 1 / gas_density)
        liquid_mass = max(0, liquid_mass)

        gas_mass = self.ox_mass - liquid_mass


        self.ullage = (gas_mass / gas_density) / self.volume
        self.ullage = max(min(self.ullage, 1), 0)

        if not constant_temperature and iters_so_far < iterations:
            newly_evaporated_gas = gas_mass - already_gas_mass
            heat_absorbed = newly_evaporated_gas * \
                find_heat_of_vaporization(self.temperature)

            total_heat_capacity = self.get_combined_total_heat_capacity()
            temperature_change = -heat_absorbed / total_heat_capacity
            self.temperature += temperature_change

            self.calculate_ullage(iterations=iterations, iters_so_far=iters_so_far + 1)
        else:
            # I think it is bad to end on a temperature change, it is giving me some serious inaccuracies because it changes the density significantly. Therefore, I will recalculate the distributions with the new temperature
            # TODO: refactor this into a separate private equation
            liquid_density = get_liquid_nitrous_density(self.temperature)
            gas_density = get_gaseous_nitrous_density(self.temperature)

            liquid_mass = (self.volume - self.ox_mass / gas_density) / (1 / liquid_density - 1 / gas_density)
            gas_mass = self.ox_mass - liquid_mass

            self.ullage = (gas_mass / gas_density) / self.volume
            self.ullage = max(min(self.ullage, 1), 0)


        if warnings:
            if self.ullage > 1:
                raise Warning(
                    "Your ox tank is filled completely with gas. Be sure to use your own calculations for density rather than the saturated model.")
                return 1
            elif self.ullage < 0:
                raise ValueError(
                    "Your ox tank is overfull with liquid. I don't know what happens when you put more volume of liquid than can fit into a container, but there are likely going to be some extra stresses here.")


    def update_drain(self, mass_change):
        '''
            Update the mass object by draining an amount out of it, usually determined by the injector.
        '''

        self.ox_mass -= mass_change

        # TODO: If it is all gas (I'll just add a boolean, we need to do a different drain method. The vapor pressure is no longer important)
        self.calculate_ullage()


if __name__ == '__main__':
    # print(find_minimum_wall_thickness(5.688*10**6, 0.09525, 1.5, 2.551e+8)) # 6061 T6
    # print(get_length(70.61538462 / get_liquid_nitrous_density(280), 0.1905 / 2))
    
    # print(find_specific_enthalpy_of_gaseous_nitrous(273 - 0))
    ox_mass = 68.5  # kg
    # 3ish cubic feet converted to meters cubed
    volume = 4 / 35.3147
    print(find_ullage(ox_mass, volume, 298, constant_temperature=False))
    print(find_ullage(ox_mass, volume, 298, constant_temperature=True))
    

    '''
    # print(get_gaseous_nitrous_density(273.15 + 40))
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
