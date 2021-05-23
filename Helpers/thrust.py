"""from Helpers.general import *


# Thrust
# https://www.thrustcurve.org/motors/Hypertek/1685CCRGL-L550/
propellant_mass = 1552 / 1000  # in kg
mass += propellant_mass
thrust_data = pd.read_csv("Data/Input/thrustCurve.csv")
total_thrust = 0  # 3,094.7
# this is close but not exactly correct (actually it's exactly what the data indicates, but not the experimental value) - I changed it to better match the experimental
for index, row in thrust_data.iterrows():
    if index == 0:
        continue

    p_row = thrust_data.iloc[index - 1]
    change_in_time = row["time"] - p_row["time"]
    average_thrust = (row["thrust"] + p_row["thrust"]) / 2
    total_thrust += change_in_time * average_thrust


mass_per_thrust = propellant_mass / total_thrust


finished_thrusting = False


def get_thrust(current_time):
    global finished_thrusting

    if finished_thrusting:
        return 0
    # this isn't very efficient, but there are barely 100 data points so it should be instant
    try:
        previous_thrust = thrust_data[thrust_data["time"] < current_time]

        next_thrust = thrust_data[thrust_data["time"] > current_time]

        previous_thrust = previous_thrust.iloc[-1]
        next_thrust = next_thrust.iloc[0]

        return interpolate(
            current_time, previous_thrust["time"],
            next_thrust["time"],
            previous_thrust["thrust"],
            next_thrust["thrust"])
    except IndexError:
        finished_thrusting = True
        return 0
"""
