# LOGGER CLASS
# The data storage is separated from the rocket class and integrated via the Simulation class
# There is a basic version that only stores a csv file, under Logger, and there a few additional print statements under FeedbackLogger

import numpy as np
import pandas as pd
from presetObject import PresetObject
from copy import deepcopy

# TODO: import the magnitude method from helpers instead of np.linalg.norm


class Logger(PresetObject):
    """
        Logs only the data.
        Should be hooked into the Simulation object, but a reference also has to be set in the Rocket object.
        
        Stores an array of objects, since I think that is slightly better than appending to a dataframe.
    """

    def __init__(self, logging_object, **kwargs):
        # Use the actual rocket object to determine the data
        self.logging_object = logging_object
        self.splitting_arrays = False
        self.to_record = []
        self.target = "output.csv"

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
        # print(self.splitting_arrays)
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
        for key in self.to_record:
            self.add_items({key: self.rocket.__dict__[key].copy()})

        self.save_row()

    def save_to_csv(self):
        df = pd.DataFrame(self.rows)
        # Rather than using the index (0, 1, 2, 3, 4...), I will index the rows by the time the row is recorded at
        df.set_index('time', inplace=True)

        df.to_csv(self.full_path)

        return df

    def reset(self):
        """
            Reinitialize the Logger object
        """
        self.__init__(self.logging_object, self.to_record)


class RocketLogger(Logger):
    """
        Logs the progress of the rocket simulation along with some print statements.
    """

    def print(self, statement):
        if self.verbose:
            print(statement)

    def __init__(self, rocket, **kwargs):
        self.verbose = True

        # We have some slightly different defaults in this child class
        self.to_record = ['position', 'velocity', 'acceleration', 'rotation', 'angular_velocity',
        'angular_acceleration']
        

        super().__init__(rocket, **kwargs)

        self.printed_rail_stats = False
        self.printed_thrusted = False
        self.turned = False

        self.print("Logger is prepared to launch rocket")

    # Make it so that you can access it via either the logging_object or rocket property
    # TODO: do the same for Motor
    @property
    def rocket(self):
        return self.logging_object

    @rocket.setter
    def rocket(self, r):
        self.logging_object = r

    def handle_frame(self):
        super().handle_frame()

        if not self.printed_rail_stats and self.rocket.position[2] > self.rocket.environment.rail_length:
            self.printed_rail_stats = True

            self.print(f"Off the rail, the rocket has {self.rocket.gees} gees")

        if self.rocket.descending and not self.turned:
            self.print('Reached the turning point at %.3s seconds with a height of %.5s meters' % (
                self.rocket.environment.time, self.rocket.position[2]))
            self.turned = True
            self.print('The highest velocity during ascent was %.1f m/s, and the highest mach number was %.2f' % (
                self.rocket.simulation.max_velocity, self.rocket.simulation.max_mach))


        if not self.printed_thrusted and self.rocket.motor.finished_thrusting:
            self.print('Finished thrusting after %.3s seconds' % self.rocket.environment.time)
            self.printed_thrusted = True

        if self.rocket.landed:
            self.print(
                "Rocket landed with a speed of %.3s m/s after %.4s seconds of flight time" %
                (np.linalg.norm(self.rocket.velocity),
                 self.rocket.environment.time))


    def save_to_csv(self):
        self.print(super().save_to_csv())

        self.print(f"Saved the trial to csv at {self.full_path}")
