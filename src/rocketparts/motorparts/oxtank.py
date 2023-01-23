# OXIDIZER TANK OBJECT
# Describes the ox tank - mostly just how to calculate ullage
# In addition, it provides some design equations for determining the safety of the tank given the thickness and pressure

from src.rocketparts.massObject import MassObject

from lib.general import cylindrical_volume, cylindrical_length
from src.data.input.chemistry.nitrousproperties import *
from lib.decorators import diametered


@diametered
class OxTank(MassObject):
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
        super().__init__()

        self._temperature = 293.15 # Kelvin
        self._length = 3.7 # m
        self.radius = 0.1016 # m
        self.ox_mass = 70.0 # kg
        self.p_gas_mass = 0
        self.gas_only_phase = False

        super().overwrite_defaults(**kwargs)

        self.initial_temperature = self._temperature
        self.initial_mass = self.ox_mass
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
    
    @property
    def length(self):
        return self._length
    
    @length.setter
    def length(self, l):
        self._length = l
        self.volume = self.get_volume()

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

    @property
    def oxidizer_center_of_mass(self):
        # All centers of mass are with reference to the top of the ox tank
        # The current calculations do not account for hemispherical end caps
        gas_center_of_mass = self.length * self.ullage / 2
        gas_end_distance = self.length * self.ullage
        liquid_center_of_mass = gas_end_distance + self.length * (1 - self.ullage) / 2


        return self.front + (liquid_center_of_mass * self.get_liquid_mass() + gas_center_of_mass * self.get_gas_mass()) / (self.get_liquid_mass() + self.get_gas_mass())

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
    
    def get_mass_flow_vap(self, time_increment):
        return (self.p_gas_mass - self.get_gas_mass()) / time_increment
    
    @property
    def total_mass_used(self):
        return self.initial_mass - self.ox_mass

    #endregion

    def calculate_phase_distribution(self, strict=True):
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

    def calculate_ullage(self, constant_temperature=False, iterations=3, iters_so_far=0, strict=True):
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
        elif iters_so_far == iterations: # not necessary if we say constant_temperatures
            # I think it is bad to end on a temperature change
            # it is giving me some serious inaccuracies because it changes the density significantly.
            # Therefore, I will recalculate the distributions with the new temperature,
            # ensuring we end with the correct total mass
            self.calculate_phase_distribution()
            


        if strict:
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
