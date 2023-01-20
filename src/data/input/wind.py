# Ranges from -1 to 1 I think
# Installing this requires C++ compilation. If you don't want to install that capability on your computer, you can install it by downloading the wheel from https://www.lfd.uci.edu/~gohlke/pythonlibs/#noise
# Then running pip install <wheel-location>
from helpers.general import interpolate_looped, vector_from_angle
from lib.presetObject import PresetObject
from noise import pnoise1
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as st



# TODO: write some custom functions that work as settings for the wind
# One can be a constant magnitude
# One can be the OpenRocket method
# One can be the method that I made up

class Wind(PresetObject):
    """
    A wind simulator based on perlin noise and visual matching with second by second data from Salt Lake City
    Completely independent of time increment, but does vary over time and altitude
    Adjusts average wind speeds for altitude, and varies direction over time
    Also simulates gusts using a Weibull distribution
    """

    def __init__(self, **kwargs):
        """
        :param float average_wind_speed: At the supplied base altitude, what is the wind speed in m/s
        """

        # https://www.homerenergy.com/products/pro/docs/latest/weibull_k_value.html
        # 3 or 4 will be relatively steady, 1.5 will be gusty
        # This parameter is similar to the standard deviation / amplitude
        self.weibull_shape = 1
        self.interpolation_speed = 0.00005
        self.count = 30
        self.seeds = np.random.random(self.count) * self.count * 100

        # I have no idea what this does, but it is in the code for noise and it is an important parameter
        self.base = 0.9
        self.octaves = 50


        self.base_altitude = 10
        self.average_wind_speed = 5
        self.roughness = 1


        self.overwrite_defaults(**kwargs)

        self.altitude_randomized = 0
        # This value is the number of meters of altitude change that that is equivalent to one second passing
        # idk; this value has virtually no effect on our time scale
        self.time_from_altitude = 1000 / 10
        self.time_last_randomized = 0
        self.time_to_interpolate = self.get_random_interpolation_time()
        self.start_direction = 0
        self.wind_direction = self.start_direction
        self.target_direction = self.get_random_direction()

        # Have to manually calculate normalized perlin noise deviation
        self.std = self.determine_std()



    # region Statistics Stuff


    def get_normal_perlin(self, time):
        total = 0
        for i in range(self.count):
            total += pnoise1(self.seeds[i] + time, self.octaves, self.base)

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

    def determine_std(self):
        size = 10000


        ys = [[] for _ in range(self.count)]


        for index in range(len(ys)):
            for i in range(size):
                # Actually, I don't think time increment even needs to be included in tis
                ys[index].append(pnoise1(
                    self.seeds[index] + i * self.interpolation_speed, self.octaves))

        average_ys = []
        for i in range(len(ys[0])):
            total = 0
            for j in range(len(ys)):
                total += ys[j][i]

            average_ys.append(total / len(ys))


        return np.std(average_ys)

    # endregion


    def get_average_speed_altitude(
            self, altitude):
        if altitude == 0:
            print("Because this assumes the no slip condition, it does not work at altitude=0. Returning zero for wind speed")
            return 0
        # Roughness is z_0, or roughness length
        # For lake jackson, z_0 = 1
        # Relatively good explanation: https://wind-data.ch/tools/profile.php?lng=en
        # Review this equation more closely, it does not appear to be giving high enough increases
        return self.average_wind_speed * np.log(altitude / self.roughness) / np.log(
            self.base_altitude / self.roughness)


    def get_air_velocity(self, time, altitude=10):
        """
        Gets the air speed in all three dimensions at a point in time
        :param float base_altitude: The altitude AGL in meters where the average wind speed was recorded
        """

        wind_unit_vector = vector_from_angle(
            self.get_air_direction(time, altitude))

        value = self.get_normal_perlin(time * self.interpolation_speed)
        z_score = self.get_z_score(0, self.std, value)

        p = self.get_percentile_from_z(z_score)

        average_speed = self.get_average_speed_altitude(altitude)

        speed = self.lookup_weibull(p, average_speed)

        # TODO: Add some variability to the wind direction, particularly as altitude changes
        # In meters per second
        return wind_unit_vector * speed



    def get_random_interpolation_time(self):
        return np.random.normal(1800, 300)

    def get_random_direction(self):
        return np.random.uniform() * 2 * np.pi

    def calculate_average_direction(self, time, altitude):
        adjusted_time = time + (
            altitude - self.altitude_randomized) / self.time_from_altitude

        if adjusted_time > self.time_last_randomized + self.time_to_interpolate:
            self.target_direction = (
                self.wind_direction + (self.get_random_direction() - np.pi) * 0.5) % (2 * np.pi)
            if self.target_direction > 2 * np.pi:
                self.target_direction -= np.pi

            self.start_direction = self.wind_direction
            self.time_last_randomized = time
            self.altitude_randomized = altitude
            self.time_to_interpolate = self.get_random_interpolation_time()

        # This isn't exactly a linear interpolation since I am setting the start point each time. I think it is more of an ease-out interpolation; we will see how it looks
        self.wind_direction = interpolate_looped(
            adjusted_time, self.time_last_randomized, self.
            time_last_randomized + self.time_to_interpolate, self.
            start_direction, self.target_direction)


    def get_air_direction(self, time, altitude=10):
        # I am including altitude as an input, because as your altitude changes the wind direction will also change

        # The average direction is just a line moving from one randomly generated point on a circle to another randomly generated point on a circle. However, the direction has an additional perlin noise added to it, which makes it match the wobbliness of the real thing (visual inspection seems to say that direction variability is relatively independent of strength)

        # Maybe need some other variables for direction
        value = self.get_normal_perlin(time * self.interpolation_speed)
        z_score = self.get_z_score(0, self.std, value)

        noise_component = z_score * 1

        self.calculate_average_direction(time, altitude)

        return np.array([(self.wind_direction + noise_component) %
                         (2 * np.pi) - np.pi, np.pi / 2])




if __name__ == "__main__":
    w = Wind()

    print(w.get_average_speed_altitude(150))
