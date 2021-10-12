import sys
sys.path.append(".")

from preset_object import PresetObject


"""class CustomMotor(Motor):
    # Test with https://www.grc.nasa.gov/www/k-12/rocket/ienzl.html
    # At the moment, everything is being calculated as a constant
    # I'm pretty sure it changes, but I haven't quite realized what gives.
    # Obviously it has something to do with the mass flow rate, since at some points there will be more material going through.
    # However, there doesn't appear to be any wiggle room for that in the equation

    def __init__(self, config={}):
        # TODO: Figure out how rocket motors work with gas (particularly hybrid) because I think it might affect these variables
        # pt is the total pressure in the combustion chamber, same for tt
        # I'm not sure these are the only things changing. I mean, there should be someway to simulate the fuel grain
        self.total_pressure = 10
        self.total_temperature = 100

        # Supposedly ratio should be from 1 to 60
        self.chamber_area = 0.1  # m
        self.throat_area = 0.01  # m
        self.exit_area = 0.1  # m

        # I believe that 1.33 is the best value for Nitrous, a common fuel
        # Between 1.3 and 1.6 ish
        self.specific_heat_ratio = 1.4  # often abbreviated gamma in equations
        self.gas_constant = 8.31446261815324  # per mole, probably not correct
        self.specific_heat_exponent = (
            self.specific_heat_ratio + 1) / (2 * (self.specific_heat_ratio - 1))

        super().overwrite_defaults(config)


    def mass_flow_rate(self, mach=1):
        # TODO: add mach adjustment into here
        # I believe this is for the conditions given that mass flow rate is choked at sonic conditions
        # I suspect this is where a CFD would be much more accurate
        # tis is were the problems are

        ans = self.throat_area * self.total_pressure / \
            (self.total_temperature) ** (1 / 2)

        ans *= (self.specific_heat_ratio / self.gas_constant) ** (1 / 2)

        ans *= ((self.specific_heat_ratio + 1) / 2) ** -self.specific_heat_exponent

        return ans
"""

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

class Nozzle(PresetObject):

    def __init__(self, config={}, fuel_grain=None):
        self.area_ratio = 4

        super().overwrite_defaults(config)

    def get_nozzle_coefficient(self, chamber_pressure, exit_pressure, atmospheric_pressure, isentropic_exponent):
        """
            Calculate the multiplicative effect that the nozzle has on thrust

            Notice that pressure can be in any units so long as they are all the same
        """

        isentropic_less = isentropic_exponent - 1
        isentropic_more = isentropic_exponent + 1

        # C_F = sqrt([(2*gamma^2)/(gamma-1)] * [2/(gamma+1)]^[(gamma+1)/(gamma-1)] * [1 - (P_e / P_c) ^ [(gamma-1)/gamma]])  +  (P_e - P_a)/P_c * A_e/A_t

        first_coefficient = 2 * isentropic_exponent ** 2 / isentropic_less
        second_coefficient = (2 / isentropic_more) ** (isentropic_more / isentropic_less)
        third_coefficient = 1 - (exit_pressure / chamber_pressure) ** (isentropic_less / isentropic_exponent)

        momentum_component = (first_coefficient * second_coefficient * third_coefficient) ** (1 / 2)

        pressure_difference_component = (exit_pressure - atmospheric_pressure) / chamber_pressure * self.area_ratio

        return momentum_component + pressure_difference_component






if __name__ == "__main__":
    import matplotlib.pyplot as plt
    import numpy as np

    inputs = np.linspace(20, 50)
    outputs = []
    
    for k in inputs:
        outputs.append(determine_expansion_ratio(k, 1, 1.3))

    plt.plot(inputs, outputs)
    plt.show()