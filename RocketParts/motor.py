# MOTOR CLASS
# Started off as just a place to store the code to get a thrust curve up and running for a rocket class
# Eventually, I need to integrate all of the inherited functions from the base motor class so that they actually work in the custom motor
# That is a secondary priority however, since the evolution of chamber pressure is just incorrect at the moment

import pandas as pd

import sys
sys.path.append(".")

from RocketParts.massObject import MassObject
from Helpers.general import interpolate
from environment import Environment

# Imports for defaults
from RocketParts.Motor.oxTank import OxTank
from RocketParts.Motor.grain import Grain
from RocketParts.Motor.injector import Injector
from RocketParts.Motor.combustionChamber import CombustionChamber
from RocketParts.Motor.nozzle import Nozzle
from logger import MotorLogger



class Motor(MassObject):
    # TODO: rewrite so I can have some variable names that actually make sense. Right now, .total_impulse just gives you a value that is literally not the total impulse

    def __init__(self, **kwargs):
        super().__init__(**kwargs)        
        self.environment = Environment()

        # Mass including the propellant
        self.front = 3 # m
        self.center_of_gravity = 2 # m
        self.mass = 105 # kg
        self.propellant_mass = 105 # kg
        self.thrust_curve = "Data/Input/currentGoddard.csv"

        self.thrust_multiplier = 1
        self.time_multiplier = 1


        super().overwrite_defaults(**kwargs)

        self.set_thrust_data_path(self.thrust_curve)

        self.finished_thrusting = False

    def set_thrust_data_path(self, path):
        self.thrust_curve = path
        dataframe = pd.read_csv(path)
        self.set_thrust_data(dataframe)

    def set_thrust_data(self, dataframe):
        self.thrust_curve = None
        self.thrust_data = dataframe

        total_thrust = 0
        # this is close but not exactly correct (actually it's exactly what the data indicates, but not the experimental value) - I changed the first point of the base data to better match the experimental
        for index, row in self.thrust_data.iterrows():
            if index == 0:
                continue

            p_row = self.thrust_data.iloc[index - 1]
            change_in_time = row["time"] - p_row["time"]
            average_thrust = (row["thrust"] + p_row["thrust"]) / 2
            total_thrust += change_in_time * average_thrust

        self.total_impulse = total_thrust

        self.burn_time = self.thrust_data.iloc[-1]["time"]

        self.mass_per_thrust = self.propellant_mass / total_thrust
        # print(self.mass_per_thrust)


    def calculate_thrust(self, current_time):
        if self.finished_thrusting:
            return 0

        # The longer we want the burn time, the more we want to shrink the lookup time
        current_time /= self.time_multiplier
        # this isn't very efficient, but there are barely 100 data points so it should be instant
        try:
            previous_thrust = self.thrust_data[self.thrust_data["time"] <= current_time]

            next_thrust = self.thrust_data[self.thrust_data["time"] >= current_time]

            previous_thrust = previous_thrust.iloc[-1]
            next_thrust = next_thrust.iloc[0]

            thrust = self.thrust_multiplier * interpolate(
                current_time, previous_thrust["time"],
                next_thrust["time"],
                previous_thrust["thrust"],
                next_thrust["thrust"])


            new_mass = self.total_mass - self.thrust_to_mass(thrust, self.environment.time_increment)
            # This section is slightly more complicated with a more complicated motor
            self.set_mass_constant(new_mass)

            return thrust
        except IndexError as e:
            self.finished_thrusting = True
            return 0

    def thrust_to_mass(self, thrust, time):
        return thrust * self.mass_per_thrust * time / (self.thrust_multiplier * self.time_multiplier)

    def get_total_impulse(self):
        # This has got to be the most confusing way possible to do this. There is a total impulse that is te total impulse of the data without multipliers
        return self.time_multiplier * self.thrust_multiplier * self.total_impulse

    def get_average_thrust(self):
        return self.get_total_impulse() / self.get_burn_time()

    def get_burn_time(self):
        return self.time_multiplier * self.burn_time

    def specific_impulse(self):
        return 1 / (self.mass_per_thrust * 9.81)

    #region SCALING
    def scale_thrust(self, multiplier):
        self.thrust_multiplier *= multiplier

    def reset_thrust_scale(self):
        self.thrust_multiplier = 1

    def scale_time(self, multiplier):
        self.time_multiplier *= multiplier

    def reset_time_scale(self):
        self.time_multiplier = 1

    #endregion

class CustomMotor(Motor):
    def __init__(self, **kwargs):
        self.thrust_multiplier = 1
        self.time_multiplier = 1
        self.finished_thrusting = False

        self.ox_tank = OxTank()
        self.injector = Injector()
        self.combustion_chamber = CombustionChamber()
        self.nozzle = Nozzle()

        self.data_path = "./Data/Input/CombustionLookup.csv"
        self.data = pd.read_csv(self.data_path)

        self.logger = MotorLogger(self)

        super().__init__()
        self.overwrite_defaults(**kwargs)

        # This is only defined as a cached variable to provide easier graphing
        self.thrust = 0
        self.OF = 0

    def update_values_from_CEA(self, chamber_pressure, OF):
        """
        This is doing a look up for the chamber pressure in Pascals.
        It will always round up
        """
        # I don't really know what to do if we are getting condensed values in the nose cone. I guess we can just use the next one up
        looking_for_pressure = False

        for index, row in self.data.iterrows():
            if looking_for_pressure and chamber_pressure < row["Chamber Pressure [psia]"] * 6894.76: # convert to Pa
                # We have found the row we want
                # Eventually, I should probably add an output for the nozzle throat temperature over time. We want to be certain that our graphite won't be damaged by the extreme heat
                # Actually we don't even need the velocity at the throat because we can calculate it from the c-star and the internal pressure
                self.nozzle.throat_velocity = row["Throat Velocity [m/s]"]
                self.nozzle.exit_pressure = row["Exit Pressure [psia]"] * 6894.76
                self.nozzle.isentropic_exponent = row["gamma"]
                self.combustion_chamber.density = row["Chamber Density [kg/m^3]"]
                self.combustion_chamber.temperature = row["Chamber Temperature [K]"]
                self.combustion_chamber.cstar = row["C-star"] # m/s
                
                average_molar_mass = row["Molar Mass [kg/mol]"]
                # The molar mass is in g/mol by default
                self.combustion_chamber.ideal_gas_constant = 8.314 / (average_molar_mass / 1000)
                
                self.combustion_chamber.OF = self.OF

                break
            elif looking_for_pressure:
                # If we are already looking for pressure, we don't need to set it true again
                continue

            if OF < row["O/F Ratio"]:
                # To make sure that we always get a number, I am going to always pick the row that has an O/F ratio immediately above the current value
                looking_for_pressure = True

    

    def simulate_step(self):
        # upstream_pressure = self.ox_tank.pressure
        # downstream_pressure = self.combustion_chamber.pressure
        self.ox_tank.update_drain(self.ox_flow * self.environment.time_increment)
        self.combustion_chamber.update_combustion(self.ox_flow, self.nozzle, self.environment.time_increment)

        # I have no idea how I have made it this far without considering the O/F. The ox-fuel ratio should determine the C-star.
        # Actually, I guess all that I need is the chamber temperature and the average molar mass
        if self.fuel_flow == 0:
            self.OF = 100
        else:
            self.OF = self.ox_flow / self.fuel_flow
        
        self.update_values_from_CEA(self.combustion_chamber.pressure, self.OF)


        nozzle_coefficient = self.nozzle.get_nozzle_coefficient(self.combustion_chamber.pressure, self.environment.get_air_pressure(0))

        # TODO: Account for nozzle loss from the port diameter ratio to the nozzle throat. I still need to read about this some more
        # TODO: I want to reimplement this so that the nozzle is giving mass flow and exit velocity values. I think both ways should work, but that way will be easier to compare, and I am not sure that my nozzle coefficient calculation is correct
        self.thrust = nozzle_coefficient * self.nozzle.throat_area * self.combustion_chamber.pressure


    # region Helper Properties
    @property
    def ox_flow(self):
        # Actually it is probably bad not to cache this; there is a square root call
        return self.injector.get_mass_flow()

    @property
    def fuel_flow(self):
        return self.combustion_chamber.fuel_grain.mass_flow

    @property
    def mass_flow(self):
        return self.ox_flow + self.fuel_flow

    @property
    def specific_impulse(self):
        return self.thrust / self.mass_flow / self.environment.gravitational_acceleration

    # endregion



    

# TODO: Figure out the min mass flow rate, if any, for the nozzle to reach mach one at the choke. I don't see how it could instantaneously reach mach speeds; I think CEA has some outputs for this
