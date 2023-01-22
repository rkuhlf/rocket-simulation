# ROCKET FRAME/FUSELAGE
# Literally just a mass object
# Added some additional functions to help design with stresses and loads in mind

import numpy as np


from src.rocketparts.massObject import MassObject
from lib.decorators import diametered

@diametered
class Frame(MassObject):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.length = 3 # meters
        self.thickness = 0.003175 # meters = 1/8 inch
        self.youngs_modulus = 6.8 * 10**10
        self.poisson = 0.31 # from googling aluminum
        self.compressive_strength = 241316505 # Pascals of yield strength (https://www.giraltenterprises.com/Use_of_Aluminum.pdf)
        self.radius = 0.0762 # meters = 3 in 

        self.overwrite_defaults(**kwargs)

    @property
    def cross_sectional_area(self):
        return np.pi * self.diameter * self.thickness


    @property
    def compressive_critical_force(self):
        area_cross_section = np.pi * self.diameter * self.thickness

        return self.compressive_strength * area_cross_section
    
    # region Buckling
    # Mostly based on https://shellbuckling.com/papers/classicNASAReports/NASA-SP-8007-2020Rev2FINAL.pdf
    @property
    def critical_buckling_load_donnell(self):
        return self.critical_axial_stress_donnell * self.cross_sectional_area

    @property
    def critical_axial_stress_donnell(self):
        # Assumes self.poisson = 0.3
        return 0.605 * self.knockdown_factor * self.youngs_modulus * self.thickness / self.radius

    @property
    def buckling_line_load(self):
        return self.buckling_coefficient * np.pi ** 2 * self.flexural_wall_stiffness / self.length ** 2

    @property
    def flexural_wall_stiffness(self):
        return self.youngs_modulus * self.thickness ** 3 / (12 * (1 - self.poisson ** 2))

    @property
    def buckling_coefficient(self):
        return 4 * 3 ** (1/2) / np.pi ** 2 * self.knockdown_factor

    @property
    def knockdown_factor(self):
        phi = 1 / 16 * np.sqrt(self.radius / self.thickness)

        return 0.606 * (1 - 0.901*(1 - np.e**(-phi)))


    @property
    def buckling_critical_force(self):
        print(self.area_moment_of_inertia)
        return np.pi ** 2 * self.youngs_modulus * self.area_moment_of_inertia / self.length ** 2

    @property
    def area_moment_of_inertia(self):
        return np.pi * self.radius ** 3 * self.thickness

    # endregion


if __name__ == "__main__":
    f: Frame = Frame()
    f.length = 5.6388 # meters; 222 inches that Jase told me
    f.thickness = 0.003175 # meters; Using the 0.125 inch thickness of the ox tank because I think anything more complex would be better served by a full FEA
    f.youngs_modulus = 69 * 10**9 # 69 gigapascal young's modulus for aluminum; I think that Fiberglass
    f.radius = 0.0889
    max_expected_compressive = 10200 # Newtons; sum of the max drag, max thrust, and max weight


    print(f"The buckling critical force is {f.buckling_critical_force} N, and we probably will not get compressive forces greater then {max_expected_compressive}, giving us a safety factor of {f.buckling_critical_force/max_expected_compressive:.2f}")

    print(f"Donnell predicts the buckling critical force is {f.critical_buckling_load_donnell} N, and we probably will not get compressive forces greater then {max_expected_compressive}, giving us a safety factor of {f.critical_buckling_load_donnell/max_expected_compressive:.2f}")

    print(f"The compressive critical force is {f.compressive_critical_force} N, and we probably will not get compressive forces greater then {max_expected_compressive}, giving us a safety factor of {f.compressive_critical_force/max_expected_compressive:.2f}")