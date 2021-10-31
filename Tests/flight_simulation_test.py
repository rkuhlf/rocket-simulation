# TEST THE OUTPUTS OF FLIGHT TO FIND BUGS
# Uses the data from outputs.csv and a base rocket
# In theory, these tests should be run on every single rocket simulation to verify that none of the programming messed up

import unittest
import pandas as pd
import numpy as np
from random import random

import sys
sys.path.append(".")

import SimulateRocket
from Helpers.general import angle_between


class TestSimulateRocket(unittest.TestCase):        
    def get_current_simulation(self):
        if not hasattr(self, "sim"):
            self.sim = SimulateRocket.simulate_rocket()
        
        return self.sim

    def get_current_output(self):
        if not hasattr(self, "data"):
            sim = self.get_current_simulation()

            self.data = pd.read_csv(sim.logger.full_path)
        
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

    def lift_direction(self):
        pass
        # These things should be true for the vast majority of the ascent
        # There could be small differences depending on off-by-one frame issues
        # Also atm I am not accounting for different headings so, that part is wrong


        # When theta_around is 1.5 and theta_down is 0.2: 
        # the rocket is heading in the positive y direction and the positive z direction
        # The lift is in the positive y direction
        # And the angular accel. down should be negative, pushing the fins down
        # Therefore, the y+ axis should be causing negative angular acceleration
        # ? appears to be working still

        # When theta_around is 1.5 and theta_down is 2.8: 
        # the rocket is heading in the positive y direction and the negative z direction
        # The lift is in the negative y direction
        # And the angular accel. down should be negative, pushing the fins down
        # Therefore, the y+ axis should be causing positive angular acceleration
        # ? lift looks good


        # When theta_around is 4.7 and theta_down is 0.2: 
        # the rocket is heading in the negative y direction and the positive z direction
        # The lift is in the negative y direction
        # And the angular acceleration down should be negative, pushing the fins down
        # Therefore, the y+ axis should be causing positive angular acceleration
        # ? This one looks good still

        # When theta_around is 4.7 and theta_down is 2.8: 
        # the rocket is heading in the negative y direction and the negative z direction
        # The lift is in the positive y direction
        # And the angular velocity down should be negative, pushing the fins down
        # Therefore, the y+ axis should be causing negative angular acceleration
        # ? This looks like it is correct

        # You know what, it is mildly possible that we have just got an off-by-one error that results in an extra push after we are already over the edge
        


# TODO: implement test to make sure that the rocket flight is nearly identical (with the same/no wind) regardless of which way around the rotation you start (0.05 and -0.05)

class TestWholeFlight(TestSimulateRocket):
    def test_flipping(self):
        data = self.get_current_output()

        for i, row in data.iterrows():
            self.assertGreater(abs(row["rotation2"]), 0,  
                "The flipping code is not working correctly. Somehow we got a negative rotation down.")
            
            self.assertLess(abs(row["rotation2"]), np.pi,  
                "The flipping code is not working correctly. Somehow we got an overrotated rotation down.")


    def test_lift_drag_perpendicular(self):
        # By definition, the lift and the drag on the rocket should be directed perpendicularly
        data = self.get_current_output()

        for i, row in data.iterrows():
            lift = np.array([row["Lift1"], row["Lift2"], row["Lift3"]])
            drag = np.array([row["Drag1"], row["Drag2"], row["Drag3"]])

            if np.any(np.isnan(lift)) or np.any(np.isnan(drag)):
                continue

            between = angle_between(lift, drag)

            self.assertAlmostEqual(between, np.pi/2)

    def test_arbitrary_rotations(self):
        # When there is no wind, only the angle of inclination matters - the apogee should be the same regardless of theta_around
        self.sim = SimulateRocket.get_simulation()
        self.sim.environment.apply_wind = False
        original_rotation = self.sim.rocket.rotation.copy()


        self.sim.run_simulation()
        base_apogee = self.sim.apogee


        self.sim.reset()
        self.sim.rocket.rotation = np.array([random() * np.pi * 2, original_rotation[1]])

        self.sim.run_simulation()
        new_apogee = self.sim.apogee

        self.assertLess(abs(base_apogee - new_apogee) / base_apogee, 0.005, "There is an error in the rotation code - running two simulations at identical inclinations should result in very similar heights (with no randomized features). These simulations had different results.")


