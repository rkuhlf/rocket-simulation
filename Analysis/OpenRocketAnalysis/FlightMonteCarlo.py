# Simulate randomized flights using OR stepper
# They are randomized for launch conditions and use a selected motor

import pandas as pd
from Analysis.monteCarlo import create_motors_from_directory
import numpy as np
from random import gauss
from Analysis.OpenRocketAnalysis.monteCarloFlightOR import MonteCarloFlightOR, MonteCarloFlightRandomMotorOR

from Analysis.OpenRocketAnalysis.openRocketHelpers import apogee, most_updated_sim, new_or_instance





if __name__ == '__main__':
    import javaInitialization
    import orhelper
    from orhelper import Helper

    with new_or_instance() as instance:
        orh = Helper(instance)
        motors = create_motors_from_directory("./Analysis/MotorMonteCarloShorterOx-Temporary/")

        df = pd.read_csv("./Data/Input/aerodynamicQualities.csv")
        m = MonteCarloFlightRandomMotorOR(orh, motors, drag_dataframe=df, dry_mass=50.2, dry_CG=3.404, ox_tank_front=1.600)

        
        m.simulate_randomized(100)

    m.print_characteristic_figures()

    root_folder = "./Analysis/Testing-Temporary"
    m.save_important_data(f"{root_folder}/MonteCarloFlightSimulations/")

    m.save_characteristic_figures(f"{root_folder}/MonteCarloFlightData/output.csv")


    m.plot_overview()
    m.plot_landing()
    m.plot_max_velocity()
    m.plot_max_mach()
    m.plot_impulse_correlation()

    # I think that the time values are off here for some reason
    m.plot_altitude_curves()
