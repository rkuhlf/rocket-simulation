from Helpers.general import *


def get_gravitational_attraction():
    # Position[1] updates automatically since it is basically a module wide variable
    return gravitational_constant * earth_mass / (
        earth_radius + position[1] + base_altitude) ** 2
