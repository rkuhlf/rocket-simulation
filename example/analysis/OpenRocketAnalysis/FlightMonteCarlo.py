# Simulate randomized flights using OR stepper
# They are randomized for launch conditions and use a selected motor
# I think I should be more careful with this. All of the units have to be base metric for this to work

import pandas as pd
from lib.data import read_sims
import javaInitialization
from Analysis.OpenRocketAnalysis.monteCarloFlightOR import MonteCarloFlightOR, MonteCarloFlightRandomMotorOR
from Analysis.monteCarlo import create_motors_from_directory

from Analysis.OpenRocketAnalysis.openRockethelpers import apogee, most_updated_sim, new_or_instance
from Analysis.MonteCarloFlightData.AnalyzeMonteCarloFlight import display_altitude_lines, display_apogee_distribution, display_landing, display_max_mach_distribution, display_max_velocity, display_total_impulse_effect

def run_simulation():
    import orhelper
    from orhelper import Helper

    with new_or_instance() as instance:
        orh = Helper(instance)
        motors = create_motors_from_directory("Analysis/MotorMonteCarloUpdatedDimensions2/", 100)

        df = pd.read_csv("./Data/Input/aerodynamicQualities.csv")

        m = MonteCarloFlightRandomMotorOR(orh, motors, drag_dataframe=df, dry_mass=45.071, dry_CG=3.3274, ox_tank_front=1.625)

        
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

def display_overview():
    df = pd.read_csv("Analysis\MonteCarloPreDatcom\MonteCarloFlightData\output.csv")

    # display_apogee_distribution(df)
    # display_landing(df)
    # display_max_velocity(df)
    # display_max_mach_distribution(df)
    # display_total_impulse_effect(df)

    sims = read_sims("./Analysis/MonteCarloPreDatcom/MonteCarloFlightSimulations")

    display_altitude_lines(sims)


if __name__ == '__main__':
    # run_simulation()
    display_overview()

    pass