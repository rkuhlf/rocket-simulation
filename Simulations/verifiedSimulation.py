# VERIFIED SIMULATION CLASS
# Realistically, we should be verifying that there are no errors in the programming after every single time we run a simulation
# To do so, I have implemented both automated tests and a manual optical inspection
# This class simply extends the base simulation class to offer both features
# As a side note, you should really also like at a 3D representation of the flight over time, it will make many rotations easier to interpret

import sys
sys.path.append(".")

from simulation import Simulation
from Visualization.FlightOpticalAnalysis import display_optical_analysis

import unittest



class VerifiedSimulation(Simulation):
    def run_automated_tests(self):
        loader = unittest.TestLoader()
        start_dir = './Tests'
        suite = loader.discover(start_dir)
        # FIXME: the loader doesn't find anything
        # Also, it is simulating another test. I need to find a way to only run the flight_simulation ones, and to pass in the sim to it (I can just set attribute)
        print(suite)
        runner = unittest.TextTestRunner()
        runner.run(suite)

    def open_optical_analysis(self):
        #TODO: Throw some errors if you are going unstable at the beginning
        display_optical_analysis()

    def run_simulation(self):
        super().run_simulation()

        # unittest.main()
        self.run_automated_tests()
        self.open_optical_analysis()

