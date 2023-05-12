# OXIDIZER TANK OBJECT
# Describes the ox tank - mostly just how to calculate ullage
# In addition, it provides some design equations for determining the safety of the tank given the thickness and pressure

from src.rocketparts.massObject import MassObject

from lib.general import cylindrical_volume, cylindrical_length
from src.data.input.chemistry.nitrousproperties import *
from lib.chemistry import van_der_waals_pressure
from lib.decorators import diametered

# General rule is to clamp the temperature for nitrous lookups if you are gas only, because then it might be really cold but we still want it to work.
# As a state variable, I am going to use the amount of heat in the nitrous.

@diametered
class OxTank(MassObject):
    '''
        Ox tank model for nitrous oxide.
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
        self.liquid_only_phase = False
        # Molar mass of nitrous oxide
        self.molar_mass = 44.013 / 1000 # Convert from g/mol to kg/mol.
        self.a = 0.3832
        self.b = 0.04415 * 0.001

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
        if isinstance(self._temperature, complex):
            self._temperature = self._temperature.real
        return self._temperature

    @temperature.setter
    def temperature(self, t: float):
        if isinstance(t, complex):
            t = t.real
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
        if self.gas_only_phase:
            return 0
        
        # This one actually works backwards, using the mass as dependent.
        if self.liquid_only_phase:
            return self.get_liquid_mass() / get_liquid_nitrous_density(self.temperature)
        
        return self.get_volume() * (1 - self.ullage)

    def get_gas_mass(self):
        if self.gas_only_phase:
            return self.ox_mass
        
        if self.liquid_only_phase:
            return 0
        
        return self.get_gas_volume() * get_gaseous_nitrous_density(self.temperature)

    def get_liquid_mass(self):
        if self.gas_only_phase:
            return 0
        
        if self.liquid_only_phase:
            return self.ox_mass

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
        """
        The ullage must be correctly set for this to work right.
        """
        # Returns the number of kJ required to heat up the system 1 K (kJ/K)
        # Notice that we use mass. This is a scientific thing. You do not heat up a volume of something, you heat up a mass of particles.
        gaseous_specific_heat = get_gaseous_heat_capacity(self.temperature)
        liquid_specific_heat = get_liquid_heat_capacity(self.temperature)

        return self.get_gas_mass() * gaseous_specific_heat + self.get_liquid_mass() * liquid_specific_heat

    @property
    def pressure(self):
        '''
            Return the pressure of the system in Pa
        '''

        if self.gas_only_phase:
            # Return the pressure predicted by the adjusted ideal gas law. (Ideal way overpredicts pressure).
            # This model is off by about 3 bar in some spots.
            moles = self.ox_mass / self.molar_mass
            
            return van_der_waals_pressure(self.get_volume(), moles, self.temperature, self.a, self.b)
        
        if self.liquid_only_phase:
            return 0
        
        # Return the pressure of the gas above the liquid.
        # It is converted from bar.
        return get_vapor_pressure(self.temperature) * 100000
    
    def get_mass_flow_vap(self, time_increment):
        return (self.p_gas_mass - self.get_gas_mass()) / time_increment
    
    @property
    def total_mass_used(self):
        return self.initial_mass - self.ox_mass

    #endregion

    def calculate_phase_distribution(self, strict=True):
        """Does algebra needed to calculate ullage; does not account for temperature change"""

        liquid_density = get_liquid_nitrous_density(self.temperature, clamped=self.gas_only_phase)
        gas_density = get_gaseous_nitrous_density(self.temperature, clamped=self.gas_only_phase)

        
        # Nitrous is now liquid only:
        # The less than is so that it doesn't conflict when I purposefully condense up to the minimum temperature.
        if self.temperature < minimum_temperature:
            liquid_mass = self.ox_mass
            self.liquid_only_phase = True
            self.gas_only_phase = False

            return 0
        else:
            self.liquid_only_phase = False

            # We only need to calculate it if it isn't liquid only.
            liquid_mass = (self.volume - self.ox_mass / gas_density) / (1 / liquid_density - 1 / gas_density)
            

        if liquid_mass < 0:
            self.gas_only_phase = True
            self.liquid_only_phase = False
            liquid_mass = 0
            self.ullage = 1
            # All of the oxidizer is gas
            return self.ox_mass

        # If there is liquid in the tank.
        self.gas_only_phase = False
        gas_mass = self.ox_mass - liquid_mass

        self.ullage = (gas_mass / gas_density) / self.volume
        self.ullage = max(min(self.ullage, 1), 0)

        return gas_mass

    def calculate_ullage(self, constant_temperature=False, iterations=3, iters_so_far=0, strict=True, already_gas_mass=None):
        """
        Calculate indicates that it will not return a value, but there are side effects to the object - it changes the object.
        In this case it returns the ullage fraction and changes the temperature
        """

        if already_gas_mass is None:
            already_gas_mass = self.get_gas_mass()
        
        # This is here just so that the gas_mass is stored for the logger.
        if iters_so_far == 0:
            self.p_gas_mass = already_gas_mass


        # Recalculate the gas distribution, then check if it is gas only.
        gas_mass = self.calculate_phase_distribution()

        if not constant_temperature and self.liquid_only_phase and iters_so_far < iterations:
            # We need to condense enough nitrous to reach the minimum.
            required_temp_change = minimum_temperature - self.temperature
            heat_required = required_temp_change * self.get_combined_total_heat_capacity()
            required_condensation = heat_required / get_heat_of_vaporization(self.temperature, clamped=self.gas_only_phase)

            # There is not enough to bring it up to temp, so it will all turn to liquid.
            if required_condensation > self.ox_mass:
                pass
            else:
                self.temperature = minimum_temperature
                self.liquid_only_phase = False
                
        elif not constant_temperature and iters_so_far < iterations:
            newly_evaporated_gas = gas_mass - already_gas_mass
            heat_absorbed = newly_evaporated_gas *                get_heat_of_vaporization(self.temperature, clamped=self.gas_only_phase)

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


    def update_mass(self, mass_change, temperature=None):
        '''
            Update the mass object by draining an amount out of it, usually determined by the injector.
        '''

        if mass_change < 0:
            # We don't have to adjust the temperature, since we know we are losing ox that is the same temp as what is already in the tank.
            self.ox_mass += mass_change

            self.calculate_ullage()
        if mass_change > 0:
            if temperature is None:
                raise ValueError("Filling tank requires the temperature of the mass being added. Value passed was None.")
            
            # Update the temperature of the tank as a whole.
            # Basically a weighted average of the temperatures, using heat capacity as weight.
            original_energy = self.get_combined_total_heat_capacity() * self.temperature
            additional_energy = get_liquid_heat_capacity(temperature) * mass_change * temperature
            total_energy = additional_energy + original_energy

            # Try these two commands in opposite order and see if there is a big difference.
            # The main thing is that the heat capacity will be slightly different depending on when you calculate it.
            # It would be best to store a total Q of the system, in which case I would just have to update that. Oh well.
            # Setting the temperature normally would force it to recalculate the ullage, but it keeps the temperature constant. That means that if a lot of this liquid is evaporating, it will not lose the proper amount of energy.
            self._temperature = total_energy / (self.get_combined_total_heat_capacity() + get_liquid_heat_capacity(temperature) * mass_change)
            # I am pretty sure that this number ends up too high at some point, and it just thinks that a ton of stuff unevaporated so the temperature goes way up.
            already_gas_mass = self.get_gas_mass()
            self.ox_mass += mass_change

            # Allow it to recalculate how much should be in each phase afterwards.
            self.calculate_ullage(already_gas_mass=already_gas_mass)
        
