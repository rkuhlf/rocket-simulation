from numpy import pi
from preset_object import PresetObject


# Linear interpolation of radius does not make sense. Any time you change the radius (reference area, you have to recalculate the CD)
class Parachute(PresetObject):

    def __init__(self, config={}):
        self.radius = 2  # meters, I'm just making it up
        self.area = pi * self.radius ** 2
        self.drag_coefficient = 1.75
        self.mass = 0.01  # kg

        # Should recalculate center of pressure, don't bother too much until Barrowman equations are implemented. Also will be difficult because the parachute rotates separately from the rocket

        self.deployed = False

        super().overwrite_defaults(config)

    # For some reason, the drag is not being applied in the direction of free-stream velocity
    def deploy(self, rocket):
        # TODO: Rewrite this to use a gradual deployment function
        if not self.deployed:
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
