# LOGGER CLASS
# The data storage is separated from the rocket class and integrated via the Simulation class
# There is a basic version that only stores a csv file, under Logger, and there a few additional print statements under FeedbackLogger

import numpy as np
import pandas as pd
import string
import random
from copy import deepcopy, copy

from presetObject import PresetObject
from Helpers.data import nested_dictionary_lookup, force_save
from Helpers.general import magnitude

# TODO: I need to refactor the to_record feature to allow a different name for the columns
# I can probably just use a separate array

class Logger(PresetObject):
    """
        Logs only the data.
        Should be hooked into the Simulation object, but a reference also has to be set in the Rocket object.
        
        Stores an array of objects, since I think that is slightly better than appending to a dataframe.
    """

    def __init__(self, logging_object, **kwargs):
        # Use the actual rocket object to determine the data
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

    def save_to_csv(self):
        df = self.get_dataframe()
        force_save(df, self.full_path)
        
        

    def reset(self):
        """
            Reinitialize the Logger object
        """
        self.__init__(self.logging_object, self.to_record)

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
        print(f"We are {self.simulation.environment.time} seconds through the simulation")
        self.last_debugged += self.debug_every

    def handle_frame(self):

        if self.partial_debugging and self.simulation.environment.time > self.last_debugged + self.debug_every:
            self.display_partial_data()


        return super().handle_frame()

    
    def save_to_csv(self):
        self.print(super().save_to_csv())

        self.print(f"Saved the trial to csv at {self.full_path}")


class RocketLogger(FeedbackLogger):
    """
        Logs the progress of the rocket simulation along with some print statements.
    """

    def __init__(self, rocket, **kwargs):
        # You need to make sure the parent's override doesn't override the self values we have already established, so we set our defaults after this
        super().__init__(rocket)

        self.to_record = ['position', 'velocity', 'acceleration', 'rotation', 'angular_velocity',
        'angular_acceleration']


        self.debug_every = 20 # seconds

        self.overwrite_defaults(**kwargs)

        self.printed_rail_stats = False
        self.printed_thrusted = False
        self.turned = False



    # Make it so that you can access it via either the logging_object or rocket property
    @property
    def rocket(self):
        return self.logging_object

    @rocket.setter
    def rocket(self, r):
        self.logging_object = r

    def display_partial_data(self):
        super().display_partial_data()

        if self.rocket.ascending:
            print(f"Rocket is ascending at {self.rocket.velocity[2]} m/s")
        else:
            print(f"Rocket is descending at {abs(self.rocket.velocity[2])} m/s", end="")
            if self.rocket.parachute_deployed:
                print(" under parachutes")
            else:
                print()

        print(f"It is currently {self.rocket.position[2]} meters in the air")


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
                self.simulation.max_velocity, self.simulation.max_mach))


        if not self.printed_thrusted and self.rocket.motor.finished_thrusting:
            self.print('Finished thrusting after %.3s seconds' % self.rocket.environment.time)
            self.printed_thrusted = True

        if self.rocket.landed:
            self.print(
                "Rocket landed with a speed of %.3s m/s after %.4s seconds of flight time" %
                (magnitude(self.rocket.velocity),
                 self.rocket.environment.time))


class MotorLogger(FeedbackLogger):
    """
        Logs the progress of the custom motor simulation along with some print statements.
    """

    def __init__(self, motor, **kwargs):
        # You need to make sure the parent's override doesn't override the self values we have already established
        super().__init__(motor)

        # TODO: it would be nice to have the average molar mass of the products displayed
        self.to_record = ["thrust", "combustion_chamber.pressure", "ox_tank.pressure", "combustion_chamber.temperature", "ox_tank.temperature", "combustion_chamber.fuel_grain.port_diameter", "OF", "combustion_chamber.cstar", "specific_impulse", "fuel_flow", "ox_flow", "mass_flow", "mass_flow_out", "combustion_chamber.ideal_gas_constant", "propellant_CG", "propellant_mass"]

        self.debug_every = 2 # seconds

        self.overwrite_defaults(**kwargs)

        self.printed_pressurized = False
        # Print every time it switches
        self.overexpanded = True

        self.initial_pressure = self.motor.ox_tank.pressure

    @property
    def motor(self):
        return self.logging_object

    @motor.setter
    def motor(self, m):
        self.logging_object = m

    def display_partial_data(self):
        print(f"Ox Tank pressure {self.motor.ox_tank.pressure} Pascals")
        print(f"Chamber pressure {self.motor.combustion_chamber.pressure} Pascals")

        return super().display_partial_data()
        
    def handle_frame(self):
        super().handle_frame()

        if not self.printed_pressurized and not self.motor.combustion_chamber.pressurizing:
            print(f"Motor finished pressurizing to {self.motor.combustion_chamber.pressure} Pa at {self.motor.environment.time}")
            self.printed_pressurized = True


    def save_to_csv(self):
        # Give some information about how we are looking a the end of the burn

        print(f"The motor finished with {self.motor.combustion_chamber.fuel_grain.fuel_mass} kg of fuel and {self.motor.combustion_chamber.fuel_grain.outer_radius - self.motor.combustion_chamber.fuel_grain.port_radius} meters left")

        print(f"There is {self.motor.ox_tank.ox_mass} kg of oxidizer left and there is still a pressure difference of {self.motor.ox_tank.pressure - self.motor.combustion_chamber.pressure} Pa")

        return super().save_to_csv()