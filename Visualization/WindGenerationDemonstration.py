# PROOF OF CONCEPT FOR THE WIND SIMULATION
# This file isn't really used anywhere else, but I am leaving it because it shows how I figured out the wind simulation that I am rolling with at the moment
# MAJOR DISCLAIMER: This isn't a simulation based on real research. I found out that wind follows a weibull distribution, so I wrote a rolling perlin noise generation that maps to a weibull
# The time-scale is probably totally off, so it shouldn't be used in place of an actual wind table, and I would like to replace it


# Ranges from -1 to 1 I think
from noise import pnoise1
import matplotlib.pyplot as plt
import numpy as np



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



if __name__ == "__main__":
    # show_normal_perlin_disparity()
    show_CLT_of_perlin()