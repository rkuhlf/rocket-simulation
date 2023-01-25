# PROOF OF CONCEPT FOR THE WIND SIMULATION
# This file isn't really used anywhere else, but I am leaving it because it shows how I figured out the wind simulation that I am rolling with at the moment
# To be honest, I am pretty happy with the way the wind works at the moment
# I scaled the time increment and the weibull parameter and the octaves and base to match some second by second data from a calm day in Utah, but I think that it should scale pretty well just by adjusting the average wind speed
# I did the same thing for the direction when you are standing still, but I think that one is basically a guessing game for a rocket that is rapidly increasing in altitude


# Ranges from -1 to 1 I think
from noise import pnoise1
import matplotlib.pyplot as plt
import numpy as np


from lib.general import magnitude
from src.data.input.wind import Wind
from src.data.input.Wind.whiteSandsModels import speed_at_altitude


def show_normal_perlin_disparity():
    # As you can see, it is not the same

    x = []
    y = []
    for i in range(10000):
        x.append(0.1 + i * 0.01)
        y.append(pnoise1(0.1 + i * 0.01, 4))

    # plt.scatter(x, y)

    std = np.std(y)

    normal_distribution = np.random.normal(loc=0, scale=std, size=10000)

    bins = 20
    plt.hist(y, bins, alpha=0.5, label='x')
    plt.hist(normal_distribution, bins, alpha=0.5, label='y')
    plt.legend(loc='upper right')

    plt.show()


def show_CLT_of_perlin():
    # Ranges from -1 to 1 I think
    size = 10000

    x = []
    for i in range(size):
        x.append(i * 0.01)

    ys = [[] for _ in range(30)]


    for index in range(len(ys)):
        offset = np.random.random() * 100
        for i in range(size):
            ys[index].append(pnoise1(offset + i * 0.01, 4))

    average_ys = []
    for i in range(len(ys[0])):
        total = 0
        for j in range(len(ys)):
            total += ys[j][i]

        average_ys.append(total / len(ys))

    plt.scatter(x=x, y=average_ys)
    plt.show()

    std = np.std(average_ys)

    normal_distribution = np.random.normal(loc=0, scale=std, size=size)

    bins = np.linspace(-4 * std, 4 * std, 30)

    plt.hist(average_ys, bins, alpha=0.5, label='x')
    plt.hist(normal_distribution, bins, alpha=0.5, label='y')
    plt.legend(loc='upper right')

    plt.show()


def show_wind_speed_over_time():
    w = Wind()

    inputs = np.linspace(0, 100, 100)
    outputs = []

    for i in inputs:
        outputs.append(magnitude(w.get_air_speed(i, average_wind_speed=5)))

    plt.plot(inputs, outputs)

    plt.show()

def show_wind_speed_at_altitude_versus_WSMR():
    """
    Compare two models of wind speed at altitude.
    The logarithm one is for a lower part of the atmosphere based on the roughness of the ground
    The thing it is comparing to is what the WSMR wind table says that was given to us
    """

    w = Wind(average_wind_speed=3.08)

    base_altitude = 10 # meters
    max_altitude = 15000

    altitudes = np.linspace(base_altitude, max_altitude, 100)
    avg_speeds = []

    for alt in altitudes:
        # Base altitude and average wind speed are based off of WSMR data
        avg_speeds.append(w.get_average_speed_altitude(alt))

    plt.plot(altitudes, avg_speeds)


    w.get_average_speed_altitude = speed_at_altitude
    avg_speeds = []
    for alt in altitudes:
        # Base altitude and average wind speed are based off of WSMR data
        avg_speeds.append(w.get_average_speed_altitude(alt))

    plt.plot(altitudes, avg_speeds)

    plt.show()


def show_wind_direction():
    w = Wind()

    points = 500

    times = np.linspace(0, 100, points)
    directions_no_alt = []

    for time in times:
        # Base altitude and average wind speed are based off of WSMR data
        directions_no_alt.append(w.get_air_direction(time)[0])

    

    altitudes = np.linspace(1300, 15000, points)

    directions_alt = []

    for (time, alt) in zip(times, altitudes):
        # Base altitude and average wind speed are based off of WSMR data
        directions_alt.append(w.get_air_direction(time, alt)[0])


    fig, (ax1, ax2) = plt.subplots(2)
    ax1.scatter(times, directions_no_alt, s=1)
    ax2.scatter(times, directions_alt, s=1)

    plt.show()



if __name__ == "__main__":
    # show_normal_perlin_disparity()
    # show_CLT_of_perlin()

    # show_wind_speed_over_time()

    show_wind_speed_at_altitude_versus_WSMR()
    # show_wind_direction()
