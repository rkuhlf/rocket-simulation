
import sys
sys.path.append(".")

from preset_object import PresetObject
from Helpers.general import interpolate, binary_solve
import pandas as pd



# You know what, I'm just going to go for a data-oriented design with the whole engine
# Functions for everything. Later, I can have functions for sensitivity analysis
# from preset_object import PresetObject


class Motor(PresetObject):
    def __init__(self, config={}):
        # https://www.thrustcurve.org/motors/Hypertek/1685CCRGL-L550/
        # Mass including the propellant
        self.mass = 3.898
        self.propellant_mass = 1.552
        self.thrust_curve = "thrustCurve"

        self.thrust_multiplier = 1
        self.time_multiplier = 1


        super().overwrite_defaults(config)

        # somehow it thinks there's more thrust mass than there is
        self.thrust_data = pd.read_csv(
            "Data/Input/" + self.thrust_curve + ".csv")


        self.set_thrust_data(self.thrust_data)


        self.finished_thrusting = False


    def set_thrust_data(self, dataframe):
        self.thrust_data = dataframe

        total_thrust = 0  # 3,094.7
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




    def get_thrust(self, current_time):
        if self.finished_thrusting:
            return 0

        # The longer we want the burn time, the more we want to shrink the lookup time
        current_time /= self.time_multiplier
        # this isn't very efficient, but there are barely 100 data points so it should be instant
        try:
            previous_thrust = self.thrust_data[self.thrust_data["time"] <=
                                               current_time]

            next_thrust = self.thrust_data[self.thrust_data["time"] >=
                                           current_time]

            previous_thrust = previous_thrust.iloc[-1]
            next_thrust = next_thrust.iloc[0]

            return self.thrust_multiplier * interpolate(
                current_time, previous_thrust["time"],
                next_thrust["time"],
                previous_thrust["thrust"],
                next_thrust["thrust"])
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

    def scale_thrust(self, multiplier):
        self.thrust_multiplier *= multiplier

    def reset_thrust_scale(self):
        self.thrust_multiplier = 1

    def scale_time(self, multiplier):
        self.time_multiplier *= multiplier

    def reset_time_scale(self):
        self.time_multiplier = 1

class CustomMotor(Motor):
    def __init__(self, config={}, ox_tank=None, injector=None, combustion_chamber=None, nozzle=None, environment=None):
        # Don't really need to do anything from super in init
        self.thrust_multiplier = 1
        self.time_multiplier = 1
        self.finished_thrusting = False

        self.ox_tank = ox_tank
        self.injector = injector
        self.combustion_chamber = combustion_chamber
        self.nozzle = nozzle
        self.environment = environment

        super().overwrite_defaults(config)

        # Look, here is where I really want to have all of the mass calculations done separately
        # TODO: I could have a mass object class that all of the objects in the rocket with mass inherit from, then I have it define a get mass and a get_position function, then it uses its own state to calculate each
        self.mass = ox_tank.mass + injector.mass + combustion_chamber.mass + nozzle.mass

    def simulate_step(self):
        upstream_pressure = self.ox_tank.pressure
        downstream_pressure = self.combustion_chamber.pressure
        ox_flow = self.injector.get_mass_flow(downstream_pressure, upstream_pressure)

        self.ox_tank.update_drain(ox_flow * self.environment.time_increment)
        self.combustion_chamber.update_combustion(ox_flow)

        fuel_flow = self.combustion_chamber.grain.mass_flow

        nozzle_coefficient = self.nozzle.get_nozzle_coefficient(self.ox_tank.pressure, ox_flow / fuel_flow, self.environment.get_air_pressure(0))

        # TODO: Account for nozzle loss from the port diameter ratio to the nozzle throat. I still need to read about this some more
        self.thrust = nozzle_coefficient * self.nozzle.throat_area * self.combustion_chamber.pressure




        


# TODO: Figure out the min mass flow rate, if any, for the nozzle to reach mach one at the choke. I don't see how it could instantaneously reach mach speeds
if __name__ == "__main__":
    # some motor tests that should be moved to the actual tests TODO
    # m = CustomMotor()
    # m.exit_mach()
    # print(m.get_thrust())

    m = Motor()
    # print(m.get_burn_time())
