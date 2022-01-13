

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
        motors = create_motors_from_directory("./Analysis/MotorMonteCarlo-Temporary/")

        m = MonteCarloFlightRandomMotorOR(orh, motors)

        
        m.simulate_randomized(100)

    m.print_characteristic_figures()

    m.plot_overview()
    m.plot_landing()
    m.plot_max_velocity()
    m.plot_max_mach()
    m.plot_impulse_correlation()

    m.plot_altitude_curves()

    m.save_characteristic_figures("./Analysis/MonteCarloFlightData/output.csv")
