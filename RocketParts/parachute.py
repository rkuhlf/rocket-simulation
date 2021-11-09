# PARACHUTE CLASS

from numpy import pi
from RocketParts.massObject import MassObject
import sys
sys.path.append(".")

from Helpers.general import magnitude, interpolate


class Parachute(MassObject):
    def calculate_area(self, radius=None):
        if radius is not None:
            self.radius = radius

        self.area = pi * self.radius ** 2

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.radius = 2.4384 # meters
        self.mass = 0.01  # kg
        self.target_altitude = 1000  # m AGL (idk how actual sensors work)

        self.deployed = False
        self.time_of_deployment = 0

        self.required_deployment_time = 15 # seconds; idk

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
        self.deployed = True
        self.time_of_deployment = rocket.environment.time
        rocket.parachute_deployed = True

    def get_drag(self, rocket):
        if self.deployed:
            interpolated_area = interpolate(rocket.environment.time, self.time_of_deployment, self.time_of_deployment + self.required_deployment_time, 0, self.area)
            interpolated_area = min(interpolated_area, self.area)
            return 1/2 * self.CD * interpolated_area * rocket.dynamic_pressure

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
