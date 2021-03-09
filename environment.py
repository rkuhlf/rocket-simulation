import numpy as np
import pandas as pd
from Helpers.general import interpolate, get_next
from preset_object import PresetObject


class Environment(PresetObject):
    def __init__(self, config={}):
        # probably would have been easier to just go self. for all of these, then override it with a dictionary
        self.time = 0
        self.time_increment = 0.01  # seconds

        self.earth_mass = 5.972 * 10 ** 24  # kg
        self.gravitational_constant = 6.67 * 10 ** -11
        self.earth_radius = 6371071.03  # m
        self.base_altitude = 4  # m

        self.density_location = "airQuantities"

        super().overwrite_defaults(config)


        # https://www.digitaldutch.com/
        self.density_data = pd.read_csv(
            "Data/Input/" + self.density_location + ".csv")
        self.density_data.drop(
            columns=["Viscosity", "Temperature", "Pressure"])
        self.altitude_data = np.array(self.density_data["Altitude"])

        self.previous_air_density_index = 0

    def simulate_step(self):
        self.time += self.time_increment
        # Update the wind


    def get_gravitational_attraction(self, rocket_mass, altitude):
        """Returns the force (in Newtons) of the Earth's pull on the rocket"""
        return self.gravitational_constant * self.earth_mass * rocket_mass / (
            self.earth_radius + altitude + self.base_altitude) ** 2


    def get_air_speed(self):
        # this tells us how the rocket is moving through space relative to the surrounding fluids
        return np.zeros((2))





    def get_air_density(self, altitude):
        """Get the air density at a given number of meters in the air"""
        # Air density: This is a slow calculation
        # might be faster to optimize a function to the line
        # It turns out lookups from pandas are much slower than from numpy

        altitude /= 1000  # convert to kilometers

        index = self.previous_air_density_index
        if self.altitude_data[index] > altitude:
            index, self.previous_air_density_index = get_next(
                index, self.altitude_data, self.previous_air_density_index, -1, altitude)
        elif self.altitude_data[index] < altitude:
            index, self.previous_air_density_index = get_next(
                index, self.altitude_data, self.previous_air_density_index, 1, altitude)



        previous_density = self.density_data.iloc[self.previous_air_density_index]

        next_density = self.density_data.iloc[index]

        # previous_density = previous_density.iloc[-1]
        # next_density = next_density.iloc[0]

        return interpolate(
            altitude, previous_density["Altitude"],
            next_density["Altitude"],
            previous_density["Density"],
            next_density["Density"])
