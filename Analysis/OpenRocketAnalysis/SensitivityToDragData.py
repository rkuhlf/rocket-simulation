import os

import numpy as np
from matplotlib import pyplot as plt

import orhelper
from orhelper import FlightDataType, FlightEvent
from openRocketHelpers import getSimulationNames, most_updated_sim, new_or_instance

with new_or_instance() as instance:
    orh = orhelper.Helper(instance)

    sim = most_updated_sim(orh)
    orh.run_simulation(sim)

