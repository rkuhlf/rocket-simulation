# PARACHUTE CLASS
# Should be passed as an array to the rocket class
# This is really simple right now; it doesn't even have any snatch forces or rope stuff

from numpy import pi


from Helpers.general import interpolate
from RocketParts.massObject import MassObject
from Helpers.decorators import diametered


@diametered
class Parachute(MassObject):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.radius = 2.4384 # meters
        self.mass = 0.5  # kg
        self.target_altitude = 1000  # m AGL (idk how actual sensors work)

        self.deployed = False
        self.time_of_deployment = 0

        self.required_deployment_time = 3 # seconds; idk

        # Should probably have a drag object class to deal with the parachute and the rocket
        self.CD = 0.97


        self.overwrite_defaults(**kwargs)

    @property
    def area(self):
        return pi * self.radius ** 2


    # TODO: add some kind of deployment variance here
    def should_deploy(self, rocket):
        return rocket.descending and rocket.position[2] < self.target_altitude and not self.deployed

    def deploy(self, rocket):
        self.deployed = True
        self.time_of_deployment = rocket.environment.time
        rocket.parachute_deployed = True

    def get_drag(self, rocket):
        # TODO: use a more accurate interpolation for opening
        if self.deployed:
            interpolated_area = interpolate(rocket.environment.time, self.time_of_deployment, self.time_of_deployment + self.required_deployment_time, 0, self.area)
            interpolated_area = min(interpolated_area, self.area)

            return rocket.dynamic_pressure * self.CD * interpolated_area

        return 0

    def calculate_tension(self, weight, drag):
        "Return the tension present in the ropes holding the parachute up."
        # Double check that this is correct
        raise NotImplementedError()
        


class ApogeeParachute(Parachute):
    def should_deploy(self, rocket):
        return rocket.descending and not self.deployed



