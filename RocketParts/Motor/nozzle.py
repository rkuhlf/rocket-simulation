import numpy as np
import matplotlib.pyplot as plt

import sys
sys.path.append(".")

from preset_object import PresetObject


#region NOZZLE EQUATION
from scipy.optimize import fsolve



def get_point(t, parameters):
    x0, x1, x2, y0, y1, y2 = parameters

    return (
        (1 - t)**2 * x0 + 2 * t * (1 - t) * x1 + t ** 2 * x2,
        (1 - t)**2 * y0 + 2 * t * (1 - t) * y1 + t ** 2 * y2
    )

def generate_points(parameters):
    ti = parameters[-2]
    tf = parameters[-1]
    parameters = parameters[:-2]
    
    points = []

    for t in np.linspace(ti, tf, num=100):
        points.append(np.asarray(get_point(t, parameters)))

    return np.asarray(points)

def display_nozzle(parameters):
    print(parameters)

    points = generate_points(parameters)

    points = points.transpose()

    plt.plot(points[0], points[1])
    # plt.xlim(0, 1)
    # plt.ylim(0, 1)
    plt.title("Nozzle Contour")
    plt.show()

def equations(p):
    x0, x1, x2, y0, y1, y2, ti, tf = p
    # Each of these equations should be rearranged to equal zero

    x_start = 0
    x_end = 10

    y_start = 0
    y_end = 0

    theta_opening = np.radians(20)
    theta_exit = np.radians(8)

    slope_opening = np.tan(theta_opening)
    slope_exit = np.tan(theta_exit)

    return (
        x0 * (1-ti)**2 + x1 * 2*ti * (1-ti) + x2*ti**2 - x_start,
        x0 * (1-tf)**2 + x1 * 2*tf * (1-tf) + x2*tf**2 - x_end,
        2 * (-x0 * (1-ti) + x1 * (1-2*ti) + x2 * ti) - 1,
        2 * (-x0 * (1-tf) + x1 * (1-2*tf) + x2 * tf) - 1,

        y0 * (1-ti)**2 + y1 * 2*ti * (1-ti) + y2*ti**2 - y_start,
        y0 * (1-tf)**2 + y1 * 2*tf * (1-tf) + y2*tf**2 - y_end,
        2 * (-y0 * (1-ti) + y1 * (1-2*ti) + y2 * ti) - slope_opening,
        2 * (-y0 * (1-tf) + y1 * (1-2*tf) + y2 * tf) - slope_exit,
    )

iters = 1
least_error = 1e10
best_parameters = []

# TODO: Just write an algorithm to solve it totally randomly, recording the inputs that minimize the 8 equations
for i in range(iters):
    if i % 1000 == 0:
        print(i)
    inputs = tuple(np.random.randn((8)))
    # print("INPUTS", inputs)
    # (0, 0.5, 1, 0, 1, 0.9, 0, 1)
    parameters = fsolve(equations, inputs)
    # print(parameters)

    outputs = equations(parameters)
    total_error = 0
    for output in outputs:
        total_error += abs(output)
    if total_error < least_error:
        print("Found better parameters")
        print(outputs)
        least_error = total_error
        best_parameters = parameters
    
    # print("OUTPUTS", outputs)
    # print(error)
    # print("FAILED")
    # plt.cla()

print(least_error)
print(best_parameters)
display_nozzle(best_parameters)


parameters = fsolve(equations, (0.15470709552420203, -0.03718261636217335, 0.401636215953701, 0.29084105509625857, -0.11101274275171547, 0.013110433950737174, -0.3689025055437478, -0.10153484052973501))

display_nozzle(parameters)


'''
## -- End pasted text --
(0.0, 0.0)

In [2]: x
Out[2]: 3.5000000414181831

In [3]: y
Out[3]: 1.7500000828363667
'''
#endrregion


# https://www.grc.nasa.gov/www/k-12/rocket/rktthsum.html
# There are three equations of state (plus one for exit temperature that we don't care about)
# From the equation for exit mach, we solve for exit velocity by multiplying by the speed of sound at altitude

# The goal is to solve for thrust given easily determined characteristics of the motor
# The things that are changing is the mass flow rate and the exit velocity, as well as the exit pressure (probably)
'''class CustomMotor(Motor):
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
'''


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
    """
    This one is not really meant to be used, it is just a parent class for the CEA nozzle.
    Maybe in the future it will also be the parent class for a simpler nozzle as well.
    """

    def __init__(self, config={}, fuel_grain=None):
        self.throat_diameter = 0.03048 # meters
        self.throat_area = self.get_throat_area()
        self.area_ratio = 4
        self.throat_temperature = 800 # Kelvin

        self.isentropic_exponent = 1.3
        self.exit_pressure = 100000 # Pascals. Assumes the nozzle is optimized for sea level

        self.overexpanded = False

        super().overwrite_defaults(config)

    def get_throat_area(self):
        return np.pi * self.throat_diameter ** 2

    def get_nozzle_coefficient(self, chamber_pressure, atmospheric_pressure):
        """
            Calculate the multiplicative effect that the nozzle has on thrust

            Notice that pressure can be in any units so long as they are all the same
        """
        
        # The isentropic exponent and the exit pressure is determined by CEA software and updated by our motor class

        isentropic_less = self.isentropic_exponent - 1
        isentropic_more = self.isentropic_exponent + 1

        # C_F = sqrt([(2*gamma^2)/(gamma-1)] * [2/(gamma+1)]^[(gamma+1)/(gamma-1)] * [1 - (P_e / P_c) ^ [(gamma-1)/gamma]])  +  (P_e - P_a)/P_c * A_e/A_t

        first_coefficient = 2 * self.isentropic_exponent ** 2 / isentropic_less
        second_coefficient = (2 / isentropic_more) ** (isentropic_more / isentropic_less)
        third_coefficient = 1 - (self.exit_pressure / chamber_pressure) ** (isentropic_less / self.isentropic_exponent)

        momentum_component = (first_coefficient * second_coefficient * third_coefficient) ** (1 / 2)

        pressure_difference_component = (self.exit_pressure - atmospheric_pressure) / chamber_pressure * self.area_ratio

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