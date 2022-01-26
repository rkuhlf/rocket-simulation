import os

import numpy as np
from matplotlib import pyplot as plt



if __name__ == "__main__":
    import javaInitialization
    from Analysis.OpenRocketAnalysis.overrideCDListener import OverrideCDConstant

    import orhelper
    from orhelper import FlightDataType, FlightEvent
    from openRocketHelpers import getSimulationNames, most_updated_sim, new_or_instance
    from net.sf.openrocket.aerodynamics import FlightConditions

    with new_or_instance() as instance:
        
        orh = orhelper.Helper(instance)

        sim = most_updated_sim(orh)



        orh.run_simulation(sim, listeners=[OverrideCDConstant(sim, 1.8)])
        print(sim.getSimulatedData().getMaxAltitude())

