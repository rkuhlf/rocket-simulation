# OXIDIZER TANK OBJECT
# Describes the ox tank - mostly just how to calculate ullage
# In addition, it provides some design equations for determining the safety of the tank given the thickness and pressure

import numpy as np
import matplotlib.pyplot as plt

from presetObject import PresetObject
from Helpers.general import cylindrical_volume, cylindrical_length
from RocketParts.Motor.nitrousProperties import *
from Helpers.decorators import diametered


#region DESIGN EQUATIONS
# TODO: create equation to maximize the volume and limit the stress given a cylindrical shape, eventually do it for a hemi-spherical shape
def find_safety_factor(pressure, radius, thickness, failure_strength):
    stress = pressure * radius / thickness
    return failure_strength / stress


def find_minimum_wall_thickness(
        pressure, radius, safety_factor, failure_strength):
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

def find_required_length(ox_mass, diameter, temperature=293.15, ullage=0.15):
    """Calculate the required length for an ox tank given a constant temperature (in kelvin) and a desired ullage (as a proportion)"""
    liquid_density = get_liquid_nitrous_density(temperature)
    gas_density = get_gaseous_nitrous_density(temperature)
    
    # ullage * V_tot = V_gas
    # (1 - ullage) * V_tot = V_liquid
    # m_tot = V_gas * p_gas + V_liquid * p_liquid
    # m_tot = ullage * V_tot * p_gas + (1 - ullage) * V_tot * p_liquid
    # m_tot = V_tot * (ullage * p_gas + (1 - ullage) * p_liquid)
    # m_tot / (ullage * p_gas + (1 - ullage) * p_liquid) = V_tot
    required_volume = ox_mass / (ullage * gas_density + (1 - ullage) * liquid_density)
    # Assumes flat circular heads
    return cylindrical_length(required_volume, diameter / 2)

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

#endregion

@diametered
class OxTank(PresetObject):
    '''
        Ox tank model of the rocket
        Stores the oxidizer in terms of the temperature, total volume, and loaded ox mass
        Has a cached ullage value, but the system is not defined by it.
        At the moment, it does not simulate the gas-only phase

        Notice that all of your inputs will have to be in SI base units, because these class uses many look ups of Nitrous properties that are in SI base units
    '''


    def __init__(self, **kwargs):
        """
        :param double length: The length of the tank; generally in meters
        :param double diameter: the inner diameter; generally in meters
        :param double ox_mass: the total amount of liquid and gaseous nitrous oxide in the tank

        The ullage will be calculated automatically (assuming a constant temperature)
        """
        self._temperature = 293.15 # Kelvin
        self.length = 3.7 # m
        self.radius = 0.1016 # m
        self.ox_mass = 70.0 # kg
        self.p_gas_mass = 0
        self.gas_only_phase = False

        super().overwrite_defaults(**kwargs)

        self.volume = self.get_volume()

        # Initialize the ullage in-place after declaring it
        self.ullage = 0
        # When somebody sets the starting, they probably actually want it to be that temperature
        self.calculate_ullage(constant_temperature=True)

    @property
    def temperature(self):
        return self._temperature

    @temperature.setter
    def temperature(self, t):
        self._temperature = t
        if hasattr(self, 'ullage'):
            self.calculate_ullage(constant_temperature=True)

    #region Getters
    def get_mass_flow_vap(self, time_increment):
        return (self.p_gas_mass - self.get_gas_mass()) / time_increment

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

    @property
    def pressure(self):
        '''
            Return the pressure of the system in Pa
        '''

        # it is converted from bar
        return get_nitrous_vapor_pressure(self.temperature) * 100000

    #endregion

    def calculate_phase_distribution(self):
        """Does algebra needed to calculate ullage; does not account for temperature change"""

        liquid_density = get_liquid_nitrous_density(self.temperature)
        gas_density = get_gaseous_nitrous_density(self.temperature)

        liquid_mass = (self.volume - self.ox_mass / gas_density) / (1 / liquid_density - 1 / gas_density)
        if liquid_mass < 0:
            self.gas_only_phase = True
            liquid_mass = 0
        else:
            self.gas_only_phase = False

        gas_mass = self.ox_mass - liquid_mass

        self.ullage = (gas_mass / gas_density) / self.volume
        self.ullage = max(min(self.ullage, 1), 0)

        return gas_mass

    def calculate_ullage(self, constant_temperature=False, iterations=3, iters_so_far=0, warnings=True):
        # FIXME: Right now, I just made gas-only constant because I don't know the math yet
        """
        Calculate indicates that it will not return a value, but there are side effects to the object - it changes the object.
        In this case it returns the ullage fraction and changes the temperature
        """
        if self.gas_only_phase:
            self.ullage = 1
            return

        already_gas_mass = self.get_gas_mass()
        if iters_so_far == 0:
            self.p_gas_mass = already_gas_mass

        gas_mass = self.calculate_phase_distribution()

        if not constant_temperature and iters_so_far < iterations:
            newly_evaporated_gas = gas_mass - already_gas_mass
            heat_absorbed = newly_evaporated_gas * \
                find_heat_of_vaporization(self.temperature)

            total_heat_capacity = self.get_combined_total_heat_capacity()
            temperature_change = -heat_absorbed / total_heat_capacity
            # Set _temperature rather than calling set_temperature, which calls calculate_ullage again
            self._temperature += temperature_change

            self.calculate_ullage(iterations=iterations, 
                                  iters_so_far=iters_so_far + 1,
                                  constant_temperature=constant_temperature)
        else:
            # I think it is bad to end on a temperature change
            # it is giving me some serious inaccuracies because it changes the density significantly.
            # Therefore, I will recalculate the distributions with the new temperature,
            # ensuring we end with the correct total mass
            self.calculate_phase_distribution()
            


        if warnings:
            if self.ullage > 1:
                raise Warning(
                    "Your ox tank is filled completely with gas. Be sure to use your own calculations for density rather than the saturated model.")
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
    ox_mass = 70  # kg
    # 4ish cubic feet converted to meters cubed
    volume = 4 / 35.3147
    print(find_ullage(ox_mass, volume, 298, constant_temperature=False))
    print(find_ullage(ox_mass, volume, 298, constant_temperature=True))
    
