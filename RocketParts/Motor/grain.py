# FUEL GRAIN
# Simulate the properties of the fuel grain
# Mostly covers regression calculations

from random import choice
from typing import Callable
import numpy as np
from numpy.core.numeric import tensordot
from RocketParts.massObject import MassObject


from presetObject import PresetObject
from Helpers.general import cylindrical_volume, interpolate, constant
from Helpers.decorators import diametered

#region REGRESSION-RATE EQUATIONS
# This is just a list of pre-programmed regression-rate equations that I have come across

def exponential(leading: float, exponent: float) -> Callable:
    def inner(grain) -> float: # does not matter what it is passed; it will be constant

        return leading * grain.get_flux() ** exponent

    return inner


# https://classroom.google.com/u/0/c/MzgwNjcyNDIwMDg3/m/NDA0NTQyMjUyODI4/details
# Notice that n is even less than 0.5, which means that your burn will end fuel-rich with annular
marxman_doran_HTPB_nitrous = exponential(1.8756e-4, 0.347)
marxman_whitman_HTPB_nitrous = exponential(2.55e-5, 0.679)
marxman_waxman_paraffin_nitrous = exponential(1.55e-4, 0.5)
# https://classroom.google.com/u/2/c/MzgwNjcyNDIwMDg3/m/Mzg1OTk5OTY1Njc5/details (table 4.1)
regression_rate_ABS_nitrous_constant = constant(0.0007)
marxman_whitman_ABS_nitrous = exponential(2.623e-5, 0.664)

def whitmore_regression_model(grain):
    """Predict the regression rate of non-entraining fuels. For a low viscosity fuel like Paraffin, use the whitmore_regression_model_with_entrainment"""
    ans = grain.friction_coefficient
    ans *= grain.get_flux() / (2 * grain.density * grain.prandtl_number ** (2/3))
    ans *= grain.enthalpy_difference / grain.latent_heat

    return ans

def whitmore_regression_model_with_entrainment(grain):
    pass

def marxman_original_flat_plate_regression(grain):
    """For a given propellant system, everything except G and x is generally held constant"""
    pass



def whitmore_friction_coefficient(grain):
    # https://digitalcommons.usu.edu/cgi/viewcontent.cgi?article=1148&context=spacegrant
    # I have no idea if this is correct
    re = grain.reynolds_number
    if grain.verbose:
        if re < 10 ** 6 or re > 10 ** 7:
            print(f"Reynolds number of {re:.1e} is outside of the theoretical range of 10^6 to 10^7 for this friction model")

    return 0.074 / grain.reynolds_number ** 0.2

# https://digitalcommons.usu.edu/cgi/viewcontent.cgi?article=1148&context=spacegrant suggests 0.8
constant_prandtl_number = constant(0.8)
constant_latent_heat_HTPB = constant(1.8e6) # J/kg
constant_latent_heat_karabeyoglu_HTPB = constant(1.812e6)
constant_latent_heat_karabeyoglu_HDPE = constant(2.2e6)
constant_latent_heat_karabeyoglu_PMMA = constant(9.66e5)
constant_enthalpy_difference_karabeyoglu_PMMA_GOX = constant(22306e3)
constant_enthalpy_difference_karabeyoglu_HDPE_GOX = constant(24734e3)
constant_enthalpy_difference_karabeyoglu_HTPB_GOX = constant(25296e3)
# ! FIXME: figure out the actual value for this. At the moment paraffin is just copied from HTPB
constant_latent_heat_paraffin = constant(1.8e6)
constant_latent_heat_ABS = constant(2.3e6)

constant_nitrous_viscosity = constant(4e-5)

def no_internal_transfer_enthalpy_difference(grain):
    # It varies from about 800 to 1300 for Nitrous gas http://edge.rit.edu/edge/P07106/public/Nox.pdf
    specific_heat = 1200 # J / kg for Nitrous

    return specific_heat * (grain.flame_temperature - grain.fuel_temperature)

def bath_correction_for_helical_regression(regression, reynolds_number, port_diameter, helix_diameter):
    """The correction uses a ratio of diameters, so the units must match"""
    gniel_friction = 0.0791 * reynolds_number ** -0.25 + 0.0075 * (port_diameter / helix_diameter) ** 0.5
    blasius_friction = 0.3164 / (4 * reynolds_number ** 0.25)

    return gniel_friction / blasius_friction * regression


#endregion




#region DESIGN-ORIENTED FUNCTIONS
def find_required_length(port_diameter, outer_diameter, mass, density):
    """Determine the required length of the grain given the amount that is needed and the diameters of the grain."""
    port_radius = port_diameter / 2
    outer_radius = outer_diameter / 2
    cross_sectional_area = np.pi * outer_radius ** 2 - np.pi * port_radius ** 2
    
    required_volume = mass / density
    
    return required_volume / cross_sectional_area


def determine_optimal_starting_diameter_minimizing_weight(min_mass, outer_diameter, ox_flow, regression_func, density, target_OF, optimize_for=0.5, iterations=100, min_flux=350, max_flux=500):
    """
        Unlike determine_optimal_starting_diameter, we are not assuming a correct total O/F here
        That means that we should have enough degrees of freedom to get the minimum flux that we need
        Especially for the very low regression rate fuels (which need to be very long, even with the small inner diameter)
    """

    # Does not need to know how far the motor will regress in total, that number will take effect based on the minimum mass

    grain = Grain()
    grain.density = density
    grain.outer_diameter = outer_diameter
    grain.regression_rate_function = regression_func

    # Based on a brief survey of several papers, it looks like you do not want to go too high for flux because you get combustion instability and eventually either blow-out or flooding
    # And you do not want to go too low because eventually you get cooking
    smallest_radius = (ox_flow / (np.pi * max_flux)) ** (1/2)
    largest_radius = (ox_flow / (np.pi * min_flux)) ** (1/2)

    

    record_mass = 10 ** 10
    for initial_port_radius in np.linspace(smallest_radius, largest_radius, iterations):
        port_radius = interpolate(optimize_for, 0, 1, initial_port_radius, outer_diameter / 2)

        grain.port_radius = port_radius
        
        grain.length = grain.determine_optimal_length_OF(ox_flow, target_OF)

        fuel_mass = grain.fuel_mass
        
        if fuel_mass < record_mass and fuel_mass > min_mass:
            print(f"Found new best fuel grain, has {grain.outer_diameter} m OD, {grain.port_diameter} m ID (initially), and a length of {grain.length} meters, giving a mass of {grain.fuel_mass}, only {grain.fuel_mass - min_mass} kg heavier than specified. It starts off with a flux of {ox_flow / (np.pi * initial_port_radius ** 2)}")
            record_mass = fuel_mass
    
    if record_mass == 10 ** 10:
        raise Exception("There is no fuel grain that has the correct O/F at the specified point and at least the minimum mass requested. Your only option is to make the fuel grain OD larger, or to make the inner diameter smaller to the point that your initial flux is more than 500. Alternatively, you could use a fuel that has a lower regression rate, since that would give a more optimized O/F at a larger length, bringing it closer to the requested mass. If you believe your combustion will remain stable at a higher flux, you could raise the max_flux parameter.")

    return grain


def determine_optimal_starting_diameter(outer_diameter, target_mass, density, ox_flow, regression_func, target_OF, optimize_for=0.5, iterations=100):
    """
        Iteratively determine the starting port diameter to match a target initial O/F ratio and the correct total O/F ratio.
        Note that you must input in base SI units - your diameters must be in meters, and your flow must be in kilograms per second
        This will not give you a perfectly balanced engine - it will give you perfect combustion at the beginning, but it will probably be fuel-lean as it continues to regress.
        Read more about O/F over time at https://www.overleaf.com/read/gccgffsnzwhh

        Optimize for uses the start O/F if you choose 0, the midpoint if you choose 0.5, and the end if you choose 1
    """
    # Loop through all of the possible port diameters, starting as small as possible 
    
    # 500 kg/m^2-s = ox_flow / (pi * smallest_radius ** 2)
    # 500 * pi * r ^ 2 = ox_flow
    # r = sqrt(ox_flow / (500 * pi)
    
    # 500 is a number given by Mr. McLeod
    smallest_radius = (ox_flow / (np.pi * 500)) ** (1/2)
    
    sign_difference = 0
    for initial_port_radius in np.linspace(smallest_radius, outer_diameter / 2, iterations):
        port_radius = interpolate(optimize_for, 0, 1, initial_port_radius, outer_diameter / 2)

        port_area = np.pi * port_radius ** 2
        # We want to have the correct amount of stuff there regardless of whether the regression rates match
        length = find_required_length(port_radius * 2, outer_diameter, target_mass, density)
        burn_area = length * np.pi * 2 * port_radius

        print(regression_func(ox_flow / port_area))
        
        fuel_flow = regression_func(ox_flow / port_area) * burn_area * density
        
        current_OF = ox_flow / fuel_flow
        
        new_sign = np.sign(current_OF - target_OF)
        if sign_difference != 0 and new_sign != sign_difference:
            # We moved from having an OF that is too small to an OF that is too large (or vice-versa)
            return port_radius * 2
        
        sign_difference = new_sign
        
    
    raise Exception("The optimal starting diameter is too small for the grain. I don't really think this is physically realistic, but it is definitely mathematically possible. You can try increasing the outer diameter (I think; not well tested).")

#endregion


# TODO: integrate this with the mass object class
@diametered("port_radius", "port_diameter")
@diametered("outer_radius", "outer_diameter")
class Grain(MassObject):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.port_radius = 0.05
        self.outer_radius = 0.25
        # of the fuel
        self.mass_flow = 0
        self.density = 920 # kg / m^3
        self.length = 0.4 # m

        self.fuel_temperature = 300 # Kelvin

        self.verbose = False
        # Should usually be overriden in MotorSimulation
        self.stop_on_error = True

        self.regression_rate_function = marxman_waxman_paraffin_nitrous
        self.prandtl_number_function = constant_prandtl_number
        self.latent_heat_function = constant_latent_heat_paraffin
        self.friction_coefficient_function = whitmore_friction_coefficient
        self.oxidizer_dynamic_viscosity_function = constant_nitrous_viscosity
        self.enthalpy_difference_function = no_internal_transfer_enthalpy_difference

        super().overwrite_defaults(**kwargs)

        self.initial_mass = self.fuel_mass
        self.initial_radius = self.port_radius

        if self.verbose:
            print(f"Initialized fuel grain with {self.fuel_mass} kg of fuel. It has an {self.port_diameter} m port diameter and a {self.outer_diameter} m outer diameter.")

    #region Properties
    @property
    def fuel_mass(self):
        return self.fuel_volume * self.density

    @property
    def fuel_volume(self):
        return cylindrical_volume(self.length, self.outer_radius) - cylindrical_volume(self.length, self.port_radius)

    @property
    def regression_rate(self):
        return self.regression_rate_function(self)

    @property
    def prandtl_number(self):
        return self.prandtl_number_function(self)

    @property
    def friction_coefficient(self):
        return self.friction_coefficient_function(self)

    @property
    def latent_heat(self):
        return self.latent_heat_function(self)

    @property
    def enthalpy_difference(self):
        return self.enthalpy_difference_function(self)

    @property
    def oxidizer_dynamic_viscosity(self):
        return self.oxidizer_dynamic_viscosity_function(self)

    @property
    def reynolds_number(self):
        return self.get_flux() * self.length / self.oxidizer_dynamic_viscosity
    #endregion

    def get_port_area(self, port_diameter=None):
        if port_diameter is None:
            port_diameter = self.port_diameter
        
        return np.pi * (port_diameter / 2) ** 2

    # TODO: make a decorator for this kind of function that takes parameters as overrides (really think about it the other way; the self.__dict__ is overriding the parameters)
    def get_flux(self, ox_flow=None, port_diameter=None):
        if ox_flow is None:
            ox_flow = self.ox_flow

        if port_diameter is None:
            port_diameter = self.port_diameter

        return ox_flow / self.get_port_area(port_diameter)

    def get_burn_area(self, port_diameter=None, length=None):
        if port_diameter is None:
            port_diameter = self.port_diameter
        if length is None:
            length = self.length

        return np.pi * port_diameter * length

    def determine_optimal_length_OF(self, ox_flow, target_OF, port_diameter=None):
        if port_diameter is None:
            port_diameter = self.port_diameter
        
        ox_flux = self.get_flux(ox_flow, port_diameter)

        regression_rate = self.get_regression_rate(ox_flux)

        

        # Solve for length
        # regression_rate * pi * port_diameter * length * density = fuel_flow
        # ox_flow / fuel_flow = target_OF
        # length = ox_flow / (target_OF * regression_rate * pi * port_diameter * density)

        return ox_flow / (target_OF * regression_rate * np.pi * port_diameter * self.density)




    def get_outer_cross_sectional_area(self):
        return np.pi * self.outer_radius ** 2

    def get_volume_flow(self):
        return self.mass_flow / self.density

    def update_regression(self, ox_flow, time_increment, flame_temperature=2000):
        self.ox_flow = ox_flow
        self.flame_temperature = flame_temperature

        ox_flux = self.get_flux()

        # Give a warning if ox flux is too big: might blow fire out, might cause combustion instability
        if ox_flux > 700: # assumes kg/m^2
            raise Warning("McLeod told us not to go past 500 kg/m^2-s. He warned of blowing the flame out, but I have also seen some combustion instability stuff.")

        if self.port_radius > self.outer_radius:
            raise Warning("You have burned through the entire fuel grain")

        # Right now this is space-averaged. TODO: It might be kind of fun to do a not space-averaged thing, just simulating about 25 separate points along the grain
        burn_area = self.get_burn_area()
        regression_rate = self.regression_rate
        self.mass_flow = regression_rate * burn_area * self.density

        regressed_distance = regression_rate * time_increment
        self.port_radius += regressed_distance


    #region Evaluations
    def approximate_average_regression_rate(self, burn_time):
        # Use the average diameter method
        return (self.port_radius - self.initial_radius) / burn_time

    @property
    def total_mass_used(self):
        return self.initial_mass - self.fuel_mass

    def __repr__(self) -> str:
        ans = f"Fuel grain of density {self.density} kg/m^3 with port diameter {self.port_diameter} m and outer diameter {self.outer_diameter} m, giving mass of {self.fuel_mass:.2f} kg. "

        if hasattr(self, "ox_flow"):
            ans += f"Current regression rate is {self.regression_rate:.6f} m/s with a flux of {self.get_flux():.1f} kg/m^2-s. "
        else:
            ans += "Flow has not started yet. "

        return ans

    #endregion

class HTPBGrain(Grain):
    """Exact same as Grain, just uses different defaults. Be aware that you must also override the motor data_path to correct CEA data"""
    # This would probably be better implemented with the prototype design pattern, but I do not know how to use that

    def __init__(self, **kwargs):
        super().__init__()

        self.density = 930 # kg/m^3; from google. I have also seen 920
        self.regression_rate_function = marxman_doran_HTPB_nitrous
        self.latent_heat_function = constant_latent_heat_karabeyoglu_HTPB

        self.overwrite_defaults(**kwargs)

class ABSGrain(Grain):
    """Exact same as Grain, just uses different defaults. Be aware that you must also override the motor data_path to correct CEA data"""
    # This would probably be better implemented with the prototype design pattern, but I do not know how to use that

    def __init__(self, **kwargs):
        super().__init__()

        self.density = 1000 # kg/m^3; from google. I have also seen 975
        self.regression_rate_function = whitmore_regression_model
        self.latent_heat_function = constant_latent_heat_ABS

        self.overwrite_defaults(**kwargs)

    def randomize_regression_algorithm(self):
        self.regression_rate_function = choice([whitmore_regression_model, regression_rate_ABS_nitrous_constant, marxman_whitman_ABS_nitrous])


if __name__ == "__main__":
    g = HTPBGrain()
    g.length = 0.86
    g.port_diameter = 0.0254 # = 1 in
    g.regression_rate_function = whitmore_regression_model


    print(g)
    area = np.pi * g.port_radius ** 2
    g.update_regression(350 * area, 0, flame_temperature=3000)

    print(g)


    # best_ID = determine_optimal_starting_diameter(0.2032, 15, 920, 4.8, marxman_doran_HTPB_nitrous, 6) 
    # print(best_ID)

    # Using an ID of 5 cm, an OD of 5.75 inches - 1 inches (0.5 inches on both sides in case we have extra regression)
    # print(find_required_length(0.025, 0.146, 8.48381877, 1000))

    # print(determine_optimal_starting_diameter_minimizing_weight(8.48, 0.146, 2.7, regression_rate_ABS_nitrous_constant, 975, 6.18, optimize_for=0.5))
    # Give an extra half inch on each side
    # print(determine_optimal_starting_diameter_minimizing_weight(8.48, 0.120, 2.7, regression_rate_ABS_nitrous_constant, 975, 6.18, optimize_for=0.5, max_flux=1000)) # will be more than 650 kg/m2s; there just is not enough space to have the proper O/F through the whole burn
    # Give an extra 10 centimeters on either side (1.5 SF of r-dot)
    # print(determine_optimal_starting_diameter_minimizing_weight(8.48, 0.126, 2.7, regression_rate_ABS_nitrous_constant, 1000, 6.18, optimize_for=0.5, max_flux=1000)) # will be more than 650 kg/m2s; there just is not enough space to have the proper O/F through the whole burn
    # Found new best fuel grain, has 0.146 m OD, 0.1213269691560687 m ID (initially), and a length of 1.6794435545384543 meters, giving a mass of 8.482525721614701, only 0.002525721614700771 kg heavier than specified


    # print(determine_optimal_starting_diameter_minimizing_weight(12.48, 0.08255 * 2, 2.1, regression_rate_ABS_nitrous_constant, 1060, 6.18, optimize_for=0.5, max_flux=1000))


    # test_grain = Grain(density=1060, length=1.147, port_diameter=0.127, outer_radius=0.08255)
    # print(test_grain.fuel_volume)
    # print(test_grain.fuel_mass)

    pass
