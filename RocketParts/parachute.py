from numpy import pi
from preset_object import PresetObject


# Linear interpolation of radius does not make sense. Any time you change the radius (reference area, you have to recalculate the CD)
class Parachute(PresetObject):
    def calculate_area(self, radius=None):
        if radius is not None:
            self.radius = radius

        self.area = pi * self.radius ** 2

    def __init__(self, config={}):
        self.radius = 1  # meters, I'm just making it up
        self.drag_coefficient = 1.0
        self.mass = 0.01  # kg
        self.target_altitude = 1000  # m AGL (idk how actual sensors work)

        # Should recalculate center of pressure, don't bother too much until Barrowman equations are implemented. Also will be difficult because the parachute rotates separately from the rocket

        self.deployed = False

        super().overwrite_defaults(config)

        self.calculate_area()


    def should_deploy(self, rocket):
        if rocket.turned and rocket.position[2] < self.target_altitude and not self.deployed:
            print("Should deploy thinks true")
            return True

        return False


    def deploy(self, rocket):
        # TODO: Rewrite this to use a gradual deployment function
        self.deployed = True

        rocket.reference_area = self.area
        rocket.drag_coefficient = self.drag_coefficient

    # def update(self):
    #     if self.deployed:
    #         rocket.ref

    def calculate_tension(self, weight, drag):
        "Return the tension present in the ropes holding the parachute up."
        # Double check that this is correct
        return weight - drag

    # Need some kind of function to recalculate the center of pressure, the area, and the coefficient of drag.
    # For now, the rocket's values will just be overriden by the parachute


class ApogeeParachute(Parachute):
    def should_deploy(self, rocket):
        return rocket.velocity[2] < 0 and not self.deployed
