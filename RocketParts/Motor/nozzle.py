# NOZZLE CLASS AND DESIGN
# Script for the nozzle object and the equations that will let us CAD it
# This may be too many responsibilities for one file

import numpy as np
import matplotlib.pyplot as plt
from Helpers.decorators import diametered
from RocketParts.massObject import MassObject




from presetObject import PresetObject
from Helpers.general import linear_intersection, interpolate, interpolate_point, transpose_tuple, get_radius


#region NOZZLE CONSTRUCTION METHODS
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

    print(f"The exit angle for the truncated bell is {angle(final_point[0])} radians \
            or {angle(final_point[0]) * 180 / np.pi} degrees")

    inputs = np.linspace(initial_point[0], final_point[0], divisions)
    outputs = nozzle_height(inputs)


    points = [inputs, outputs]

    # Convert tuples to 2d numpy
    # https://stackoverflow.com/questions/39806259/convert-list-of-list-of-tuples-into-2d-numpy-array
    points = np.array([*points])
    points = points.transpose()

    return points

#endregion

#region FUNCTIONS TO BE RUN FOR DISPLAY
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
    ax1.set(title="Same Angle", xlabel="Horizontal Distance", ylabel="Horizontal Distance")

    ax2.plot(quadratic_points_zero[0], quadratic_points_zero[1])
    ax2.plot(truncated_points[0], truncated_points[1])
    ax2.set(title="Different Angle", xlabel="Horizontal Distance", ylabel="Horizontal Distance")

    hide_me_1.axis('off')
    hide_me_2.axis('off')

    # So, my implementation of the parabolic nozzle construction is slightly different from Cristian's. In his model, the component that is allowed to vary is the length, rather than the exit angle
    # I believe that the first one matched up simply by chance, but I am pretty sure that the quadratic bezier solution is slightly more general.
    # However, the parabolic construction may be the method that 80%-bell is referring to.
    hide_me_1.text(-0.1, 0, "When the exit angles are equivalent, the \nnozzles appear to be an exact match. \nThe quadratic bezier adds another degree \nof freedom, allowing you to vary the exit \nangle. From Rao's original publications, \nthe exit angle is an important factor \nin properly approximating the shape.")

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

@diametered(radius_name="bolt_radius", diameter_name="bolt_diameter")
class RetentionRing(MassObject):
    def __init__(self, **kwargs):
        self.bolt_count = 6
        self.bolt_radius = 0.00635 / 2
        self.target_safety_factor = 1.5
        self.bolt_shear_strength = 900_000_000 * 0.6 # Pa
        self.retention_ring_shear_strength = 900_000_000 * 0.6 # Pa
        self.retention_ring_compressive_strength = 250e6 # Pa
        # Width of the retention ring
        self.bolt_length_into_ring = 0.0127 * 3/4 # m; totally made up
        # The shortest length between the top of the retention ring and the middle of the top bolt
        self.bolt_minor_thickness = 0.0254

        # Force variables that should change frequently through a simulation
        # # https://workflowy.com/s/nozzle-retention/R3QmGFlhHrfeqdaw
        # shear load = abs(inner weight + base drag + internal pressure force - thrust - external weight - external drag)
        self.internal_load = 50_000 # N; all of the forces pushing down on the inside of the nozzle
        self.external_load = 600 # N; all of the forces pushing down on the outside of the shell

        self.overwrite_defaults(**kwargs)
    
    @property
    def bolt_area(self):
        return np.pi * self.bolt_radius ** 2

    @property
    def total_bolt_area(self):
        return self.bolt_count * self.bolt_area
    
    @property
    def bolt_shear_safety_factor(self):
        experienced_pressure = self.internal_load / self.total_bolt_area

        return self.bolt_shear_strength / experienced_pressure
    
    @property
    def tear_out_safety_factor(self):
        # It has to tear out on both sides of the bolt, and on the end
        individual_tear_out_area = self.bolt_length_into_ring * self.bolt_minor_thickness * 2
        individual_tear_out_area += self.bolt_diameter * self.bolt_minor_thickness
        experienced_pressure = self.internal_load / (individual_tear_out_area * self.bolt_count)

        return self.retention_ring_shear_strength / experienced_pressure
    
    @property
    def bearing_safety_factor(self):
        # It has to tear out on both sides of the bolt, and on the end
        individual_bearing_area = self.bolt_length_into_ring * self.bolt_diameter
        experienced_pressure = self.internal_load / (individual_bearing_area * self.bolt_count)

        return self.retention_ring_compressive_strength / experienced_pressure

    def check_safety_factor(self):
        print(f"Shear: {self.bolt_shear_safety_factor}")
        print(f"Tear Out: {self.tear_out_safety_factor}")
        print(f"Bearing: {self.bearing_safety_factor}")

# Tear out/bearing for the outside coupler piece will eventually be an issue with drag attempting to accelerate the outer shell more than accelerates the entire rocket 


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

        # Both are  overriden by a CEA lookup in the actual motor simulation
        self.isentropic_exponent = 1.3
        self.exit_pressure = 100000 # Pascals. Assumes the nozzle is optimized for sea level

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
        # FIXME: occasionally this gives a very negative value


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

        momentum_component = (first_coefficient * second_coefficient * third_coefficient) ** (1 / 2)

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

    # TODO: move nozzle construction to different file
    # display_constructed_quadratic()
    # calculate_nozzle_coordinates_truncated_parabola((0, 0.1), 35 * np.pi / 180, (1, 0.5))
    # compare_truncated_to_quadratic()

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

    # Total weight is based on the wet mass. It will actually be less. For a more complex calculation, it would have to be frame-by-frame # TODO: write code that does this in the Analysis folder
    # nozzle base drag is based on CD for base=0.25 out of CD total = 0.85, which is about 30%, then I multiplied it by the 2000 N at max drag
    # The pressure is pi*(0.1651/2)^2 * 2500000
    # Tensile strength of steel alloy screw is 900000000 Pa (according to McMasterCarr), but I will use 60% for shear strength. 900_000_000 * 0.6
    # Tensile strength of aluminum is much worse than steel
    # I am going to look at a few diameters, but I think we are in the range of 3/8 inch
    # Highly sensitive to bolt diameter: 8 mm gives 30, 10 mm gives 20, 12 mm gives 14
    # Tanner said 620528156 Pa (90000 psi) was what he had been using for his bolts
    # print(find_required_retention_bolts(120 * 9.81, 600, 53520, 620528156, 0.00635, safety_factor=1))
    # only giving two for some reason
    retention = RetentionRing()
    retention.check_safety_factor()

    pass