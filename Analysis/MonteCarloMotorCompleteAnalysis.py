# Look at the distribution from randomizing every single input into the motor

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# The defaults for this class were created specifically for this, so they work perfectly
from monteCarloMotor import MonteCarloMotor

# FIXME: debug the NaN values that occasionally come up

if __name__ == "__main__":
    m = MonteCarloMotor()
    m.simulate_randomized(100)

    m.print_characteristic_figures()

    # time is logged automatically because it is the index
    # "thrust", "combustion_chamber.pressure", "ox_tank.pressure", "combustion_chamber.temperature", "ox_tank.temperature", "combustion_chamber.fuel_grain.port_diameter", "OF", "combustion_chamber.cstar", "specific_impulse", "fuel_flow", "ox_flow", "mass_flow", "mass_flow_out", "combustion_chamber.ideal_gas_constant"
    # m.save_important_data("./Analysis/MotorMonteCarlo1-Temporary/", names=["thrust"])

    m.plot_overview()
    m.plot_efficiency()
    m.plot_average_thrust()
    m.plot_thrust_curves()

    m.plot_cstar_efficiency_correlation()
    m.plot_OF_correlation()
    m.plot_regression_correlation()