# Class that all Monte Carlo style sims should inherit from

import os
from pathlib import Path
from time import time
from typing import Dict

from numpy.lib.function_base import append
from src.rocketparts.motor import Motor
from lib.simulation import Simulation
import pandas as pd
import numpy as np

from lib.data import force_save


def create_motors_from_directory(path, max_count=-1):
    filenames = os.listdir(path)

    if max_count == -1:
        max_count = len(filenames)

    print("Reading motor csv")
    motors = []

    for filename in filenames[:max_count]:
        try:
            print(f"Reading file {filename}")
            motor = Motor()
            motor.set_thrust_data_path(os.path.join(path, filename))

            motors.append(motor)
        except Exception as e:
            print("You probably are including an output.csv file in this directory. Skipping over the non-working file.")
        
    return motors


class MonteCarlo:
    def __init__(self, sims=[]):
        # You can start with an array of already run simulations, if you like
        self.sims = sims
        self.failed_sims = []

        self.characteristic_figures: list[Dict] = []
        self.important_data: list[pd.DataFrame] = []

    def simulate_randomized(self, count=20):
        start_time = time()
        for i in range(count):
            print(f"Simulating {i+1} out of {count}")

            sim = self.initialize_simulation()
            try:
                sim.automatically_save = False
                sim.logger.partial_debugging = False
            except AttributeError as e:
                print(f"Presumably because you are using somebody else's simulation class (like OR), this error was thrown {e}. It is being ignored.")

            try:
                # Use pass-by-reference
                self.run_simulation(sim)
                self.save_simulation(sim)
            except Exception as e:
                self.handle_failed_sim(sim, e)

            current_time = time()
            time_elapsed = current_time - start_time
            predicted_time = time_elapsed / (i + 1) * (count - (i + 1))
            print(f"Predicted time to completion: {predicted_time/60:.1f} minutes")

        self.finish_simulating()

    def handle_failed_sim(self, sim, e):
        self.failed_sims.append(sim)
        print(f"Simulation threw error {e}. Failed sims is now {len(self.failed_sims)}")

        

    def initialize_simulation(self) -> Simulation:
        raise NotImplementedError("This function must be overriden by children")

    def run_simulation(self, sim):
        # Little gap to indicate it is running
        print("")
        try:
            sim.run_simulation()
        except AttributeError as e:
            print("You probably have to override the run_simulation method in an implementation of the Monte Carlo class, since the sim you are using does not have such a method")
            raise
    
    def save_simulation(self, sim):
        self.sims.append(sim)

    def print_characteristic_figures(self, names=None):
        figures = self.characteristic_figures_dataframe

        if names is None:
            names = figures.columns
        
        for name in names:
            print(f"{name}: {np.average(figures[name]):.3e} +- {np.std(figures[name]):.2e} ")

    # TODO: replace with surefire save
    def save_important_data(self, target_folder: str, names: "list[str]"=None):
        """Saves the series of dataframes into the target folder. Each of the file names will be a number counting up from one. Only the columns with the requested names will be saved.
        """
        if len(self.important_data) == 0:
            print("No data has been stored yet")
            return

        if names is None:
            names = self.important_data[0].columns

        Path(target_folder).mkdir(parents=True, exist_ok=True)

        for index, df in enumerate(self.important_data):
            file_path = Path(target_folder, str(index + 1) + ".csv")
            df = df[names]
            df.to_csv(file_path)
    
    def save_characteristic_figures(self, target_path="./MonteCarloFlightSimulation"):
        """Saves a table with all of the overall outputs to the specified target_path"""
        force_save(self.characteristic_figures_dataframe, target_path, override=False)

    @property
    def characteristic_figures_dataframe(self):
        return pd.DataFrame(self.characteristic_figures)

    def finish_simulating(self):
        print(f"Ran {len(self.sims)} simulations, {len(self.failed_sims)} failed.")

