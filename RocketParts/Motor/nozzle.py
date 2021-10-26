# NOZZLE CLASS AND DESIGN
# Script for the nozzle object and the equations that will let us CAD it
# This may be too many responsibilities for one file

import numpy as np
import matplotlib.pyplot as plt


import sys
sys.path.append(".")

from preset_object import PresetObject
from Helpers.general import linear_intersection, interpolate, interpolate_point, transpose_tuple



def calculate_nozzle_coordinates_bezier(initial_point, initial_angle, final_point, final_angle, divisions=100):
    """
        Return a series of x, y coordinate pairs that make up a quadratic Bezier.
        Supposedly, this curve is an approximation for the Method of Characteristics.
        Angles should be in radians
    """

    initial_slope = np.tan(initial_angle)
    final_slope = np.tan(final_angle)
    
    intersection_point = linear_intersection(initial_point, initial_slope, final_point, final_slope)

    points = []

    for i in range(divisions):
        start_point = interpolate_point(i, 0, divisions - 1, initial_point, intersection_point)
        end_point = interpolate_point(i, 0, divisions - 1, intersection_point, final_point)

        points.append(interpolate_point(i, 0, divisions - 1, start_point, end_point))

    return points


def calculate_nozzle_coordinates_truncated_parabola(initial_point, initial_angle, final_point, divisions=100):
    # Calculate the extrapolated vertex point
    # Print the length fraction based on the passed final point

    # Assuming x^2 parabola

    initial_slope = np.tan(initial_angle)

    x1, y1 = initial_point
    x2, y2 = final_point

    numerator = y2 - y1 - initial_slope * x2 + initial_slope * x1
    denominator = x2 ** 2 - 2 * x1 * x2 - x1 ** 2 + 2 * x1 ** 2

    a = numerator / denominator
    b = initial_slope - 2 * a * x1
    c = y1 - a * x1 ** 2 - b * x1

    nozzle_height = lambda x : a * x ** 2 + b * x + c
    angle = lambda x : 2 * a * x + b

    print(f"The exit angle for the truncated bell is {angle(final_point[0])} radians or {angle(final_point[0]) * 180 / np.pi} degrees")

    inputs = np.linspace(initial_point[0], final_point[0], divisions)
    outputs = nozzle_height(inputs)


    points = [inputs, outputs]

    # Convert tuples to 2d numpy - https://stackoverflow.com/questions/39806259/convert-list-of-list-of-tuples-into-2d-numpy-array
    points = np.array([*points])
    points = points.transpose()

    return points


#region FUNCTIONS FOR MAIN
def display_constructed_quadratic():
    start_point = (0, 0.1)
    start_angle = 35 / 180 * np.pi

    end_point = (1, 0.5)
    end_angle = 8 / 180 * np.pi

    points = calculate_nozzle_coordinates_bezier(start_point, start_angle, end_point, end_angle)

    # Convert tuples to 2d numpy - https://stackoverflow.com/questions/39806259/convert-list-of-list-of-tuples-into-2d-numpy-array
    points = np.array([*points])
    points = points.transpose()

    plt.plot(points[0], points[1])
    inputs = np.linspace(start_point[0], end_point[0])
    plt.plot(inputs, np.tan(start_angle) * (inputs - start_point[0]) + start_point[1])
    plt.plot(inputs, np.tan(end_angle) * (inputs - end_point[0]) + end_point[1])
    plt.show()


def compare_truncated_to_quadratic():
    start_point = (0, 0.1)
    start_angle = 35 / 180 * np.pi

    end_point = (1, 0.5)
    end_angle = 5.717686887804168 / 180 * np.pi

    quadratic_points_nonzero = transpose_tuple(calculate_nozzle_coordinates_bezier(start_point, start_angle, end_point, end_angle))
    quadratic_points_zero = transpose_tuple(calculate_nozzle_coordinates_bezier(start_point, start_angle, end_point, 0))
    truncated_points = transpose_tuple(calculate_nozzle_coordinates_truncated_parabola(start_point, start_angle, end_point))

    fig, ((ax1, hide_me_1), (ax2, hide_me_2)) = plt.subplots(2, 2)

    ax1.plot(quadratic_points_nonzero[0], quadratic_points_nonzero[1])
    ax1.plot(truncated_points[0], truncated_points[1])

    ax2.plot(quadratic_points_zero[0], quadratic_points_zero[1])
    ax2.plot(truncated_points[0], truncated_points[1])

    hide_me_1.axis('off')
    hide_me_2.axis('off')

    hide_me_1.text(-0.1, 0, "When the exit angles are equivalent, the \nnozzles appear to be an exact match. \nThe quadratic bezier adds another degree \nof freedom, allowing you to vary the exit \nangle. I have yet to do research on the \noptimal exit angle, but I would assume \nit to be zero. In that case, there is \nnoticable difference.")

    plt.show()

#endregion



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
    # display_constructed_quadratic()
    # calculate_nozzle_coordinates_truncated_parabola((0, 0.1), 35 * np.pi / 180, (1, 0.5))
    compare_truncated_to_quadratic()

    # inputs = np.linspace(20, 50)
    # outputs = []
    
    # for k in inputs:
    #     outputs.append(determine_expansion_ratio(k, 1, 1.3))

    # plt.plot(inputs, outputs)
    # plt.show()