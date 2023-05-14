# OXIDIZER TANK OBJECT
# Describes the ox tank - mostly just how to calculate ullage
# In addition, it provides some design equations for determining the safety of the tank given the thickness and pressure

from math import pi
from src.environment import Environment
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

        The ullage will be calculated automatically.
        """
        self.initializing = True
        super().__init__()

        # State variables. They are all properties, so setting them will automatically update the state.
        self._heat = 0 # kJ
        self._length = 3.7 # m
        self.radius = 0.1016 # m
        self._ox_mass = 70.0 # kg

        self._volume = self.get_volume()


        self.p_gas_mass = 0
        
        # Molar mass of nitrous oxide
        self.molar_mass = 44.013 / 1000 # Convert from g/mol to kg/mol.
        # Constants for Van der Waal's gas pressure
        self.a = 0.3832
        self.b = 0.04415 * 0.001


        self.environment = Environment()

        temperature = kwargs.get("temperature", 293)
        # That way it doesn't get to the override.
        del kwargs["temperature"]

        super().overwrite_defaults(**kwargs)

        self.initializing = False
        self.update_state()
        
        self.set_temperature(temperature)
        # Initialize the ullage and temperature.

        # Used as overall characteristic figures for the drain.
        self.initial_temperature = self._temperature
        self.initial_mass = self.ox_mass

    def update_state(self):
        """
        Given the state of the nitrous mass, tank volume, and internal energy, update the state variables. Notably, the temperature and ullage are set.

        Will ignore everything until initialization is complete, to avoid excessive recalculation.
        """
        if self.initializing:
            return
        
        # Recalculate all cached variables.

        self._volume = self.get_volume()
        self._temperature, self._phase = calculate_temperature(self._volume, self.ox_mass, self._heat)

        if self.phase == NitrousState.LIQUID_ONLY:
            self._liquid_mass = self.ox_mass
            self._gas_mass = 0
            self._liquid_volume = self._liquid_mass / get_liquid_nitrous_density(self._temperature, override_range=True)
            self._gas_volume = 0
            self._ullage = 1 - (self._liquid_volume / self._volume) # the empty air is basically ullage.
        elif self.phase == NitrousState.GAS_ONLY:
            self._liquid_mass = 0
            self._gas_mass = self.ox_mass
            self._liquid_volume = 0
            self._gas_volume = self._volume
            self._ullage = 1
        elif self.phase == NitrousState.EQUILIBRIUM:
            self._liquid_mass = get_liquid_mass(self._volume, self.ox_mass, self._temperature)
            self._gas_mass = self.ox_mass - self._liquid_mass
            self._liquid_volume = self._liquid_mass / get_liquid_nitrous_density(self._temperature)
            self._gas_volume = self._volume - self._liquid_volume
            self._ullage = self._gas_volume / self._volume
        elif self.phase == NitrousState.SUPERCRITICAL:
            # If any of these things get used instead of .ox_mass, something is going wrong. This will throw an error.
            self._gas_mass = None
            self._liquid_mass = None
            self._liquid_volume = None
            self._gas_volume = None
            self._ullage = 0 # Meh, I feel like this kinda represents ullage of 0.
        
    #region State Variables: Updating state variables automatically updates state.
    @property
    def length(self):
        return self._length
    
    @length.setter
    def length(self, l):
        self._length = l
        self.update_state()

    @property
    def heat(self):
        return self._heat
    
    @heat.setter
    def heat(self, h):
        self._heat = h
        self.update_state()
    
    @property
    def ox_mass(self):
        return self._ox_mass
    
    @ox_mass.setter
    def ox_mass(self, m):
        self._ox_mass = m
        self.update_state()

    #endregion

    #region Getters (many of these are read-only properties).
    def get_volume(self):
        '''
            Calculate the volume of a cylinder with flat heads
        '''
        return cylindrical_volume(self.length, self.radius)

    @property
    def temperature(self):
        return self._temperature

    @temperature.setter
    def temperature(self, t):
        raise Exception("You must call set_temperature. This is an expensive operation.")

    @property
    def ullage(self):
        return self._ullage

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
        gaseous_specific_heat = get_gaseous_specific_heat(self.temperature)
        liquid_specific_heat = get_liquid_specific_heat(self.temperature)

        return self.get_gas_mass() * gaseous_specific_heat + self.get_liquid_mass() * liquid_specific_heat

    @property
    def pressure(self):
        '''
            Return the pressure of the system in Pa
        '''

        if self.phase == NitrousState.GAS_ONLY:
            # Return the pressure predicted by the adjusted ideal gas law. (Ideal way overpredicts pressure, since it's very compressible).
            # This model is off by about 3 bar in some spots, based on the conversion from equilibrium model to this model.
            moles = self.ox_mass / self.molar_mass
            
            return van_der_waals_pressure(self._volume, moles, self.temperature, self.a, self.b)
        
        if self.phase == NitrousState.LIQUID_ONLY:
            # ρ * g * h = g * ox_mass / liquid_volume * liquid_volume / circle_area = ox_mass * g / circle_area.
            circle_area = pi * self.radius ** 2
            return  self.ox_mass / circle_area * self.environment.gravitational_acceleration
        
        if self.phase == NitrousState.EQUILIBRIUM:
            # Return the pressure of the gas above the liquid.
            # It is converted from bar.
            return get_vapor_pressure(self.temperature) * 100000
        
        if self.phase == NitrousState.SUPERCRITICAL:
            raise NotImplementedError("The idea gas law doesn't work for supercritical fluids. idk if Van der Waal's does either, but I doubt that the same coefficients would work as for not supercritical.")

    @property
    def total_mass_used(self):
        return self.initial_mass - self.ox_mass

    @property
    def phase(self):
        return self._phase

    #endregion

    def set_temperature(self, temperature: float):
        # State will be automatically updated.
        self.heat = calculate_heat(self._volume, self._ox_mass, temperature)


    def update_mass(self, mass_change: float, temperature: float, phase: NitrousState):
        '''
        mass_change is the amount going into or out of the tank (positive is into).
        temperature is the temperature of the fluid going into or out of the tank.
        
            Update the mass object by draining an amount out of it, usually determined by the injector.
        '''
        self.ox_mass += mass_change

        # I am pretty sure that we have to use the heat capacity at this point, even though we are using a discrete approximation over a changing temperature. Hopefully the heat in the tank is still zero when we finish.
        if phase == NitrousState.SUPERCRITICAL:
            specific_heat = 2 # kJ/kg/K for supercritical.
        elif (phase == NitrousState.LIQUID_ONLY or
            phase == NitrousState.EQUILIBRIUM): # In equilibrium, there's a puddle at the bottom.
            specific_heat = get_liquid_specific_heat(temperature, clamped=True)
        elif phase == NitrousState.GAS_ONLY:
            specific_heat = get_gaseous_specific_heat(temperature)

        self.heat += mass_change * specific_heat

    def drain_mass(self, drain_amount: float):
        """For a specific case of updating the mass."""
        self.update_mass(-drain_amount, self._temperature, self._phase)

