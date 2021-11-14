# PROOF OF CONCEPT FOR THE WIND SIMULATION
# This file isn't really used anywhere else, but I am leaving it because it shows how I figured out the wind simulation that I am rolling with at the moment
# To be honest, I am pretty happy with the way the wind works at the moment
# I scaled the time increment and the weibull parameter and the octaves and base to match some second by second data from a calm day in Utah, but I think that it should scale pretty well just by adjusting the average wind speed


# Ranges from -1 to 1 I think
from noise import pnoise1
import matplotlib.pyplot as plt
import numpy as np
import sys
sys.path.append(".")

from Helpers.general import magnitude
from Data.Input.wind import Wind


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



if __name__ == "__main__":
    # show_normal_perlin_disparity()
    # show_CLT_of_perlin()

    show_wind_speed_over_time()
