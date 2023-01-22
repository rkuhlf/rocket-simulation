import os
import matplotlib.pyplot as plt
from Analysis.monteCarloFlightPickMotor import MonteCarloFlightPickMotor
from src.rocketparts.motor import Motor

from lib.data import create_motors_from_directory
    

if __name__ == "__main__":
    motors = create_motors_from_directory("./Analysis/MotorMonteCarlo/")
    m = MonteCarloFlightPickMotor(motors)
    m.simulate_randomized(100)

    m.print_characteristic_figures()

