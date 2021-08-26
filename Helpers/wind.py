# Ranges from -1 to 1 I think
# Installing this requires C++ compilation. If you don't want to install that capability on your computer, you can install it by downloading the wheel from https://www.lfd.uci.edu/~gohlke/pythonlibs/#noise
# Then running pip install <wheel-location>
from noise import pnoise1
import matplotlib.pyplot as plt
import numpy as np
from Helpers.general import vector_from_angle
import scipy.stats as st


class Wind():
    # A wind simulator based on perlin noise

    def determine_std(self):
        size = 10000


        ys = [[] for _ in range(self.count)]


        for index in range(len(ys)):
            for i in range(size):
                ys[index].append(pnoise1(
                    self.seeds[index] + i * self.time_increment * self.interpolation_speed, self.octaves))

        average_ys = []
        for i in range(len(ys[0])):
            total = 0
            for j in range(len(ys)):
                total += ys[j][i]

            average_ys.append(total / len(ys))


        return np.std(average_ys)

    def __init__(
            self, time_increment, count=30, octaves=4, wind_direction=[0, 0],
            interpolation_speed=0.1, k=2):
        # FIXME: I never really bothered to test any of this
        # TODO: Add some more visualization stuff to make sure that this is following a weibull distribution and that interpolation speed = 0.1 makes sense
        self.interpolation_speed = interpolation_speed
        self.count = count
        self.seeds = np.random.random(self.count) * self.count * 100

        self.octaves = octaves
        self.time_increment = time_increment

        # Wind direction isn't constant.
        self.wind_direction = np.array(wind_direction, dtype="float64")

        # https://www.homerenergy.com/products/pro/docs/latest/weibull_k_value.html
        # 3 or 4 will be relatively steady, 1.5 will be gusty
        self.weibull_shape = k

        # Have to manually calculate normalized perlin noise deviation
        # The time increment has to be the exact same each time too, otherwise the standard deviation of the theoretical won't match the actual

        self.std = self.determine_std()


    def randomize_direction(self):
        # At this point I am basically just assuming that there is no vertical wind
        # This function is called by the environment class. It is basically a public method
        self.wind_direction[0] = np.random.rand() * np.pi * 2

    def get_normal_perlin(self, x):
        total = 0
        for i in range(self.count):
            total += pnoise1(self.seeds[i] + x, self.octaves)

        return total / self.count

    def get_z_score(self, mean, std, val):
        return (val - mean) / std

    def get_percentile_from_z(self, z):
        # Get the cumulative distribution function for a normal distribution based on a z-value
        return st.norm.cdf(z)


    def lookup_weibull(self, p, average):
        "Given the percentile, return the multiplier based on the weibull shape parameter and the average"
        # use self.weibull_shape
        # Based on https://www.itl.nist.gov/div898/handbook/eda/section3/eda3668.htm, I found the output given a percentile (after flipping x and y around)

        return (-np.log(1 - p)) ** (1 / self.weibull_shape) * average


    def get_average_speed_altitude(
            self, roughness, base_altitude, average_wind_speed, altitude):

        # Roughness is z_0, or roughness length
        # For lake jackson, z_0 = 1
        # Relatively good explanation: https://wind-data.ch/tools/profile.php?lng=en
        return average_wind_speed * np.log(altitude / roughness) / np.log(
            base_altitude / roughness)

    def get_air_speed(self, roughness, base_altitude, average_wind_speed,
                      altitude, time):
        "Gets the air speed in all three dimensions at a point in time"
        wind_unit_vector = vector_from_angle(self.wind_direction)

        value = self.get_normal_perlin(time * self.interpolation_speed)
        z_score = self.get_z_score(0, self.std, value)

        p = self.get_percentile_from_z(z_score)

        average_speed = self.get_average_speed_altitude(
            roughness, base_altitude, average_wind_speed, altitude)

        speed = self.lookup_weibull(p, average_speed)

        # TODO: Add some variability to the wind direction, particularly as altitude changes
        # In meters per second
        # return [0, 0, 0]
        return wind_unit_vector * speed
