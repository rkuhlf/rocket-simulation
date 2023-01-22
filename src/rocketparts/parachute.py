# PARACHUTE CLASS
# Should be passed as an array to the rocket class
# This is really simple right now; it doesn't even have any snatch forces or rope stuff

from numpy import pi
from src.data.input.models import get_density


from lib.general import constant, interpolate
from src.rocketparts.massObject import MassObject
from lib.decorators import diametered


#region Opening Force Functions
def pflanz_method(parachute: "Parachute", expected_velocity: float, air_density: float):
    # Not currently including the velocity reduction
    Cx = parachute.opening_load_factor
    force_reduction_factor = 0.6

    dynamic_pressure = 1/2 * air_density * expected_velocity ** 2

    return Cx * force_reduction_factor * dynamic_pressure * parachute.drag_area
#endregion

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

        self.opening_load_factor_function = constant(1.7)


        self.overwrite_defaults(**kwargs)

    @property
    def area(self):
        return pi * self.radius ** 2

    @property
    def drag_area(self):
        return self.area * self.CD

    def get_inflation_time(self, velocity, density):
        # FIXME: actually calculate
        return 0.25
    
    def get_force_reduction_load_factor(self, ballistic_parameter):
        return 
    
    def get_ballistic_parameter(self, mass, air_density, velocity):
        """Often abbreviated with A"""
        return 2 * mass / (self.drag_area * self.get_inflation_time(velocity, air_density) * air_density * velocity)

    @property
    def opening_load_factor(self):
        return self.opening_load_factor_function(self)

    # TODO: add some kind of deployment variance here
    def should_deploy(self, rocket):
        return rocket.descending and rocket.position[2] < self.target_altitude and not self.deployed

    def deploy(self, rocket):
        self.deployed = True
        self.time_of_deployment = rocket.simulation.time
        # TODO: refactor so thatt you can say rocket.parachute.deployed
        # I want to make all of these functions so that they do not require rocket to be passed.
        rocket.parachute_deployed = True

    def get_drag(self, rocket):
        # TODO: use a more accurate interpolation for opening
        if self.deployed:
            interpolated_area = interpolate(rocket.simulation.time, self.time_of_deployment, self.time_of_deployment + self.required_deployment_time, 0, self.area)
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



if __name__ == "__main__":
    p = Parachute()
    force = pflanz_method(p, 50, get_density(10))


    print("%.2f" % force)