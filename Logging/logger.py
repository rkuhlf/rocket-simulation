# LOGGER CLASS
# The data storage is separated from the rocket class and integrated via the Simulation class
# There is a basic version that only stores a csv file, under Logger, and there a few additional print statements under FeedbackLogger

import numpy as np
import pandas as pd
import string
import random
from copy import deepcopy, copy
from Logging.verbosity import Verbosity

from presetObject import PresetObject
from Helpers.data import nested_dictionary_lookup, force_save
from Helpers.general import magnitude


# TODO: refactor Verbosity to work with all of the classes. It should just be a superclass of almost everything

# TODO: Add a bunch of self.print statements to indicate what is happening

class Logger(PresetObject):
    """
        Logs only the data.
        Should be hooked into the Simulation object, but a reference also has to be set in the Rocket object.
        
        Stores an array of objects, since I think that is slightly better than appending to a dataframe.
    """

    def __init__(self, logging_object, **kwargs):
        """The logging_object is probably the simulation from which data should be stored"""

        self.verbosity = Verbosity.NORMAL

        self.logging_object = logging_object
        self.splitting_arrays = True
        self.to_record = []
        self.target = "output.csv"

        # This isn't necessary for every type of logger, but it is overriden in the base simulation class
        self.simulation = None

        super().overwrite_defaults(**kwargs)

        self.rows = []
        self.current_row = {}

    def copy(self):
        # Hopefully this is being called from the simulation and the rocket I am about to make gets overridden (This comment exists from a time when I was working on the Goddard Problem Optimization)
        return deepcopy(self)

    @property
    def full_path(self):
        return "Data/Output/" + self.target

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
        self.add_items({'time': self.simulation.environment.time})

        for key in self.to_record:
            value = copy(nested_dictionary_lookup(self.logging_object, key))
            self.add_items({key: value})

        self.save_row()

    def get_dataframe(self):
        df = pd.DataFrame(self.rows)

        try:
            # Rather than using the index (0, 1, 2, 3, 4...), I will index the rows by the time the row is recorded at
            df.set_index('time', inplace=True)
        except KeyError as e:
            print("Attempted to create dataframe, but there was no time index. Likely, the simulation did not make it past one frame, and no time was ever logged.")
        
        return df

    def save_to_csv(self, target=None):
        if target is None:
            target = self.full_path
        
        df = self.get_dataframe()
        self.print_debug(df)

        force_save(df, target)
        self.print(f"Saved the trial to csv at {self.full_path}")

        return df

        

    def reset(self):
        """
            Reinitialize the Logger object
        """
        self.__init__(self.logging_object, self.to_record)

    
    def print(self, statement, level=Verbosity.NORMAL):
        if self.verbosity >= level:
            print(statement)
    
    def print_error(self, statement):
        self.print(statement, Verbosity.ERROR)
    
    def print_debug(self, statement):
        self.print(statement, Verbosity.DEBUGGING)

# TODO: Write a bunch of mapping functions as static functions on each of the loggers. There should be one or two for OpenRocket and one for RASAero. I need to come up with a default list that has all of the symbol names that I want to have.

# Static properties that contain the string translation for each name
# See if you can make abstract static properties?
# Then I just need to write some classes for OR, rocksim, and RASAero. I also need a branch for flight and motor
# I will have a CustomLogger class
# FlightLogger will inherit both

# The I will turn the feedback logger into the custom logger
# I need something where you are required to override every single variable