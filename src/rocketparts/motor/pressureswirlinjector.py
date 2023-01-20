# Most of the equations in here are based off of https://www.researchgate.net/publication/324141385_Review_on_pressure_swirl_injector_in_liquid_rocket_engine/link/5b1bb892aca272021cf44bc6/download
# It turns out that most of this stuff is kind of irrelevant because this isn't how our PSV injectors work


import numpy as np

from helpers.general import constant, create_multiplication_modifier
from rocketparts.motor.injector import Injector
from rocketparts.motor.oxtank import OxTank


# TODO: make graphs of all of these over different pressures, debug the reason for numbers being different


class PressureSwirlInjector(Injector):
    def __init__(self, **kwargs):
        # Not sure the correct method for initialization here. I should write some documentation that explains how to do it.

        # TODO: turn this into a property based on some other inputs like the count of tangential ports
        self.tangential_port_area = 0.001 # often abbreviated with A_t
        # TODO: make this a diametered property
        self.tangential_port_diameter = 0.0003

        self.swirl_chamber_diameter = 0.002 # D_s; TODO: find a real value
        self.injector_diameter = 0.005 # often abbreivated D_0; TODO: find a real value


        # 50 degrees converted to radians
        self.spray_angle_function = constant(50 * 180 / np.pi)

        super().__init__(**kwargs)

    @property
    def injector_constant(self): # often abbreviated by K
        """Based primarily on the dimensions of the tangential ports and the swirl chamber"""
        # I think this is the congruent definition of this value
        numerator = self.tangential_port_area
        denominator = (self.swirl_chamber_diameter - self.tangential_port_diameter) * self.injector_diameter

        return numerator / denominator
    
    @property
    def spray_angle(self):
        """Returns the full angle made by the spray in radians"""

        return self.spray_angle_function(self)
    
    @property
    def geometry_characteristic_constant(self): # Usually abbreviated by A
        numerator = (1 - self.filling_coefficient) * np.sqrt(2)
        denominator = self.filling_coefficient * np.sqrt(self.filling_coefficient)
    
    @property
    def filling_coefficient(self): # Abbreviated by phi
        return 1 - self.dimensionless_air_core_area
    

    # TODO: equations for X. It also says that X is the dimensionless air core area
    def dimensionless_air_core_diameter(self):
        pass

    # TODO: abbreviatiated with K_v
    @property
    def velocity_correction_coefficient(self):
        pass


#region Regression Adjustments
# Since the fluid is being injected slightly differently, it will regress slightly faster or slower. The current research makes it hard to discern.

bouziane_PSW_adjustment = create_multiplication_modifier(0.8)
null_PSW_adjustment = create_multiplication_modifier(1)
bertoldi_PSW_adjustment = create_multiplication_modifier(1.2)

PSW_modifiers = [bouziane_PSW_adjustment, null_PSW_adjustment, bertoldi_PSW_adjustment]

#endregion


#region Spray Angle
def spray_angle_lefebvre(injector: PressureSwirlInjector):
    """Requires K_v, X"""
    K_v = injector.K_v
    X = injector.X

    coefficient_of_discharge = K_v * np.sqrt((1 - X) ** 3 / (1 + X))

    return np.arccos(coefficient_of_discharge / (K_v * (1 - X)))


def spray_angle_lefebvre_2(injector: PressureSwirlInjector):
    X = injector.X

    fraction = (1 - X) / (1 + X)

    return np.arccos(np.sqrt(fraction))

def spray_angle_rizk(injector: PressureSwirlInjector):
    K = injector.K
    X = injector.X
    D_s = injector.swirl_chamber_diameter


    K_v = 0.00367 * K ** 0.29 * (injector.pressure_drop * injector.liquid_density / injector.liquid_dynamic_viscosity) ** 0.2

    C_d = 0.35 * K ** 0.5 * (D_s / D_o) ** 0.25

    return C_d / (K_v * (1 - X))

def spray_angle_liu(injector: PressureSwirlInjector):
    # This is an empirical equation that requires the port_angle in degrees
    A = injector.geometry_characteristic_coefficient
    L_0 = injector.orifice_length
    D_s = injector.swirl_chamber_diameter
    D_0 = injector.injector_diameter
    
    ratio = 0.302 * (1 + np.tan(injector.tangential_port_angle * 180 / np.pi)) ** 0.414 * (1/A) ** 0.35 * (L_0 / D_0) ** 0.043 * (D_s / D_0) ** 0.026 + 0.612
    
    return np.arccos(ratio)
                        
def spray_angle_giffen(injector: PressureSwirlInjector):
    X = injector.dimensionless_area_ratio # Might be diameter ratio
    K = injector.injector_constant
    
    numerator = (np.pi / 2) * (1 - X) ** 1.5
    denominator = K * (1 + np.sqrt(X)) * np.sqrt(1 + X)
    
    return np.arcsin(numerator / denominator)

def spray_angle_giffen_santangelo_variation(injector: PressureSwirlInjector):
#   # I am not 100% sure that this is actually the correct source for this equation
    X = injector.dimensionless_something
    
    C_d = np.sqrt((1 - X) ** 3 / (1 + X))
    # It is very weird that they define K like this. I don't think that is how it is theoretically defined
    K = np.sqrt(np.pi ** 2 * (1 - X) ** 3 / (32 * X** 2))
    
    denominator = 2 * K * (1 + np.sqrt(X))
        
    return np.arcsin(np.pi * C_d / denominator)


def spray_angle_xue(injector: PressureSwirlInjector):
    pass

def spray_angle_giffen_2(injector: PressureSwirlInjector):
    pass

def spray_angle_orzechowski(injector: PressureSwirlInjector):
    pass

def spray_angle_chinn(injector: PressureSwirlInjector):
    pass

def spray_angle_fu(injector: PressureSwirlInjector):
    A = injector.geometry_characteristic_constant
    Re = injector.tangential_inlet_reynolds # Re_t, technically
    return np.arctan(0.033 * A ** 0.338 * Re ** 0.249)

def spray_angle_inamura(injector: PressureSwirlInjector):
    # Solves for a different kind of spray angle
    pass

def spray_angle_lefebvre_3(injector: PressureSwirlInjector):
    # This is a nice equation because it does not require the dimensionless air core (X)
    K = injector.injector_constant
    A_t = injector.tangential_port_diameter
    D_s = injector.diameter_swirl_port
    D_0 = injector.injector_diameter

    # The A_t / D_s / D_0 term comes up a lot
    first_term = A_t / D_s / D_0
    second_term = 30 * 10**5 * injector.injector_diameter ** 2 * injector.liquid_density / injector.liquid_dynamic_viscosity ** 2
    
    # The division by two is because the paper fitted it to the half-angle
    return 6 * first_term ** -0.15 * second_term ** 0.11 / 2
    

def spray_angle_khil(injector: PressureSwirlInjector):
    # Very slight adjustment of the lefebvre 3 equation to use the injector constant instead of the dimensions
    K = injector.injector_constant
    
    second_term = injector.pressure_drop * injector.injector_diameter ** 2 * injector.liquid_density / injector.liquid_dynamic_viscosity ** 2
    
    # The division by two is because the paper fitted it to the half-angle
    return 6 * K ** -0.15 * second_term ** 0.11 / 2

def spray_angle_benjamin(injector: PressureSwirlInjector):
    # Fitted to the same parameters as Lefebvre 3, but it has significantly different coefficients
    A_t = injector.tangential_port_area
    D_s = injector.swirl_chamber_diameter
    D_0 = injector.injector_diameter
    
    first_term = (A_t / D_s / D_0) ** -0.237
    second_term = (30 * 10**5 * D_0 ** 2 * injector.liquid_density / injector.liquid_dynamic_viscosity ** 2) ** 0.067
    
    # The division by two is because the paper fitted it to the half-angle
    return 9.75 * first_term * second_term / 2

#endregion



if __name__ == "__main__":
    ox = OxTank()
    inj = PressureSwirlInjector(ox_tank=ox)
    inj.spray_angle_function = spray_angle_lefebvre_3
    # inj.spray_angle_function = spray_angle_benjamin
    
    print(inj.spray_angle)

