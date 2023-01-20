# TODO: actually implement tests for the motor
# I need to make sure that the total mass loss is equal to the sum of the mass flows out




import unittest
import pandas as pd
import numpy as np
from random import random


from helpers.data import riemann_sum
# import SimulateMotor
import Simulations.DesignedMotorHTPB as SimulateMotor


class TestSimulateMotor(unittest.TestCase):        
    def get_current_simulation(self):
        if not hasattr(self, "sim"):
            self.sim = SimulateMotor.get_sim()
        
        return self.sim

    def get_current_output(self):
        if not hasattr(self, "data"):
            sim = self.get_current_simulation()

            self.data = pd.read_csv(sim.logger.full_path)
        
        return self.data


class TestAverages(TestSimulateMotor):
    def test_total_impulse(self):
        # The total impulse of the motor should be the same in the inputs and the outputs
        sim = self.get_current_simulation()
        target = sim.motor.get_total_impulse()

        time_increment = sim.environment.time_increment


        data = self.get_current_output()

        # Integrate over the thrust using a trapezoidal riemann sum (that is how it is added in the model)
        actual = 0
        previous_thrust = 0
        for i, row in data.iterrows():
            actual += (row["Thrust"] + previous_thrust) / 2 * time_increment
            previous_thrust = row["Thrust"]

        percent_error = abs(actual - target) / target * 100
        self.assertLess(percent_error, 1, 
        "The computed thrust of your model is more than 1 percent off of what it should be. This is likely caused by a time increment that is too large relative to your burn time.")

    def test_mass_flow(self):
        data = self.get_current_output()

        flow_in = riemann_sum(data["time"], data["mass_flow"])
        flow_out = riemann_sum(data["time"], data["mass_flow_out"])

        # Based on the math, even if you stop as soon as pressure equalizes, there is no way you have more than 2 kilograms in there
        self.assertLess(flow_in - flow_out, 2)





class TestWholeFlight(TestSimulateMotor):
    def test_flipping(self):
        data = self.get_current_output()

        for i, row in data.iterrows():
            self.assertGreater(abs(row["rotation2"]), 0,  
                "The flipping code is not working correctly. Somehow we got a negative rotation down.")
            
            self.assertLess(abs(row["rotation2"]), np.pi,  
                "The flipping code is not working correctly. Somehow we got an overrotated rotation down.")
