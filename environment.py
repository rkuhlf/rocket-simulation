import numpy as np
import pandas as pd
from Helpers.general import interpolate, get_next
from preset_object import PresetObject
from Data.Input.models import get_density, get_speed_of_sound


class Environment(PresetObject):
    def __init__(self, config={}):
        self.time = 0
        self.time_increment = 0.01  # seconds

        self.earth_mass = 5.972 * 10 ** 24  # kg
        self.gravitational_constant = 6.67 * 10 ** -11
        self.earth_radius = 6371071.03  # m
        self.base_altitude = 4  # m

        self.density_location = "airQuantities"

        self.previous_air_density_index = 0

        super().overwrite_defaults(config)

        # https://www.digitaldutch.com/
        self.density_data = pd.read_csv(
            "Data/Input/" + self.density_location + ".csv")
        self.density_data.drop(
            columns=["Viscosity", "Temperature", "Pressure"])
        self.altitude_data = np.array(self.density_data["Altitude"])


    def simulate_step(self):
        self.time += self.time_increment
        # Update the wind


    def get_gravitational_attraction(self, rocket_mass, altitude):
        """Returns the force (in Newtons) of the Earth's pull on the rocket"""
        return self.gravitational_constant * self.earth_mass * rocket_mass / (
            self.earth_radius + altitude + self.base_altitude) ** 2


    def get_air_speed(self):
        # this tells us how the rocket is moving through space relative to the surrounding fluids

        # Random things that might I come back to
        # https://www.quora.com/What-is-the-average-wind-speed-at-different-altitudes
        # https://retscreen.software.informer.com/4.0/
        # https://ieeexplore.ieee.org/document/6808712
        # https://www.osti.gov/servlets/purl/6632347
        # https://github.com/srlightfoote/AWEA_WRA_Working_Group/blob/master/Example_Wind_Resource_Assessment_Using_R.md#packages
        # https://rmets.onlinelibrary.wiley.com/doi/pdf/10.1017/S1350482702004048
        # https://www.researchgate.net/publication/328173177_SMARTS_Modeling_of_Solar_Spectra_at_Stratospheric_Altitude_and_Influence_on_Performance_of_Selected_III-V_Solar_Cells/figures?lo=1
        # https://qph.fs.quoracdn.net/main-qimg-30e7697ac625734562eaca496e813467.webp

        # Probably useful
        # https://weatherspark.com/y/9257/Average-Weather-in-Lake-Jackson-Texas-United-States-Year-Round
        return np.array([100, 0, 0])


    def get_speed_of_sound(self, altitude):
        return get_speed_of_sound(altitude)


    def get_air_density_from_model(self, altitude):
        # From the polynomial models file
        return get_density(altitude)


    def get_air_density_from_lookup(self, altitude):
        # This is mostly just here to double check that the model is wokring
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


    def get_air_density(self, altitude):
        """Get the air density at a given number of meters in the air"""

        altitude /= 1000  # convert to kilometers

        return self.get_air_density_from_model(altitude)
