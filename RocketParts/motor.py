# MOTOR CLASS
# Started off as just a place to store the code to get a thrust curve up and running for a rocket class
# Now there is a custom motor that can simulate a hybrid's combustion process


import numpy as np
import pandas as pd

from RocketParts.massObject import MassObject
from Helpers.data import interpolated_lookup, interpolated_lookup_2D, riemann_sum
from environment import Environment

# Imports for defaults
from RocketParts.Motor.oxTank import OxTank
from RocketParts.Motor.injector import Injector
from RocketParts.Motor.combustionChamber import CombustionChamber
from RocketParts.Motor.nozzle import Nozzle
from Logging.logger import MotorLogger



class Motor(MassObject):
    # TODO: rewrite so I can have some variable names that actually make sense. Right now, .total_impulse just gives you a value that is literally not the total impulse
    # TODO: write adjustment for atmospheric pressure

    def __init__(self, **kwargs):
        self.environment = Environment()

        super().__init__(**kwargs)        

        # Mass including the propellant
        self.front = 3 # m
        self.center_of_gravity = 2 # m
        self.mass = 105 # kg
        self.propellant_mass = 105 # kg
        self.thrust_curve = "Data/Input/ThrustCurves/currentGoddard.csv"

        self.thrust_multiplier = 1
        self.time_multiplier = 1
        # If you want to increase the thrust as the environmental pressure decreases
        self.adjust_for_atmospheric = False
        # If you want to adjust for the atmospheric pressure difference, you have to override the nozzle area
        self.nozzle_area = None
        # This doesn't get overriden exactly correctly (If you change the environment calculations, it will be wrong without updating automatically), but I don't think it really matters in any practical applications
        self.assumed_exit_pressure = self.environment.get_air_pressure(0)


        super().overwrite_defaults(**kwargs)

        self.initial_mass = self.mass

        self.set_thrust_data_path(self.thrust_curve)

        self.finished_thrusting = False
        self.thrust = 0
    

    def set_thrust_data_path(self, path):
        self.thrust_curve = path
        dataframe = pd.read_csv(path)
        self.set_thrust_data(dataframe)

    def set_thrust_data(self, dataframe: pd.DataFrame):
        if dataframe.empty:
            raise ValueError("The indicated dataframe has no values.")
        
        if dataframe.iloc[0]["time"] != 0:
            print("Passed motor thrust data has no zero time data point, it is added automatically")
            dataframe.iloc[0]["time"] = 0

        self.thrust_curve = None
        self.thrust_data = dataframe

        self.total_impulse = riemann_sum(self.thrust_data["time"], self.thrust_data["thrust"])
        self.burn_time = self.thrust_data.iloc[-1]["time"]
        self.mass_per_thrust = self.propellant_mass / self.total_impulse


    def calculate_thrust(self, altitude=0):
        if self.finished_thrusting:
            return 0


        # The longer we want the burn time, the more we want to shrink the lookup time
        lookup_time = self.environment.time / self.time_multiplier

        
        try:
            self.thrust = self.thrust_multiplier * interpolated_lookup(self.thrust_data, "time", lookup_time, "thrust")

            new_mass = self.total_mass - self.thrust_to_mass(self.thrust, self.environment.time_increment)
            self.set_mass_constant(new_mass)

            self.thrust += self.get_nozzle_force_difference(altitude)

            return self.thrust

        except IndexError as e:
            print("Finished thrusting")
            self.finished_thrusting = True
            return 0

    def get_nozzle_force_difference(self, altitude):
        if not self.adjust_for_atmospheric:
            return 0

        # We assume that the inputted nozzle was simulated at sea level
        # so the thrust curve data is based on a rocket that had too much exit pressure compared to what it currently has
        environmental_pressure = self.environment.get_air_pressure(altitude)

        # The higher the external pressure you tested at, the more of an increase we will get when the pressure is actually lower
        return self.nozzle_area * (self.assumed_exit_pressure - environmental_pressure)

    def thrust_to_mass(self, thrust, time):
        return thrust * self.mass_per_thrust * time / (self.thrust_multiplier * self.time_multiplier)

    def get_total_impulse(self):
        if self.adjust_for_atmospheric:
            print("WARNING: The total impulse that this returns is not adjusted for the varying atmospheric pressure, but your motor is currently set to adjust for that in an actual simulation")

        # This has got to be the most confusing way possible to do this. There is a total impulse that is the total impulse of the data without multipliers
        return self.time_multiplier * self.thrust_multiplier * self.total_impulse

    def get_average_thrust(self):
        return self.get_total_impulse() / self.get_burn_time()

    def get_burn_time(self):
        return self.time_multiplier * self.burn_time

    def specific_impulse(self):
        return self.get_total_impulse() / (self.initial_mass * 9.81)

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
    # FIXME: scaling the burn time does not work for custom motors
    # TODO: add a simulation for the gas phase

    def __init__(self, **kwargs):
        self.pressurization_time_increment = None
        self.post_pressurization_time_increment = None

        self.finished_thrusting = False

        self._ox_tank = OxTank()
        self.injector = Injector()
        self.combustion_chamber = CombustionChamber()
        self._nozzle = Nozzle()

        self.data_path = "./Data/Input/CEA/CombustionLookup.csv"
        self.update_data()

        self.logger = MotorLogger(self)

        self.cstar_efficiency = 0.85

        super().__init__()

        self.adjust_for_atmospheric = True
        # If you want to adjust for the atmospheric pressure difference, you have to override the nozzle area

        self.overwrite_defaults(**kwargs)

        self.pressurization_time_increment = self.pressurization_time_increment or self.environment.time_increment
        self.post_pressurization_time_increment = self.post_pressurization_time_increment or self.environment.time_increment
        self.environment.time_increment = self.pressurization_time_increment

        self.nozzle_area = self._nozzle.exit_area

        # This is only defined as a cached variable to provide easier graphing
        self.thrust = 0
        self.OF = 0
        self.initial_mass = self.propellant_mass
        self.total_impulse = 0

        self.finished_simulating = False

    @property
    def data_path(self):
        return self._data_path

    @data_path.setter
    def data_path(self, d):
        self._data_path = d
        self.update_data()
    
    def update_data(self):
        self.data = pd.read_csv(self.data_path)

    def update_values_from_CEA(self, chamber_pressure, OF):
        """
        This is doing a look up for the chamber pressure in Pascals.
        It will always round the O/F and pressure up
        """

        target_data = {
            "Throat Velocity [m/s]": 0,
            "Exit Pressure [bar]": 0,
            "gamma": 0,
            "Chamber Density [kg/m^3]": 0,
            "Chamber Temperature [K]": 0,
            "C-star [m/s]": 0,
            "Molar Mass [g/mol]": 0,
        }
        target_keys = target_data.keys()
        target_values = interpolated_lookup_2D(self.data, "Chamber Pressure [bar]", "O/F Ratio", chamber_pressure / 1e5, OF, target_keys, safe=True)
        
        for key, value in zip(target_keys, target_values):
            target_data[key] = value

        self.nozzle.throat_velocity = target_data["Throat Velocity [m/s]"]
        # TODO: add nozzle exit velocity just to check that the methods are the same (they should not be anymore; I added the effect of separation)
        self.nozzle.exit_pressure = target_data["Exit Pressure [bar]"] * 10**5 # Convert from bar to Pa
        self.nozzle.isentropic_exponent = target_data["gamma"]
        self.combustion_chamber.density = target_data["Chamber Density [kg/m^3]"]
        self.combustion_chamber.temperature = target_data["Chamber Temperature [K]"] * np.sqrt(self.cstar_efficiency)
        self.combustion_chamber.cstar = target_data["C-star [m/s]"] * self.cstar_efficiency
        
        average_molar_mass = target_data["Molar Mass [g/mol]"]
        # The molar mass is in g/mol by default, so we convert it to kg/mol
        self.combustion_chamber.ideal_gas_constant = 8.314 / (average_molar_mass / 1000)
        # Eventually, I should probably add an output for the nozzle throat temperature over time. We want to be certain that our graphite won't be damaged by the extreme heat

    
    def calculate_thrust(self, altitude=0):
        self.ox_tank.update_drain(self.ox_flow * self.environment.time_increment)
        self.combustion_chamber.update_combustion(self.ox_flow, self.nozzle, self.environment.time_increment)

        if self.fuel_flow == 0:
            self.OF = 1e10
        else:
            self.OF = self.ox_flow / self.fuel_flow
        
        self.update_values_from_CEA(self.combustion_chamber.pressure, self.OF)

        if not self.adjust_for_atmospheric:
            altitude = 0

        nozzle_coefficient = self.nozzle.get_nozzle_coefficient(self.combustion_chamber.pressure, self.environment.get_air_pressure(altitude))

        # TODO: Account for nozzle loss from the port diameter ratio to the nozzle throat. I still need to read about this some more
        # TODO: I want to reimplement this so that the nozzle is giving mass flow and exit velocity values. I think both ways should work, but that way will be easier to compare, and I am not sure that my nozzle coefficient calculation is correct
        self.thrust = nozzle_coefficient * self.nozzle.throat_area * self.combustion_chamber.pressure * self.thrust_multiplier

        self.total_impulse += self.thrust * self.environment.time_increment

        if not self.combustion_chamber.pressurizing:
            self.environment.time_increment = self.post_pressurization_time_increment

        return self.thrust


    # region Setters
    @property
    def ox_tank(self):
        return self._ox_tank

    @ox_tank.setter
    def ox_tank(self, tank):
        self._ox_tank = tank
        self.initial_mass = self.propellant_mass

    @property
    def fuel_grain(self):
        return self.combustion_chamber.fuel_grain

    @fuel_grain.setter
    def fuel_grain(self, grain):
        self.combustion_chamber.fuel_grain = grain
        self.initial_mass = self.propellant_mass

    @property
    def nozzle(self):
        return self._nozzle

    @nozzle.setter
    def nozzle(self, n):
        self._nozzle = n
        self.nozzle_area = n.exit_area
    # endregion

    # region Helper Properties
    @property
    def propellant_mass(self) -> float:
        return self.ox_tank.ox_mass + self.combustion_chamber.fuel_grain.fuel_mass

    @propellant_mass.setter
    def propellant_mass(self, p):
        print("You cannot set the propellant mass of a custom motor. Set either the ox_mass of the ox_tank or the fuel_mass of the fuel_grain. Continuing anyways because inheritance requires it (e.g. if you are running custom motor, this print statement is expected).")

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
    def mass_flow_out(self):
        return self.combustion_chamber.mass_flow_out

    @property
    def specific_impulse(self):
        return self.thrust / (self.mass_flow_out * 9.81)

    # Whole Simulation Properties
    def check_finished(self):
        if not self.finished_simulating:
            raise Exception("Motor has not finished simulating")

    def get_total_impulse(self):
        self.check_finished()

        return self.total_impulse

    def get_burn_time(self):
        self.check_finished()

        return self.burn_time

    @property
    def total_specific_impulse(self):
        self.check_finished()

        return self.get_total_impulse() / (self.initial_mass * 9.81)

    @property
    def used_specific_impulse(self):
        """Divide by only the mass that has burned away"""
        return self.get_total_impulse() / ((self.initial_mass - self.propellant_mass) * 9.81)

    # A few to evaluate it when there is no logger
    @property
    def average_OF(self):
        # Total mass of oxidizer used divided by the total mass of fuel used
        # TODO: Write a test that this works correctly
        return self.ox_tank.total_mass_used / self.fuel_grain.total_mass_used

    @property
    def average_regression_rate(self):
        return self.fuel_grain.approximate_average_regression_rate(self.get_burn_time())

    def end(self):
        self.finished_simulating = True
        self.burn_time = self.environment.time

    # endregion


