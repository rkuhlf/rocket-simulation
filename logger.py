# LOGGER CLASS
# The data storage is separated from the rocket class and integrated via the Simulation class
# There is a basic version that only stores a csv file, under Logger, and there a few additional print statements under FeedbackLogger

import numpy as np
import pandas as pd

# TODO: import the magnitude method from helpers instead of np.linalg.norm


class Logger:
    """
        Logs only the data.
        Should be hooked into the Simulation object, but a reference also has to be set in the Rocket object.
        
        Stores an array of objects, since I think that is slightly better than appending to a dataframe.
    """

    def __init__(self, rocket, to_record, target="output.csv"):
        self.rows = []
        # Use the actual rocket object to determine the data
        self.rocket = rocket
        self.splitting_arrays = False
        self.to_record = to_record
        self.current_row = {}
        self.target = target

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
        for key in self.to_record:
            self.add_items({key: self.rocket.__dict__[key].copy()})

        self.save_row()

    def save_to_csv(self):
        df = pd.DataFrame(self.rows)
        # Rather than using the index (0, 1, 2, 3, 4...), I will index the rows by the time the row is recorded at
        df.set_index('time', inplace=True)

        df.to_csv(self.full_path)

    def reset(self):
        """
            Reinitialize the Logger object
        """
        self.__init__(self.rocket, self.to_record)


class Feedback_Logger(Logger):
    """
        Logs the progress of the rocket simulation along with some print statements.
    """

    def __init__(self, rocket, to_record, target="output.csv"):
        print("Logger is prepared to launch rocket")
        self.p_turned = False
        self.p_thrusted = False
        self.should_print_top_speed = True

        super().__init__(rocket, to_record, target)

    def handle_frame(self):
        super().handle_frame()

        if not self.p_turned and self.rocket.turned:
            print('Reached the turning point at %.3s seconds with a height of %.5s meters' % (
                self.rocket.environment.time, self.rocket.position[2]))
            self.p_turned = True
            self.should_print_top_speed
            self.apogee = self.rocket.position[2]

        # TODO: I should probably print the maximum Mach and Max Q as well
        if self.should_print_top_speed:
            # If the acceleration is going against the velocity, it is decelerating
            if np.sign(self.rocket.velocity[2]) != np.sign(self.rocket.acceleration[2]):
                print("Top speed was", np.linalg.norm(
                    self.rocket.velocity), " at Mach", self.rocket.mach)

                self.should_print_top_speed = False


        if not self.p_thrusted and self.rocket.motor.finished_thrusting:
            print('Finished thrusting after %.3s seconds' %
                  self.rocket.environment.time)
            self.p_thrusted = True

        # If the position off of the base altitude is less than or equal to zero, we hit the ground
        if self.rocket.landed:
            print(
                "Rocket landed with a speed of %.3s m/s after %.4s seconds of flight time" %
                (np.linalg.norm(self.rocket.velocity),
                 self.rocket.environment.time))


    def save_to_csv(self):
        super().save_to_csv()

        print(f"Saved the trial to csv at {self.full_path}")
