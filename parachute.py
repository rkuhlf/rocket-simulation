from numpy import pi
from preset_object import PresetObject


class Parachute(PresetObject):

    def __init__(self, config={}):
        self.radius = 2  # meters, I'm just making it up
        self.area = pi * self.radius ** 2
        self.drag_coefficient = 1.75
        self.mass = 0.01  # kg

        self.deployed = False

        super().overwrite_defaults(config)


    def deploy(self, rocket):
        # TODO: Rewrite this to use a gradual deployment function
        if not self.deployed:
            self.deployed = True

            rocket.vertical_area = self.area
            rocket.drag_coefficient = self.drag_coefficient

    def calculate_tension(self, weight, drag):
        "Return the tension present in the ropes holding the parachute up."
        # Double check that this is correct
        return weight - drag

    # Need some kind of function to recalculate the center of pressure, the area, and the coefficient of drag.
    # For now, the rocket's values will just be overriden by the parachute
