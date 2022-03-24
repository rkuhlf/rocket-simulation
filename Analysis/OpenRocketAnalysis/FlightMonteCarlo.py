# Simulate randomized flights using OR stepper
# They are randomized for launch conditions and use a selected motor
# I think I should be more careful with this. All of the units have to be base metric for this to work

import pandas as pd
import javaInitialization
from Analysis.OpenRocketAnalysis.monteCarloFlightOR import MonteCarloFlightOR, MonteCarloFlightRandomMotorOR
from Analysis.monteCarlo import create_motors_from_directory

from Analysis.OpenRocketAnalysis.openRocketHelpers import apogee, most_updated_sim, new_or_instance


if __name__ == '__main__':
    import orhelper
    from orhelper import Helper

    with new_or_instance() as instance:
        orh = Helper(instance)
        motors = create_motors_from_directory("./Analysis/MotorMonteCarloUpdatedDimensions/", 100)

        df = pd.read_csv("./Data/Input/shorterOxTankAerodynamics.csv")
        m = MonteCarloFlightRandomMotorOR(orh, motors, drag_dataframe=df, dry_mass=49.5, dry_CG=3.43, ox_tank_front=1.625)

        
        m.simulate_randomized(100)

    m.print_characteristic_figures()

    root_folder = "./Analysis/MonteCarloPreDatcom"
    m.save_important_data(f"{root_folder}/MonteCarloFlightSimulations/")

    m.save_characteristic_figures(f"{root_folder}/MonteCarloFlightData/output.csv")


    m.plot_overview()
    m.plot_landing()
    m.plot_max_velocity()
    m.plot_max_mach()
    m.plot_impulse_correlation()

    m.plot_altitude_curves()
