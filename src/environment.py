# ENVIRONMENT CLASS
# Define an object to store the atmospheric conditions at any position in the world based on the 1976 Standard Atmosphere
# It models the wind (hopefully it will eventually include gusts, but right now it's a DIY thing that's wrong)
# Also models air density, pressure, and temperature.

import pandas as pd

from helpers.data import inputs_path
from helpers.general import interpolate, get_next
from lib.presetObject import PresetObject
from data.input.models import get_density, get_speed_of_sound
from data.input.wind.whiteSandsModels import speed_at_altitude
from helpers.data import interpolated_lookup
from data.input.wind import Wind


# TODO: rewrite this object to use the same data methods and closure things as the other models
class Environment(PresetObject):
    """
        Define how the environment works for a simulation (both the motor and the rocket).
        The most important factor is the time_increment - check out some of the timeStudies to see the effect.
        The base_altitude is also relatively important, as it can seriously cut down on the air density, decreasing drag
        
        The current model implements the 1976 Standard Atmosphere based on Digital Dutch's data as well as a variable gravity model of a perfectly spherical Earth.
    """
    
    def __init__(self, **kwargs):
        self.time = 0
        self.time_increment = 0.01  # seconds

        self.earth_mass = 5.972 * 10 ** 24  # kg
        self.gravitational_constant = 6.67 * 10 ** -11  # Newtons kg^-2 m^2
        self.earth_radius = 6371071.03  # m
        self.base_altitude = 1300  # m


        self.rail_length = 13.1064 # meters based on 43 feet at White Sands

        self._atmospheric_path = "airQuantities.csv"
        self.previous_air_density_index = 0

        self.apply_wind = True

        super().overwrite_defaults(**kwargs)

        self.load_atmospheric_data()

        
        self.wind = Wind()
        # It is a little weird to override a default by default, but whatever
        self.wind.get_average_speed_altitude = speed_at_altitude

    @property
    def atmospheric_path(self):
        return self._atmospheric_path

    @atmospheric_path.setter
    def atmospheric_path(self, p):
        self._atmospheric_path = p
        self.load_atmospheric_data()

    def load_atmospheric_data(self):
        self.atmospheric_data = pd.read_csv(inputs_path + self._atmospheric_path)
        self.atmospheric_data.drop(
            columns=["Viscosity", "Temperature"])

    def simulate_step(self):
        self.time += self.time_increment

        # Update the wind

    @property
    def gravitational_acceleration(self):
        return self.get_gravitational_attraction(1, 0)

    def get_gravitational_attraction(self, rocket_mass, altitude):
        """Returns the force (in Newtons) of the Earth's pull on the rocket"""
        return self.gravitational_constant * self.earth_mass * rocket_mass / (
            self.earth_radius + altitude + self.base_altitude) ** 2

    def get_air_pressure(self, altitude):
        return interpolated_lookup(self.atmospheric_data, "Altitude", altitude / 1000, "Pressure")

    def get_air_speed(self, altitude):
        if not self.apply_wind:
            return [0, 0, 0]
        # this tells us how the rocket is moving through space relative to the surrounding fluids
        # Random things that might I come back to
        # https://retscreen.software.informer.com/4.0/
        # https://ieeexplore.ieee.org/document/6808712
        # https://www.osti.gov/servlets/purl/6632347
        # https://github.com/srlightfoote/AWEA_WRA_Working_Group/blob/master/Example_Wind_Resource_Assessment_Using_R.md#packages
        # https://rmets.onlinelibrary.wiley.com/doi/pdf/10.1017/S1350482702004048
        # https://www.researchgate.net/publication/328173177_SMARTS_Modeling_of_Solar_Spectra_at_Stratospheric_Altitude_and_Influence_on_Performance_of_Selected_III-V_Solar_Cells/figures?lo=1
        # https://qph.fs.quoracdn.net/main-qimg-30e7697ac625734562eaca496e813467.webp
        # https://www.sciencedirect.com/science/article/abs/pii/0038092X81902048 Looks promising but ccan't access

        # Potentially Have the Table data
        # https://www.meteoblue.com/en/weather/archive/export/white-sands-national-monument_united-states-of-america_5497921?daterange=2021-07-20%20-%202021-08-03&domain=NEMSGLOBAL&params%5B%5D=temp2m&min=2021-07-20&max=2021-08-03&utc_offset=-6&timeResolution=daily&temperatureunit=FAHRENHEIT&velocityunit=KILOMETER_PER_HOUR&energyunit=watts&lengthunit=metric&degree_day_type=10%3B30&gddBase=10&gddLimit=30
        # https://gmao.gsfc.nasa.gov/reanalysis/MERRA-2/ <- seems most likely

        # Probably useful
        # https://weatherspark.com/y/9257/Average-Weather-in-Lake-Jackson-Texas-United-States-Year-Round
        # https://numpy.org/doc/stable/reference/random/generated/numpy.random.weibull.html
        # https://www.quora.com/What-is-the-average-wind-speed-at-different-altitudes
        # https://globalwindatlas.info/ - I think this will tell me the z value

        # I believe that Lake Jackson average windspeed is about 2.1 m/s
        # https://globalwindatlas.info/ also has some direction data
        return self.wind.get_air_velocity(self.time, altitude)


    def get_speed_of_sound(self, altitude):
        """Look up the speed of sound by the altitude (in kilometers)"""
        return get_speed_of_sound(altitude)

    def get_air_density_from_model(self, altitude):
        """Look up a the air density in kg/m^3 by the altitude in km using a fitted polynomial model"""
        # From the polynomial models file
        return get_density(altitude)


    def get_air_density_from_lookup(self, altitude):
        # TODO: Make these functions taht you can override like they are everywhere else.
        # This is mostly just here to double check that the model is working
        return interpolated_lookup(self.atmospheric_data, "Altitude", altitude, "Density")


    def get_air_density(self, altitude):
        """Get the air density at a given number of meters in the air"""

        altitude /= 1000  # convert to kilometers

        # return self.get_air_density_from_model(altitude)
        return self.get_air_density_from_lookup(altitude)
