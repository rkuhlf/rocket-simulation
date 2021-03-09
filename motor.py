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


        self.thrust_data = pd.read_csv(
            "Data/Input/" + self.thrust_curve + ".csv")


        total_thrust = 0  # 3,094.7
        # this is close but not exactly correct (actually it's exactly what the data indicates, but not the experimental value) - I changed it to better match the experimental
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
            # print("Finished Thrusting", e)
            self.finished_thrusting = True
            return 0

    def thrust_to_mass(self, thrust, time):
        return thrust * self.mass_per_thrust * time
