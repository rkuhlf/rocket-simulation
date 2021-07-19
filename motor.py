import pandas as pd

from Helpers.general import interpolate
from preset_object import PresetObject


class Motor(PresetObject):
    def __init__(self, config={}):
        # https://www.thrustcurve.org/motors/Hypertek/1685CCRGL-L550/
        # Mass including the propellant
        self.mass = 3.898
        self.propellant_mass = 1.552
        self.thrust_curve = "thrustCurve"

        super().overwrite_defaults(config)

        # somehow it thinks there's more thrust mass than there is
        self.thrust_data = pd.read_csv(
            "Data/Input/" + self.thrust_curve + ".csv")


        total_thrust = 0  # 3,094.7
        # this is close but not exactly correct (actually it's exactly what the data indicates, but not the experimental value) - I changed the first point of the base data to better match the experimental
        for index, row in self.thrust_data.iterrows():
            if index == 0:
                continue

            p_row = self.thrust_data.iloc[index - 1]
            change_in_time = row["time"] - p_row["time"]
            average_thrust = (row["thrust"] + p_row["thrust"]) / 2
            total_thrust += change_in_time * average_thrust


        self.mass_per_thrust = self.propellant_mass / total_thrust


        self.finished_thrusting = False


    def get_thrust(self, current_time):
        if self.finished_thrusting:
            return 0
        # this isn't very efficient, but there are barely 100 data points so it should be instant
        try:
            previous_thrust = self.thrust_data[self.thrust_data["time"] <=
                                               current_time]

            next_thrust = self.thrust_data[self.thrust_data["time"] >=
                                           current_time]

            previous_thrust = previous_thrust.iloc[-1]
            next_thrust = next_thrust.iloc[0]

            return interpolate(
                current_time, previous_thrust["time"],
                next_thrust["time"],
                previous_thrust["thrust"],
                next_thrust["thrust"])
        except IndexError as e:
            self.finished_thrusting = True
            return 0

    def thrust_to_mass(self, thrust, time):
        return thrust * self.mass_per_thrust * time


class CustomMotor(Motor):
    # Test with https://www.grc.nasa.gov/www/k-12/rocket/ienzl.html
    # At the moment, everything is being calculated as a constant
    # I'm pretty sure it changes, but I haven't quite realized what gives.
    # Obviously it has something to do with the mass flow rate, since at some points there will be more material going through.
    # However, there doesn't appear to be any wiggle room for that in the equation

    def __init__(self, config={}):
        # Somehow these things are just constant
        self.total_pressure = 10
        self.total_temperature = 100

        self.chamber_area = 0.1  # m
        self.throat_area = 0.01  # m
        self.exit_area = 0.1  # m

        self.specific_heat_ratio = 0.3  # often abbreviated gamma in equations
        self.gas_constant = 8.31446261815324  # per mole, probably not correct
        self.specific_heat_exponent = (
            self.specific_heat_ratio + 1) / (2 * (self.specific_heat_ratio - 1))

        super().overwrite_defaults(config)


    def mass_flow_rate(self, mach):

        ans = self.throat_area * self.total_pressure / \
            (self.total_temperature) ** (1 / 2)

        ans *= (self.specific_heat_ratio / self.gas_constant) ** (1 / 2)

        ans *= ((self.specific_heat_ratio + 1) / 2) ** -self.specific_heat_exponent

        return ans


    def exit_mach(self):
        pass


    def exit_temperature(self):
        ans = 1 / ((1 + (self.specific_heat_ratio - 1) / 2 * self.exit_mach() ** 2))

        return self.total_temperature * ans

    def exit_pressure(self):
        ans = (1 + (self.specific_heat_ratio - 1) / 2 * self.exit_mach **
               2) ** (self.specific_heat_ratio / (self.specific_heat_ratio - 1))

        return self.total_pressure * ans


    def exit_velocity(self, initial_velocity, mach):
        """Assuming flow is choked at the """

        return self.exit_mach() * \
            (self.specific_heat_ratio * self.gas_constant
             * self.exit_temperature()) ** (1 / 2)

    def get_free_stream_pressure(self):
        # A function of pressure, altitude, and mach number
        # just returning a constant atm bc idk
        return 20

    def get_thrust(self):
        # https://www.grc.nasa.gov/WWW/K-12/rocket/rktthsum.html

        return self.get_mass_flow_rate() * self.exit_velocity() + self.exit_area * (self.get_exit_pressure - self.get_free_stream_pressure())
