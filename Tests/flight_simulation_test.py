# TEST THE OUTPUTS OF FLIGHT TO FIND BUGS
# Uses the data from outputs.csv and a base rocket
# In theory, these tests should be run on every single rocket simulation to verify that none of the programming messed up

import unittest
import pandas as pd
import numpy as np

import sys
sys.path.append(".")

import SimulateRocket


class TestSimulateRocket(unittest.TestCase):
    def get_current_simulation(self):
        if not hasattr(self, "sim"):
            self.sim = SimulateRocket.simulate_rocket()
        
        return self.sim

    def get_current_output(self):
        if not hasattr(self, "data"):
            sim = self.get_current_simulation()

            data_path = "Data/Output/" + sim.logger.target
            self.data = pd.read_csv(data_path)
        
        return self.data


class TestAverages(TestSimulateRocket):
    def test_total_impulse(self):
        # The total impulse of the motor should be the same in the inputs and the outputs
        sim = self.get_current_simulation()
        target = sim.rocket.motor.get_total_impulse()

        time_increment = sim.environment.time_increment


        data = self.get_current_output()

        # Integrate over the thrust using a trapezoidal reimann sum (that is how it is added in the model)
        actual = 0
        previous_thrust = 0
        for i, row in data.iterrows():
            actual += (row["Thrust"] + previous_thrust) / 2 * time_increment
            previous_thrust = row["Thrust"]

        percent_error = abs(actual - target) / target * 100
        self.assertLess(percent_error, 1, 
        "The computed thrust of your model is more than 1 percent off of what it should be. This is likely caused by a time increment that is too large relative to your burn time.")


class TestDescent(TestSimulateRocket):
    def test_descent(self):
        data = self.get_current_output()

        descending = False
        previous_altitude = 0
        for i, row in data.iterrows():
            current_altitude = row["position3"]

            if descending:
                self.assertLess(current_altitude, previous_altitude, 
                "Somehow, your rocket started going up after it reached apogee. Rockets do not do this. One possible explanation involves the discrete integral that is taken with parachute drag. If your parachute causes a large enough force over a large time increment, it may 'bounce,' which isn't physically realistic. Try decreasing your time increment.")

            if current_altitude < previous_altitude:
                descending = True
            
            previous_altitude = current_altitude

class TestAscent(TestSimulateRocket):
    def test_rotation(self):
        data = self.get_current_output()

        previous_altitude = 0
        for i, row in data.iterrows():
            current_altitude = row["position3"]
            # print(data["rotation2"])
            self.assertLess(abs(row["rotation2"]), np.pi * 7/9,  
                "Your rocket is rotated more than 140 degrees downwards. That means the nose cone is pointing downwards during the ascent - regardless of whether a programming error, your rocket is likely going to be experienceing strains that it cannot handle. Check the stability over time. If the rocket never goes unstable, there may be an issue in the programming")

            if current_altitude < previous_altitude:
                # we are no longer ascending
                break
            
            previous_altitude = current_altitude


