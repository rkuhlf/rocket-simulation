import sys
sys.path.append(".")

from preset_object import PresetObject



# https://www.grc.nasa.gov/www/k-12/rocket/rktthsum.html
# There are three equations of state (plus one for exit temperature that we don't care about)
# From the equation for exit mach, we solve for exit velocity by multiplying by the speed of sound at altitude

# The goal is to solve for thrust given easily determined characteristics of the motor
# The things that are changing is the mass flow rate and the exit velocity, as well as the exit pressure (probably)
class CustomMotor(Motor):
    # TODO: check that the NASA method gives the same output as CEA
    # Test with https://www.grc.nasa.gov/www/k-12/rocket/ienzl.html
    # At the moment, everything is being calculated as a constant
    # I'm pretty sure it changes, but I haven't quite realized what gives.
    # Obviously it has something to do with the mass flow rate, since at some points there will be more material going through.
    # However, there doesn't appear to be any wiggle room for that in the equation

    def __init__(self, config={}):        

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




    def exit_mach(self):
        # The algebra is much more complicated
        # The exit mach is zero makes it undefined
        # It usually simplifies down to a polynomial
        # Unfortunately it often has multiple solutions
        # I believe that there should only ever be one solution at less than Mach one, which would be the correct result

        # Based on https://math.stackexchange.com/questions/2165814/how-to-solve-an-equation-with-a-decimal-exponent, I think there is no way to solve the polynomial rearrangement. I suspect that the best path forwards is the brute-force method. I think I'll just go ahead and use some kind of math library, but I am interested in coming up with a way to do this myself. Actually, I think binary search wouldn't be half bad, but it won't converge as quickly as a gradient descent algorithm
        # Have to rearrange equation so that x values are on one side
        # I'm not sure if polynomial form or original form is more efficient

        gamma_fraction = (self.specific_heat_ratio + 1) / 2

        gamma_fraction_extended = gamma_fraction / \
            (self.specific_heat_ratio - 1)


        target = self.exit_area / (self.throat_area * gamma_fraction ** -
                                   gamma_fraction_extended)

        # Just need to make sure it converges on the larger one
        ans = binary_solve(
            lambda
            exit_mach:
            (1 + ((self.specific_heat_ratio - 1) / 2) * exit_mach ** 2) **
            gamma_fraction_extended / exit_mach, target, 1, 10)


        return ans


    def exit_temperature(self):
        ans = 1 / ((1 + (self.specific_heat_ratio - 1) / 2 * self.exit_mach() ** 2))

        return self.total_temperature * ans

    def exit_pressure(self):
        ans = (1 + (self.specific_heat_ratio - 1) / 2 * self.exit_mach() **
               2) ** (self.specific_heat_ratio / (self.specific_heat_ratio - 1))

        return self.total_pressure * ans


    def exit_velocity(self):

        return self.exit_mach() * \
            (self.specific_heat_ratio * self.gas_constant
             * self.exit_temperature()) ** (1 / 2)

    def get_free_stream_pressure(self):
        # A function of pressure, altitude, and mach number
        # just returning a constant atm bc idk
        # I believe this is a quantity that will vary slightly with atmospheric conditions

        # This will get funky because the pressure at the back end of the rocket is sometimes pretty close to negative. However, I already account for a lot of that. I don't know what to do. Is that pressure additional to the aerodynamic forces?

        return 20

    def get_thrust(self):
        # https://www.grc.nasa.gov/WWW/K-12/rocket/rktthsum.html
        # I think that it would be best just to simulate these things in a CFD
        # They should also be relatively easy to figure out from experimental data
        self.update_total_pressure()
        self.update_total_temperature()

        # The amount of momentum being pushed out + the pressure difference
        return self.mass_flow_rate() * self.exit_velocity() + self.exit_area * (
            self.exit_pressure() - self.get_free_stream_pressure())



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

    def get_nozzle_coefficient(self, chamber_pressure, OF, atmospheric_pressure):
        """
            Calculate the multiplicative effect that the nozzle has on thrust

            Notice that pressure can be in any units so long as they are all the same
        """
        # Look up the isentropic exponent and the exit pressure from the CEA inputs we are using

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