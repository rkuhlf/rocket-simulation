# LOGGER CLASS
# The data storage is separated from the rocket class and integrated via the Simulation class
# There is a basic version that only stores a csv file, under Logger, and there a few additional print statements under FeedbackLogger

import numpy as np
import pandas as pd

from copy import deepcopy, copy

from lib.presetObject import PresetObject
from lib.data import nested_dictionary_lookup, force_save
from lib.general import magnitude
from lib.logging.logger_features import Feature, feature_time


class Logger(PresetObject):
    """
        Logs only the src.data.
        Should be hooked into the Simulation object, but a reference also has to be set in the Rocket object.
        
        Stores an array of objects, since I think that is slightly better than appending to a dataframe.
    """

    def __init__(self, simulation, **kwargs):
        # The logger has a reference to the simulation, since that is where it gets the data from.
        # However, the simulation controls the logger in pretty much all other ways.
        self.simulation = simulation
        self.splitting_arrays = True
        self.features: set[Feature] = set([feature_time])
        # This should probably be overridden in custom subclasses, like one for rocket and motor.
        self.full_path = "./output.csv"

        super().overwrite_defaults(**kwargs)

        self.rows = []
        self.current_row = {}

    def copy(self):
        # Hopefully this is being called from the simulation and the rocket I am about to make gets overridden (This comment exists from a time when I was working on the Goddard Problem Optimization)
        return deepcopy(self)

    def add_items(self, data):
        """
            Update the current row of data, which should eventually be saved by save_row
        """
        if self.splitting_arrays:
            k = list(data.keys())[0]
            v = list(data.values())[0]


            if isinstance(v, np.ndarray):
                if len(v) != 0:
                    data = {}
                    index = 1
                    for item in v:
                        data[k + str(index)] = item

                        index += 1

        self.current_row.update(data)

    def save_row(self):
        self.rows.append(self.current_row)
        self.current_row = {}

    def handle_frame(self):
        """
            This is the only thing that needs to be run for the logger to work in the Simulation class (also the save_to_csv)
        """
        for feature in self.features:
            try:
                value = copy(nested_dictionary_lookup(self.simulation, feature.path))
            except Exception as e:
                value = None
                print(f"Could not find value for {feature}")
                print(e)
                
            self.add_items({feature.get_label(): value})

        self.save_row()

    def get_dataframe(self):
        df = pd.DataFrame(self.rows)

        try:
            # Rather than using the index (0, 1, 2, 3, 4...), I will index the rows by the time the row is recorded at
            df.set_index(feature_time.get_label(), inplace=True)
        except KeyError as e:
            print("Attempted to create dataframe, but there was no time index. Likely, the simulation did not make it past one frame, and no time was ever logged.")
        
        return df

    def save_to_csv(self):
        df = self.get_dataframe()
        force_save(df, self.full_path)
        
        

    def reset(self):
        """
            Reinitialize the Logger object
        """
        self.__init__(self.simulation, self.features)

class FeedbackLogger(Logger):
    def print(self, statement):
        if self.verbose:
            print(statement)

    def __init__(self, logging_object, **kwargs):
        self.verbose = True

        super().__init__(logging_object)

        self.partial_debugging = True
        self.debug_every = 10 # seconds
        self.last_debugged = 0

        self.overwrite_defaults(**kwargs)

        self.print("Logger is prepared to run simulation")

    def display_partial_data(self):
        print(f"We are {self.simulation.time} seconds through the simulation")
        self.last_debugged += self.debug_every

    def handle_frame(self):
        if self.partial_debugging and self.simulation.time > self.last_debugged + self.debug_every:
            self.display_partial_data()


        return super().handle_frame()

    
    def save_to_csv(self):
        self.print(super().save_to_csv())

        self.print(f"Saved the trial to csv at {self.full_path}")

