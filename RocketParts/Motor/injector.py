# INJECTOR
# Class to be integrated with motor
# Also includes a few design methods for stress calculations
# Mostly has formulas for a few different two-phase flow calculations


import numpy as np
import sys
from Helpers.data import DataType
sys.path.append('.')

from RocketParts.massObject import MassObject
from RocketParts.Motor.nitrousProperties import get_nitrous_vapor_pressure, get_liquid_nitrous_density, find_specific_enthalpy_of_gaseous_nitrous, find_specific_enthalpy_of_liquid_nitrous


#region DESIGN/WEIGHT FUNCTIONS
def determine_required_thickness(pressure_drop, radius, poisson_ratio, failure_stress):
    """There is no unit for Poisson's Ratio, but your pressure drop and failure stress both must be in Pascals"""
    numerator = 0.375 * pressure_drop * radius**3 * (1 + poisson_ratio)
    return (numerator / failure_stress) ** (1/2)

def determine_injector_volume(thickness, radius):
    return np.pi * radius ** 2 * thickness

def determine_injector_mass(thickness, radius, density):
    return determine_injector_volume(thickness, radius) * density

def determine_orifice_count_SPI(mass_flow_rate, pressure_drop, density, orifice_diameter, coefficient_of_discharge=0.7):
    individual_orifice_area = np.pi * (orifice_diameter / 2) ** 2

    # m = C_d * (N * a) * sqrt(2 * rho * delta-P)
    # m / (C_d * a * sqrt(2 * rho * delta-P)) = N

    return mass_flow_rate / (coefficient_of_discharge * individual_orifice_area * (2 * density * pressure_drop) ** (1/2))

def determine_orifice_count_MR(mass_flow_rate, pressure_drop, liquid_density, gas_density, orifice_diameter, coefficient_of_discharge=0.7, mixing_ratio=0.2552):
    individual_orifice_area = np.pi * (orifice_diameter / 2) ** 2

    # m = C_d * (N * a) * sqrt(2 * rho * delta-P)
    # m / (C_d * a * sqrt(2 * rho * delta-P)) = N

    density = mixing_ratio * gas_density + (1 - mixing_ratio) * liquid_density

    return mass_flow_rate / (coefficient_of_discharge * individual_orifice_area * (2 * density * pressure_drop) ** (1/2))

def get_cross_sectional_area(count, diameter):
    return count * np.pi * (diameter / 2) ** 2

#endregion

#region MASS FLOW CHARACTERISTICS
def find_mass_flow_single_phase_incompressible(
        liquid_density, pressure_drop, orifice_area,
        upstream_cross_sectional_area):
    # Relatively simple model that assumes your flow is entirely liquid. This will work well for most liquid rockets, but very poorly for nitrous (it overestimates it; since it is actually lower density)

    # most models actually discount the denominator for this model, since it is almost exactly equal to unity. I put it in because that is how the model is derived

    return ((2 * liquid_density * pressure_drop) /
            (1 - (orifice_area / upstream_cross_sectional_area) ** 2)) ** (1 / 2)

def find_mass_flow_MR(pressure_drop, liquid_density, gas_density, total_area, coefficient_of_discharge=0.7, mixing_ratio=0.2552):
    density = mixing_ratio * gas_density + (1 - mixing_ratio) * liquid_density

    return total_area * coefficient_of_discharge * (2 * density * pressure_drop) ** (1/2)


def find_mass_flow_homogenous_equilibrium(
        density, upstream_enthalpy, downstream_enthalpy):
    # Some implementations of this model are going to include a C_d here, but I think it is better to only have the one C_d with dyer

    # Underpredicts flow rate, assumes equilibrium of flow

    # Notice it is upstream - downstream. When you are going to a really small energy state, you will get more mass flow
    # TODO: I don't think this is very correct. I'm pretty sure this downstream enthalpy is different than just using the temperature of nitrous in the combustion chamber
    # Even if I just say that it is all gas, the gradient is still going to be mostly backwards
    return density * (2 * (upstream_enthalpy - downstream_enthalpy)) ** (1 / 2)


def find_dyer_interpolation_factor(
        upstream_pressure, vapor_pressure, downstream_pressure):
    # upstream pressure is in the ox tank
    # downstream is in the combustion chamber
    k = ((upstream_pressure - downstream_pressure) /
         (vapor_pressure - downstream_pressure)) ** (1 / 2)

    # This is an approximation of the t_b / t_a thing
    # idk which is better, probably best to implement both to double check


    return k

# Realistically, this is the only function that should be public. So, we'll make it take all of the necessary information

# TODO: I need to implement the critical velocity point for when the pressure downstream is very low and things are basically choked

# TODO: I have a major problem; probably the best solution will be found in one of the 2 100 page papers on ox tanks
# The upstream pressure is calculated identically to the calculations for the vapor pressure in the injector. That means that k will always be sqrt(1)
# I believe that the way I am supposed to fix this is to implement a more advanced equation of state for the ox tank. I think I will try to do the Helmholtz one. It looks like it will make the 


def find_mass_flow_dyer_interpolation(
        area, discharge_coefficient, injector_fluid_temperature,
        upstream_pressure, downstream_pressure, upstream_temperature,
        downstream_temperature):

    k = find_dyer_interpolation_factor(
        upstream_pressure,
        get_nitrous_vapor_pressure(injector_fluid_temperature),
        downstream_pressure)

    liquid_density = get_liquid_nitrous_density(injector_fluid_temperature)
    # FIXME: This is wrong in so many ways I don't know how to start
    upstream_enthalpy = find_specific_enthalpy_of_liquid_nitrous(
        upstream_temperature)
    downstream_enthalpy = find_specific_enthalpy_of_gaseous_nitrous(
        downstream_temperature)

    # TODO: make sure that I am multiplying by area and density in the correct places
    return discharge_coefficient * area * \
        (
            k / (k + 1) * find_mass_flow_single_phase_incompressible(
                liquid_density,
                upstream_pressure - downstream_pressure)
            + 1 / (k + 1) * find_mass_flow_homogenous_equilibrium(
                liquid_density, upstream_enthalpy, downstream_enthalpy
            )
        )

#endregion

class Injector(MassObject):
    def __init__(self, **kwargs):
        """
        :param int orifice_count: The number of holes the flow is going through
        :param double orifice_diameter: the diameter of the circle through which the ox will flow (in meters)
        """

        # Since I don't know which properties I am going to be needing from the ox tank and the combustion chamber, I will just pass them in right here
        self.ox_tank = None
        self.combustion_chamber = None
        
        self.orifice_count = 3
        # Recall that we do not have total control over this. We have to order some swagelock fittings
        self.orifice_diameter = 0.005 # m

        self.mass_flow_datatype = DataType.FUNCTION_INJECTOR
        self.mass_flow = 0


        super().overwrite_defaults(**kwargs)

    @property
    def total_orifice_area(self):
        return get_cross_sectional_area(self.orifice_count, self.orifice_diameter)


    def mass_flow_function(self):
        # This is just the model for single phase incompressible
        upstream_pressure = self.ox_tank.pressure
        downstream_pressure = self.combustion_chamber.pressure
        pressure_drop = upstream_pressure - downstream_pressure

        if pressure_drop < 0:
            return 0

        density = get_liquid_nitrous_density(self.ox_tank.temperature)

        discharge_coefficient = 0.7

        area_ratio = self.total_orifice_area / self.combustion_chamber.fuel_grain.get_outer_cross_sectional_area()
        
        return discharge_coefficient * self.total_orifice_area * ((2 * density * pressure_drop) / (1 - area_ratio) ** 2) ** (1 / 2)


    def set_mass_flow_function(self, func):
        self.mass_flow_datatype = DataType.FUNCTION_INJECTOR
        self.mass_flow_function = func

    def get_mass_flow(self):
        if self.mass_flow_datatype is DataType.FUNCTION_INJECTOR:
            return self.mass_flow_function()
        



if __name__ == "__main__":
    # These are the numbers for aluminum, they do not include the effects of heat (probably important, considering aluminum melts at 1,221 F and our combustion will probably be around 3300 K)
    thickness = (determine_required_thickness(33.5775* 10**5, 0.1016, 0.31, 2757.9029*10**5)) # everything in meters
    print(thickness, "m", thickness * 39.3701, "in")
    mass = determine_injector_mass(thickness, 0.1016, 2710) # density in kg/m^3

    print(mass, "kg")

    print(determine_orifice_count_MR(2.258752177, (39.92607209 - 25) * 10**5, 854.4, 113.9, 0.005, 0.68106))
    
 