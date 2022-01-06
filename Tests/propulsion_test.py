import numpy as np
import unittest


from RocketParts.Motor.grain import *


class TestingChamber(unittest.TestCase):
    def test_flow_out(self):
        # TODO: implement test

        # Check that the mass flow rate we are using from CEA is similar to this one
        """
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
        pass

class TestingGrain(unittest.TestCase):
    def test_optimizing_length(self):
        # The length we end up with should have the correct total O/F ratio
        # That is a by-design of the function; if not, there is a mathematical error somewhere
        outer_diameter = 0.2

        fuel_mass = 10
        fuel_density = 920
        target_OF = 7

        port_diameter = determine_optimal_starting_diameter(outer_diameter, fuel_mass, fuel_density, 4.8, marxman_doran_HTPB_nitrous, target_OF)
        grain_length = find_required_length(port_diameter, outer_diameter, fuel_mass, fuel_density)

        calculated_mass = (np.pi * (outer_diameter / 2) ** 2 - (np.pi * (port_diameter / 2) ** 2)) * grain_length * fuel_density
        self.assertEqual(fuel_mass, calculated_mass)


    def test_required_length(self):
        # It seems like it is overkill to have a test for it, but there is a bug so I am going to debug pretty exhaustively. It turns out the bug was that I forgot I was testing 9 inch diameter

        inner_diameter = 0.05 # m
        outer_diameter = 0.1 # m

        mass = 60 # kg
        density = 920 # kg/m^3

        length = find_required_length(inner_diameter, outer_diameter, mass, density)

        calculated_mass = (np.pi * (outer_diameter / 2) ** 2 - (np.pi * (inner_diameter / 2) ** 2)) * length * density

        self.assertEqual(mass, calculated_mass)



