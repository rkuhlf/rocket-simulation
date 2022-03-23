# NOZZLE CLASS AND DESIGN
# Script for the nozzle object and the equations that will let us CAD it

import numpy as np

from presetObject import PresetObject
from Helpers.general import get_radius



#region DESIGN EQUATIONS
def determine_expansion_ratio(combustion_chamber_pressure, atmospheric_pressure, isentropic_exponent):
    """
    Outputs the optimum expansion ratio for a converging-diverging nozzle based on a known atmospheric pressure and a combustion chamber pressure, as well as the isentropic expansion coefficient.
    Isentropic expansion coefficient is often written gamma or k, and is usually determined from a 3rd party software like CEA
    Notice that the units for pressure doesn't matter so long as they line up

    Note that there may be better expansion ratios for a given rocket
    """
    # For some reason this equation is upside down in my notes. I am rolling with it, I turn it over at the end
    # A_t / A_e = [(k+1)/2]^[1/(k-1)] * (P_e/P_c)^(1/k) * sqrt([(k+1)/(k-1)] * [1 - (P_e/P_c)^[(k-1)/k])

    # I felt like the equation was too long so I broke it up a bit
    pressure_ratio = atmospheric_pressure / combustion_chamber_pressure
    isentropic_less = isentropic_exponent - 1
    isentropic_more = isentropic_exponent + 1

    first_coefficient = (isentropic_more / 2) ** (1 / isentropic_less)
    second_coefficient = pressure_ratio ** (1 / isentropic_exponent)

    sqrt_base = isentropic_more / isentropic_less * (1 - pressure_ratio ** (isentropic_less / isentropic_exponent))

    throat_to_exit = first_coefficient * second_coefficient * sqrt_base ** (1/2)

    return 1 / throat_to_exit

def find_equilibrium_throat_area(Cstar, combustion_chamber_pressure, mass_flow):
    # c* = P_c * A_t / m-dot
    return Cstar * mass_flow / combustion_chamber_pressure

def find_equilibrium_throat_diameter(Cstar, combustion_chamber_pressure, mass_flow):
    return 2 * get_radius(find_equilibrium_throat_area(Cstar, combustion_chamber_pressure, mass_flow))

def find_nozzle_length(converging_angle, entrance_diameter, throat_diameter, diverging_angle, exit_diameter, conical_proportion=1):
    """
    Find the length of the nozzle consisting of two purely conical sections
    Converging angle is the radians north of west at the throat
    Diverging angle is the radians north of east at the throat
    """
    entrance_displacement = (entrance_diameter - throat_diameter) / 2
    exit_displacement = (exit_diameter - throat_diameter) / 2

    entrance_distance = entrance_displacement / np.tan(converging_angle)
    exit_distance = exit_displacement / np.tan(diverging_angle)

    return entrance_distance + exit_distance * conical_proportion

# endregion

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
        

    def get_nozzle_coefficient(self, chamber_pressure, atmospheric_pressure=101325):
        """
            Calculate the multiplicative effect that the nozzle has on thrust
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
    # import matplotlib.pyplot as plt
    # n = Nozzle()
    # print(n.get_nozzle_coefficient(165128))

    # n.exit_pressure = 100
    
    # for k in np.linspace(0.8, 1.4, num=6):
    #     n.isentropic_exponent = k

    #     inputs = np.linspace(0.01, 2_000_000, num=500) # Pa
    #     outputs = [n.get_nozzle_coefficient(pressure) for pressure in inputs]

    #     plt.plot(inputs, outputs, label=str(k))
    # plt.legend()
    # plt.show()



    # inputs = np.linspace(20, 50)
    # outputs = []

    # print(determine_expansion_ratio(25, 0.9, 1.2))
    # a = find_equilibrium_throat_area(1619, 25*10**5, 2.7)
    # from Helpers.general import get_radius
    # print(get_radius(a))
    
    # for k in inputs:
    #     outputs.append(determine_expansion_ratio(k, 1, 1.3))

    # plt.plot(inputs, outputs)
    # plt.show()

    pass