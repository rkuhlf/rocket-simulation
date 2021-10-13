import numpy as np
import sys
sys.path.append('.')

from RocketParts.Motor.nitrousProperties import find_nitrous_vapor_pressure, find_liquid_nitrous_density, find_specific_enthalpy_of_gaseous_nitrous, find_specific_enthalpy_of_liquid_nitrous


def find_required_thickness(pressure_drop, radius, poisson_ratio, failure_stress):
    numerator = 0.375 * pressure_drop * radius**3 * (1 + poisson_ratio)
    return (numerator / failure_stress) ** (1/2)

def find_injector_volume(thickness, radius):
    return np.pi * radius ** 2 * thickness

def find_injector_mass(thickness, radius, density):
    return find_injector_volume(thickness, radius) * density


#region MASS FLOW CHARACTERISTICS

def find_total_cross_sectional_area(count, diameter):
    # for use with multiple orifices
    return count * np.pi * (diameter / 2) ** 2


def find_mass_flow_single_phase_incompressible(
        liquid_density, pressure_drop, orifice_area,
        upstream_cross_sectional_area):
    # Relatively simple model that assumes your flow is entirely liquid. This will work well for most liquid rockets, but very poorly for nitrous (it overestimates it; since it is actually lower density)

    # most models actually discount the denominator for this model, since it is almost exactly equal to unity. I put it in because that is how the model is derived

    return ((2 * liquid_density * pressure_drop) /
            (1 - (orifice_area / upstream_cross_sectional_area) ** 2)) ** (1 / 2)

# TODO: figure out which point this pressure is referring to


def find_mass_flow_homogenous_equilibrium(
        pressure, upstream_enthalpy, downstream_enthalpy):
    # Some implementations of this model are going to include a C_d here, but I think it is better to only have the one C_d with dyer

    # Underpredicts flow rate, assumes equilibrium of flow

    # Notice it is upstream - downstream. When you are going to a really small energy state, you will get more mass flow
    # TODO: I don't think this is very correct. I'm pretty sure this downstream enthalpy is different than just using the temperature of nitrous in the combustion chamber
    # Even if I just say that it is all gas, the gradient is still going to be mostly backwards
    return pressure * (2 * (upstream_enthalpy - downstream_enthalpy)) ** (1 / 2)


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
        find_nitrous_vapor_pressure(injector_fluid_temperature),
        downstream_pressure)

    liquid_density = find_liquid_nitrous_density(injector_fluid_temperature)
    # FIXME: This is wrong in so many ways I don't know how to start
    upstream_enthalpy = find_specific_enthalpy_of_liquid_nitrous(
        upstream_temperature)
    downstream_enthalpy = find_specific_enthalpy_of_gaseous_nitrous(
        downstream_temperature)


    return discharge_coefficient * area * \
        (
            k / (k + 1) * find_mass_flow_single_phase_incompressible(
                liquid_density,
                upstream_pressure - downstream_pressure)
            + 1 / (k + 1) * find_mass_flow_homogenous_equilibrium(
                pressure, upstream_enthalpy, downstream_enthalpy
            )
        )

#endregion


if __name__ == "__main__":
    # These are the numbers from memory for aluminum, they do not include the effects of heat (probably important, considering aluminum melts at 1,221 F and our combustion will probably be around 3300 F)
    thickness = (find_required_thickness(450, 4, 0.31, 40000)) # everything in psi
    mass = find_injector_mass(thickness, 4, 0.0442451) # density in kg/m^3

    print(mass, "kg")

 