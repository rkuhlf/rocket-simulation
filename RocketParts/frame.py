# ROCKET FRAME/FUSELAGE
# Literally just a mass object
# Added some additional functions to help design with stresses and loads in mind

import numpy as np
import sys
sys.path.append(".")

from RocketParts.massObject import MassObject

class Frame(MassObject):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.length = 3 # meters
        self.thickness = 0.003175 # meters = 1/8 inch
        self.youngs_modulus = 6.8 * 10**10
        self.compressive_strength = 241316505 # Pascals of yield strength (https://www.giraltenterprises.com/Use_of_Aluminum.pdf)
        self.radius = 0.0762 # meters = 3 in 

        self.overwrite_defaults(**kwargs)

    @property
    def diameter(self):
        return self.radius * 2
    
    @diameter.setter
    def diameter(self, d):
        self.radius = d / 2


    @property
    def compressive_critical_force(self):
        area_cross_section = np.pi * self.diameter * self.thickness

        return self.compressive_strength * area_cross_section

    @property
    def buckling_critical_force(self):
        return np.pi ** 2 * self.youngs_modulus * self.area_moment_of_inertia / self.length ** 2

    @property
    def area_moment_of_inertia(self):
        return np.pi * self.radius ** 3 * self.thickness


if __name__ == "__main__":
    f = Frame()
    max_expected_compressive = 10000 # Newtons; sum of the max drag and the max thrust

    print(f"The buckling critical force is {f.buckling_critical_force} N, and we probably will not get compressive forces greater then {max_expected_compressive}, giving us a safety factor of {f.buckling_critical_force/max_expected_compressive:.2f}")

    print(f"The critical force is {f.compressive_critical_force} N, and we probably will not get compressive forces greater then {max_expected_compressive}, giving us a safety factor of {f.compressive_critical_force/max_expected_compressive:.2f}")