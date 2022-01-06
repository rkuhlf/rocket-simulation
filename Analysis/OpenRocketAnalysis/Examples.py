import os

import numpy as np
from matplotlib import pyplot as plt

import orhelper
from orhelper import FlightDataType, FlightEvent
from openRocketHelpers import getSimulationNames, most_updated_sim, new_or_instance

with new_or_instance() as instance:
    orh = orhelper.Helper(instance)


    # Load document, run simulation and get data and events

    # doc = orh.load_doc(os.path.join('examples', 'simple.ork'))
    sim = most_updated_sim(orh)
    orh.run_simulation(sim)
    print(dir(sim))

