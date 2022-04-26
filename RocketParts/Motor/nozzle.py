# NOZZLE CLASS AND DESIGN
# Script for the nozzle object and the equations that will let us CAD it

# TODO: Rewrite in the style of fuel grain and such. There should be some methods that use CEA only, some that are completely manual, etc.

import numpy as np

from presetObject import PresetObject
from Helpers.general import get_radius



class Nozzle(PresetObject):
    """
    This one is not really meant to be used, it is just a parent class for the CEA nozzle.
    Maybe in the future it will also be the parent class for a simpler nozzle as well.
    """

    def __init__(self, **kwargs):
        """
        :param double throat_diameter: the diameter of the smallest cross section of the nozzle (in meters)
        :param double area_ratio: The ratio between the area of the exit and the area of the throat; also called epsilon
        """

        self.throat_radius = 0.045 # 0.03048 # meters
        self.area_ratio = 4
        self.throat_temperature = 800 # Kelvin

        # Isentropic exponent is overriden by a CEA lookup in the actual motor simulation
        self.isentropic_exponent = 1.3
        # Exit pressure is overriden by a CEA lookup in the actual motor simulation
        self.exit_pressure = 100000 # Pascals. Assumes the nozzle is optimized for sea level
        self.efficiency = 1

        self.overexpanded = False

        super().overwrite_defaults(**kwargs)


    @property
    def throat_diameter(self):
        return self.throat_radius * 2

    @throat_diameter.setter
    def throat_diameter(self, value):
        self.throat_radius = value / 2


    def get_exit_mach(self, chamber_pressure, atmospheric_pressure):
        pass

    @property
    def throat_area(self):
        return np.pi * self.throat_radius ** 2

    @property
    def exit_area(self):
        return self.throat_area * self.area_ratio
        

    def get_nozzle_coefficient(self, chamber_pressure: float, atmospheric_pressure: float=101325):
        """
            Calculate the multiplicative effect that the nozzle has on thrust.
            
            Uses an exit pressure calculated from CEA

            Notice that pressure can be in any units so long as they are all the same
        """
        # FIXME: occasionally this gives a very negative value. Not sure if this ever got fixed


        if chamber_pressure / atmospheric_pressure < 2:
            # Assume it does not actually get choked
            return 1
        
        # The isentropic exponent and the exit pressure is determined by CEA software and updated by our motor class. TODO: implement exit pressure calculations myself to validate

        isentropic_less = self.isentropic_exponent - 1
        isentropic_more = self.isentropic_exponent + 1

        # C_F = sqrt([(2*gamma^2)/(gamma-1)] * [2/(gamma+1)]^[(gamma+1)/(gamma-1)] * [1 - (P_e / P_c) ^ [(gamma-1)/gamma]])  +  (P_e - P_a)/P_c * A_e/A_t

        first_coefficient = 2 * self.isentropic_exponent ** 2 / isentropic_less
        second_coefficient = (2 / isentropic_more) ** (isentropic_more / isentropic_less)
        third_coefficient = 1 - (self.exit_pressure / chamber_pressure) ** (isentropic_less / self.isentropic_exponent)

        momentum_component = self.efficiency * (first_coefficient * second_coefficient * third_coefficient) ** (1 / 2)

        pressure_difference_component = (self.exit_pressure - atmospheric_pressure) / chamber_pressure * self.area_ratio

        return momentum_component + pressure_difference_component


if __name__ == "__main__":
    

    pass