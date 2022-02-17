# Most of the equations in here are based off of https://www.researchgate.net/publication/324141385_Review_on_pressure_swirl_injector_in_liquid_rocket_engine/link/5b1bb892aca272021cf44bc6/download

import numpy as np

from Helpers.general import constant
from RocketParts.Motor.injector import Injector



class PressureSwirlInjector(Injector):
    def __init__(self, **kwargs):
        # Not sure the correct method for initialization here. I should write some documentation that explains how to do it.

        # TODO: turn this into a property based on some other inputs like the count of tangential ports
        self.tangential_port_area = 0.001 # often abbreviated with A_t
        # TODO: make this a diametered property
        self.tangential_port_diameter = 0.0003

        self.swirl_chamber_diameter = 0.002 # D_s; TODO: find a real value
        self.injector_diameter = 0.005 # often abbreivated D_0; TODO: find a real value

        self.geometry_characteristic_constant


        # 50 degrees converted to radians
        self.spray_angle_function = constant(50 * 180 / np.pi)

        super().__init__(**kwargs)

    @property
    def injector_constant(self): # often abbreviated by K
        # I think this is the congruent definition of this value
        numerator = self.tangential_port_area
        denominator = (self.swirl_chamber_diameter - self.tangential_port_diameter) * self.injector_diameter

        return numerator / denominator
    
    @property
    def spray_angle(self):
        """Returns the full angle made by the spray in radians"""

        return self.spray_angle_function(self)
    

    # TODO: equations for X
    def dimensionless_air_core_diameter(self):
        pass

    # TODO: abbreviatiated with K_v
    @property
    def velocity_correction_coefficient(self):
        pass





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
