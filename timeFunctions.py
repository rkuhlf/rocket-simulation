# Functions to determine how fast each of the parts of the simulation are

from timeit import timeit
import importlib
from Helpers.timing import Timer
import pandas as pd
from random import random
from environment import Environment
from rocket import Rocket
from motor import Motor


# One Trial: 5.7
# With Pandas: 5.9

# TODO: Now that I am working on extremely small time increments, it is probably worthwhile to do another efficiency study


def test_overall_speed():
    # TODO: Make this work with the new implementations

    with Timer():
        # this one isn't going to work for multiple trials
        # I think if you just reset the variables.py it might work
        importlib.import_module('rocket')


# For 10,000 steps: 0.0173
# For 100 steps: 0.0044
def test_thrust():  # this one is fast
    data = pd.read_csv("data/Input/thrustCurve.csv")
    end = data["time"].max()
    steps_to_take = 10000
    with Timer():
        for i in range(steps_to_take):
            get_thrust(i * end / steps_to_take)


# 10,000 iterations takes 3 seconds with lookup and 0.7399 when density is fitted to a curve. That's fast enough # TODO: It kinda needs to be faster now
def test_drag():
    iters = 10000
    e = Environment()
    m = Motor()
    r = Rocket(environment=e, motor=m)


    with Timer():
        for i in range(iters):
            r.position[1] = random() * 3000
            r.get_drag_force(random() * 3, random() * 1.2 + 0.2)


# With a funciton, it's 0.0112
# With a lookup # TODO: Calculate
def test_density():
    iters = 10000
    end = 13
    e = Environment()
    with Timer():
        for i in range(iters):
            e.get_air_density(i * end / iters)


# This is definitely fast enough
def test_gravity():
    iters = 10000
    with Timer():
        for i in range(iters):
            Helpers.variables.position[1] = random() * 3000
            get_gravitational_attraction()


if __name__ == "__main__":
    # test_overall_speed()
    # test_density()
    test_drag()
    # test_gravity()
