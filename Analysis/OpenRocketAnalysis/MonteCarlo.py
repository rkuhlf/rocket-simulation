import os
import numpy as np
import orhelper
from random import gauss
import math

from Analysis.OpenRocketAnalysis.openRocketHelpers import apogee, most_updated_sim, new_or_instance


class RandomizedSimulations(list):
    "A list of randomized simulations with ability to run simulations and populate itself"

    def __init__(self, or_instance):
        self.apogees = []
        self.or_instance = or_instance

    def add_simulations(self, num):
        # Load the document and get simulation
        orh = orhelper.Helper(self.or_instance)
        sim = most_updated_sim(orh)
        print(sim.getName())

        # Randomize various parameters
        opts = sim.getOptions()
        rocket = opts.getRocket()

        # Run num simulations and add to self
        for p in range(num):
            print('Running simulation ', p)

            # opts.setLaunchRodAngle(math.radians(gauss(45, 5)))  # 45 +- 5 deg in direction
            # opts.setLaunchRodDirection(math.radians(gauss(0, 5)))  # 0 +- 5 deg in direction
            opts.setWindSpeedAverage(gauss(15, 5))  # 15 +- 5 m/s in wind

            orh.run_simulation(sim)
            self.append(0)
            self.apogees.append(apogee(sim))
        print(self.apogees)

    def print_stats(self):
        print(
            'Rocket flew %3.2f m +- %3.2f m up and landed some number of meters from launch site. Based on %i simulations.' % \
            (np.mean(self.apogees), np.std(self.apogees), len(self)))



if __name__ == '__main__':
    with new_or_instance() as instance:
        points = RandomizedSimulations(instance)
        points.add_simulations(20)
        # points.add_simulations(20)
        points.print_stats()