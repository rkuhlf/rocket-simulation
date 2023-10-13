# INJECTOR
# Class to be integrated with motor
# Also includes a few design methods for stress calculations
# Mostly has formulas for a few different two-phase flow calculations


from typing import Callable
import numpy as np
from lib.data import dataType
from lib.general import constant

from src.rocketparts.massObject import MassObject
from src.data.input.chemistry.nitrousproperties import get_vapor_pressure, get_liquid_nitrous_density, get_specific_enthalpy_of_nitrous_vapor, get_specific_enthalpy_of_liquid_nitrous, get_liquid_dynamic_viscosity


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
    """Find the number of orifices required to get a given flow rate."""
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

        self.mass_flow_function = normal_SPI


        super().overwrite_defaults(**kwargs)
    
    @property
    def liquid_density(self):
        return get_liquid_nitrous_density(self.ox_tank.temperature)

    @property
    def liquid_dynamic_viscosity(self):
        return get_liquid_dynamic_viscosity(self.ox_tank.temperature)
    
    @property
    def total_orifice_area(self):
        return get_cross_sectional_area(self.orifice_count, self.orifice_diameter)
    
    @property
    def upstream_pressure(self):
        return self.ox_tank.pressure
    
    @property
    def downstream_pressure(self):
        return self.combustion_chamber.pressure
    
    @property
    def pressure_drop(self):
        return self.upstream_pressure - self.downstream_pressure

    @property
    def mass_flow(self):
        if self.pressure_drop < 0:
            return 0
        
        return self.mass_flow_function(self)
        


#region MASS FLOW CHARACTERISTICS
def find_mass_flux_single_phase_incompressible(liquid_density: float, pressure_drop: float, coefficient_of_discharge: float = 1) -> float:
    """
    This is the not area-corrected version.
    Returns the mass flow per area. This should be multiplied by an area.
    """
    return coefficient_of_discharge * np.sqrt(2 * liquid_density * pressure_drop)

def find_mass_flow_single_phase_incompressible(liquid_density: float, pressure_drop: float, area: float, coefficient_of_discharge: float) -> float:
    """
    This is the not area-corrected version.
    Returns the mass flow per area. This should be multiplied by an area and a discharge coefficient.
    """
    return area * coefficient_of_discharge * np.sqrt(2 * liquid_density * pressure_drop)

    

def mass_flow_SPI_function(discharge_coefficient: float) -> Callable:
    # Relatively simple model that assumes your flow is entirely liquid. This will work well for most liquid rockets, but very poorly for nitrous (it overestimates it; since it is actually lower density)

    def inner(injector) -> float: # does not matter what it is passed; it will be constant
        area_ratio = injector.total_orifice_area / injector.combustion_chamber.fuel_grain.get_outer_cross_sectional_area()

        effective_area = discharge_coefficient * injector.total_orifice_area
        
        # most models actually discount the denominator for this model, since it is almost exactly equal to unity. I put it in because that is how the model is derived
        return effective_area * ((2 * injector.liquid_density * injector.pressure_drop) / (1 - area_ratio) ** 2) ** (1 / 2)

    return inner

poor_SPI = mass_flow_SPI_function(0.45)
normal_SPI = mass_flow_SPI_function(0.7)
efficient_SPI = mass_flow_SPI_function(0.95)

def mass_flow_fitted_HTPV(injector: Injector):
    # Conversion to MPa to match the graph it was fitted to
    
    return 1.2 * np.log10(injector.pressure_drop / 1e6 + 1) * injector.orifice_count

def mass_flow_fitted_square_root_HTPV(injector: Injector):
    return 0.0205 * np.sqrt(400 * injector.pressure_drop / 10e6) * injector.orifice_count


# TODO: rewrite some of these to simply take an injector as a parameter
def find_mass_flow_MR(pressure_drop, liquid_density, gas_density, total_area, coefficient_of_discharge=0.7, mixing_ratio=0.2552):
    """
    Function assumes that mixing_ratio fraction of the flow will be gaseous.
    """
    density = mixing_ratio * gas_density + (1 - mixing_ratio) * liquid_density

    return total_area * coefficient_of_discharge * (2 * density * pressure_drop) ** (1/2)


def find_mass_flow_homogenous_equilibrium(density, upstream_enthalpy, downstream_enthalpy):
    # Some implementations of this model are going to include a C_d here, but I think it is better to only have the one C_d with dyer

    # Underpredicts flow rate, assumes equilibrium of flow

    # Notice it is upstream - downstream. When you are going to a really small energy state, you will get more mass flow
    # TODO: I don't think this is very correct. I'm pretty sure this downstream enthalpy is different than just using the temperature of nitrous in the combustion chamber
    # Even if I just say that it is all gas, the gradient is still going to be mostly backwards
    return density * (2 * (upstream_enthalpy - downstream_enthalpy)) ** (1 / 2)


def find_dyer_interpolation_factor(upstream_pressure, vapor_pressure, downstream_pressure):
    # upstream pressure is in the ox tank
    # downstream is in the combustion chamber
    k = ((upstream_pressure - downstream_pressure) /
         (vapor_pressure - downstream_pressure)) ** (1 / 2)

    # This is an approximation of the t_b / t_a thing
    # idk which is better, probably best to implement both to double check


    return k

# Realistically, this is the only function that should be public. So, we'll make it take all of the necessary information

# TODO: I need to implement the critical velocity point for when the pressure downstream is very low and things are basically choked

# TODO: I have a major problem: currently the upstream pressure is calculated identically to the calculations for the vapor pressure in the injector. That means that k will always be sqrt(1); probably the best solution will be found in one of the 2 100 page papers on ox tanks
# I believe that the way I am supposed to fix this is to implement a more advanced equation of state for the ox tank. I think I will try to do the Helmholtz one. It looks like it will make the liquid a different temperature


def find_mass_flow_dyer_interpolation(
        area, discharge_coefficient, injector_fluid_temperature,
        upstream_pressure, downstream_pressure, upstream_temperature,
        downstream_temperature):

    k = find_dyer_interpolation_factor(
        upstream_pressure,
        get_vapor_pressure(injector_fluid_temperature),
        downstream_pressure)

    liquid_density = get_liquid_nitrous_density(injector_fluid_temperature)
    # FIXME: This is wrong in so many ways I don't know how to start
    upstream_enthalpy = get_specific_enthalpy_of_liquid_nitrous(
        upstream_temperature)
    downstream_enthalpy = get_specific_enthalpy_of_nitrous_vapor(
        downstream_temperature)

    # TODO: make sure that I am multiplying by area and density in the correct places
    return discharge_coefficient * area * \
        (
            k / (k + 1) * find_mass_flux_single_phase_incompressible(
                liquid_density,
                upstream_pressure - downstream_pressure)
            + 1 / (k + 1) * find_mass_flow_homogenous_equilibrium(
                liquid_density, upstream_enthalpy, downstream_enthalpy
            )
        )

#endregion




if __name__ == "__main__":
    # These are the numbers for aluminum, they do not include the effects of heat (probably important, considering aluminum melts at 1,221 F and our combustion will probably be around 3300 K)
    thickness = (determine_required_thickness(33.5775* 10**5, 0.1016, 0.31, 2757.9029*10**5)) # everything in meters
    print(thickness, "m", thickness * 39.3701, "in")
    mass = determine_injector_mass(thickness, 0.1016, 2710) # density in kg/m^3

    print(mass, "kg")

    print(determine_orifice_count_MR(2.258752177, (39.92607209 - 25) * 10**5, 854.4, 113.9, 0.005, 0.68106))
    
 