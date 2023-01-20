# TESTS FOR THE MASS OBJECT CLASS
# Bugs might be difficult to find in this, so I'll have some very specific tests to make sure everything is working exactly correctly

import unittest


from rocketparts.massObject import MassObject

class TestMassObject(unittest.TestCase):

    def test_CG_nested(self):
        o_ring_from_tip = 3.41
        injector_from_tip = 3.4
        ox_tank_from_tip = 2

        o_ring = MassObject({
            "mass": 0.1,
            "front": o_ring_from_tip - injector_from_tip,
            "center_of_gravity": 0.05
        })
        injector = MassObject({
            "mass": 5,
            "front": injector_from_tip - ox_tank_from_tip,
            "center_of_gravity": 0.05,
            "mass_objects": [o_ring]
        })
        ox_tank = MassObject({
            "mass": 50,
            "front": ox_tank_from_tip,
            "center_of_gravity": 1,
            "mass_objects": [injector]
        })
        rocket = MassObject({
            "mass": 10,
            "front": 0,
            "center_of_gravity": 2,
            "mass_objects": [ox_tank]
        })

        print(rocket.total_CG)
        # Meh, I am pretty sure it is correct
