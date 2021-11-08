# PARACHUTE CLASS

from numpy import pi
from RocketParts.massObject import MassObject
import sys
sys.path.append(".")

from Helpers.general import magnitude
# TODO: the descent rate is too slow

class Parachute(MassObject):
    def calculate_area(self, radius=None):
        if radius is not None:
            self.radius = radius

        self.area = pi * self.radius ** 2

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.radius = 1.2192 # meters
        self.mass = 0.01  # kg
        self.target_altitude = 1000  # m AGL (idk how actual sensors work)

        # Should recalculate center of pressure, don't bother too much until Barrowman equations are implemented. Also will be difficult because the parachute rotates separately from the rocket

        self.deployed = False

        # Should probably have a drag object class to deal with the parachute and the rocket
        self.CD = 0.97

        super().overwrite_defaults(**kwargs)

        self.calculate_area()

    @property
    def diameter(self):
        return self.radius * 2

    @diameter.setter
    def diameter(self, d):
        self.radius = d / 2
        self.calculate_area()

    def should_deploy(self, rocket):
        return rocket.descending and rocket.position[2] < self.target_altitude and not self.deployed


    def deploy(self, rocket):
        # TODO: Rewrite this to use a gradual deployment function
        self.deployed = True
        rocket.parachute_deployed = True

    def get_drag(self, rocket):
        if self.deployed:
            return 1/2 * self.CD * self.area * rocket.dynamic_pressure * magnitude(rocket.relative_velocity) ** 2

        return 0

    def calculate_tension(self, weight, drag):
        "Return the tension present in the ropes holding the parachute up."
        # Double check that this is correct
        return weight - drag

    # Need some kind of function to recalculate the center of pressure, the area, and the coefficient of drag.
    # For now, the rocket's values will just be overriden by the parachute


class ApogeeParachute(Parachute):
    def should_deploy(self, rocket):
        return rocket.descending and not self.deployed
