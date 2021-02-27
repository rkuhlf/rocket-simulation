from timeit import timeit
import importlib
import Helpers.variables
from Helpers.timing import Timer
from Helpers.thrust import get_thrust
from Helpers.dragForce import *
from Helpers.gravity import *
import pandas as pd
from random import random

# the simulation runs through 12,000 steps

# One Trial: 5.7
# With Pandas: 5.9


def test_overall_speed():
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


# 10,000 iterations takes 3 seconds
# looking up the drag is still the most inefficient part
def test_drag():  # this really slows it down
    iters = 10000
    with Timer():
        for i in range(iters):
            Helpers.variables.position[1] = random() * 3000
            get_drag_force(random() * 3, random() * 1.2 + 0.2)


# The fetching density makes up the vast majority of the time spent calculating drag
# Probably just cache the most recent index, then start checking from there to see where the next altitude is


def test_density():  # this really slows it down
    iters = 10000
    end = 13
    with Timer():
        for i in range(iters):
            get_air_density(i * end / iters)



# This is definitely fast enough
def test_gravity():
    iters = 10000
    with Timer():
        for i in range(iters):
            Helpers.variables.position[1] = random() * 3000
            get_gravitational_attraction()


if __name__ == "__main__":
    test_overall_speed()
    # test_density()
    # test_gravity()
